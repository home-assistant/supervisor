"""Network mounts in supervisor."""

from abc import ABC, abstractmethod
import asyncio
import logging
from pathlib import Path, PurePath

from dbus_fast import Variant
from voluptuous import Coerce

from ..const import (
    ATTR_NAME,
    ATTR_PASSWORD,
    ATTR_PORT,
    ATTR_TYPE,
    ATTR_USERNAME,
    ATTR_VERSION,
)
from ..coresys import CoreSys, CoreSysAttributes
from ..dbus.const import (
    DBUS_ATTR_DESCRIPTION,
    DBUS_ATTR_OPTIONS,
    DBUS_ATTR_TYPE,
    DBUS_ATTR_WHAT,
    StartUnitMode,
    StopUnitMode,
    UnitActiveState,
)
from ..dbus.systemd import SystemdUnit
from ..exceptions import (
    DBusError,
    DBusSystemdNoSuchUnit,
    MountActivationError,
    MountError,
    MountInvalidError,
)
from ..resolution.const import ContextType, IssueType
from ..resolution.data import Issue
from ..utils.sentry import capture_exception
from .const import (
    ATTR_PATH,
    ATTR_SERVER,
    ATTR_SHARE,
    ATTR_USAGE,
    MountCifsVersion,
    MountType,
    MountUsage,
)
from .validate import MountData

_LOGGER: logging.Logger = logging.getLogger(__name__)

COERCE_MOUNT_TYPE = Coerce(MountType)
COERCE_MOUNT_USAGE = Coerce(MountUsage)


class Mount(CoreSysAttributes, ABC):
    """A mount."""

    def __init__(self, coresys: CoreSys, data: MountData) -> None:
        """Initialize object."""
        super().__init__()

        self.coresys: CoreSys = coresys
        self._data: MountData = data
        self._unit: SystemdUnit | None = None
        self._state: UnitActiveState | None = None

    @classmethod
    def from_dict(cls, coresys: CoreSys, data: MountData) -> "Mount":
        """Make dictionary into mount object."""
        if cls not in [Mount, NetworkMount]:
            return cls(coresys, data)

        type_ = COERCE_MOUNT_TYPE(data[ATTR_TYPE])
        if type_ == MountType.CIFS:
            return CIFSMount(coresys, data)
        if type_ == MountType.NFS:
            return NFSMount(coresys, data)
        return BindMount(coresys, data)

    def to_dict(self, *, skip_secrets: bool = True) -> MountData:
        """Return dictionary representation."""
        return MountData(name=self.name, type=self.type.value, usage=self.usage.value)

    @property
    def name(self) -> str:
        """Get name."""
        return self._data[ATTR_NAME]

    @property
    def type(self) -> MountType:
        """Get mount type."""
        return COERCE_MOUNT_TYPE(self._data[ATTR_TYPE])

    @property
    def usage(self) -> MountUsage | None:
        """Get mount usage."""
        return (
            COERCE_MOUNT_USAGE(self._data[ATTR_USAGE])
            if ATTR_USAGE in self._data
            else None
        )

    @property
    @abstractmethod
    def what(self) -> str:
        """What to mount."""

    @property
    @abstractmethod
    def where(self) -> PurePath:
        """Where to mount (on host)."""

    @property
    @abstractmethod
    def options(self) -> list[str]:
        """List of options to use to mount."""

    @property
    def description(self) -> str:
        """Description of mount."""
        return f"Supervisor {self.type.value} mount: {self.name}"

    @property
    def unit_name(self) -> str:
        """Systemd unit name for mount."""
        return f"{self.where.as_posix()[1:].replace('/', '-')}.mount"

    @property
    def unit(self) -> SystemdUnit | None:
        """Get Systemd unit object for mount."""
        return self._unit

    @property
    def state(self) -> UnitActiveState | None:
        """Get state of mount."""
        return self._state

    @property
    def local_where(self) -> Path | None:
        """Return where this is mounted within supervisor container.

        This returns none if 'where' is not within supervisor's host data directory.
        """
        return (
            self.sys_config.extern_to_local_path(self.where)
            if self.where.is_relative_to(self.sys_config.path_extern_supervisor)
            else None
        )

    @property
    def failed_issue(self) -> Issue:
        """Get issue used if this mount has failed."""
        return Issue(IssueType.MOUNT_FAILED, ContextType.MOUNT, reference=self.name)

    def __eq__(self, other):
        """Return true if mounts are the same."""
        return isinstance(other, Mount) and self.name == other.name

    async def load(self) -> None:
        """Initialize object."""
        await self._update_await_activating()

        # If there's no mount unit, mount it to make one
        if not self.unit:
            await self.mount()

        # At this point any state besides active is treated as a failed mount, try to reload it
        elif self.state != UnitActiveState.ACTIVE:
            await self.reload()

    async def update(self) -> None:
        """Update info about mount from dbus."""
        try:
            self._unit = await self.sys_dbus.systemd.get_unit(self.unit_name)
        except DBusSystemdNoSuchUnit:
            self._unit = None
            self._state = None
            return
        except DBusError as err:
            capture_exception(err)
            raise MountError(f"Could not get mount unit due to: {err!s}") from err

        try:
            self._state = await self.unit.get_active_state()
        except DBusError as err:
            capture_exception(err)
            raise MountError(
                f"Could not get active state of mount due to: {err!s}"
            ) from err

        # If active, dismiss corresponding failed mount issue if found
        if (
            self.state == UnitActiveState.ACTIVE
            and self.failed_issue in self.sys_resolution.issues
        ):
            self.sys_resolution.dismiss_issue(self.failed_issue)

    async def _update_await_activating(self):
        """Update info about mount from dbus. If 'activating' wait up to 30 seconds."""
        await self.update()

        # If we're still activating, give it up to 30 seconds to finish
        if self.state == UnitActiveState.ACTIVATING:
            _LOGGER.info(
                "Mount %s still activating, waiting up to 30 seconds to complete",
                self.name,
            )
            for _ in range(3):
                await asyncio.sleep(10)
                await self.update()
                if self.state != UnitActiveState.ACTIVATING:
                    break

    async def mount(self) -> None:
        """Mount using systemd."""
        # If supervisor can see where it will mount, ensure there's an empty folder there
        if self.local_where:
            if not self.local_where.exists():
                _LOGGER.info(
                    "Creating folder for mount: %s", self.local_where.as_posix()
                )
                self.local_where.mkdir(parents=True)
            elif not self.local_where.is_dir():
                raise MountInvalidError(
                    f"Cannot mount {self.name} at {self.local_where.as_posix()} as it is not a directory",
                    _LOGGER.error,
                )
            elif any(self.local_where.iterdir()):
                raise MountInvalidError(
                    f"Cannot mount {self.name} at {self.local_where.as_posix()} because it is not empty",
                    _LOGGER.error,
                )

        try:
            options = (
                [(DBUS_ATTR_OPTIONS, Variant("s", ",".join(self.options)))]
                if self.options
                else []
            )
            if self.type != MountType.BIND:
                options += [(DBUS_ATTR_TYPE, Variant("s", self.type.value))]

            await self.sys_dbus.systemd.start_transient_unit(
                self.unit_name,
                StartUnitMode.FAIL,
                options
                + [
                    (DBUS_ATTR_DESCRIPTION, Variant("s", self.description)),
                    (DBUS_ATTR_WHAT, Variant("s", self.what)),
                ],
            )
        except DBusError as err:
            raise MountError(
                f"Could not mount {self.name} due to: {err!s}", _LOGGER.error
            ) from err

        await self._update_await_activating()

        if self.state != UnitActiveState.ACTIVE:
            raise MountActivationError(
                f"Mounting {self.name} did not succeed. Check host logs for errors from mount or systemd unit {self.unit_name} for details.",
                _LOGGER.error,
            )

    async def unmount(self) -> None:
        """Unmount using systemd."""
        await self.update()

        try:
            if self.state == UnitActiveState.FAILED:
                await self.sys_dbus.systemd.reset_failed_unit(self.unit_name)
            else:
                await self.sys_dbus.systemd.stop_unit(self.unit_name, StopUnitMode.FAIL)
        except DBusSystemdNoSuchUnit:
            _LOGGER.info("Mount %s is not mounted, skipping unmount", self.name)
        except DBusError as err:
            raise MountError(
                f"Could not unmount {self.name} due to: {err!s}", _LOGGER.error
            ) from err

        self._unit = None
        self._state = None

    async def reload(self) -> None:
        """Reload or restart mount unit to re-mount."""
        try:
            await self.sys_dbus.systemd.reload_unit(self.unit_name, StartUnitMode.FAIL)
        except DBusSystemdNoSuchUnit:
            _LOGGER.info(
                "Mount %s is not mounted, mounting instead of reloading", self.name
            )
            await self.mount()
            return
        except DBusError as err:
            raise MountError(
                f"Could not reload mount {self.name} due to: {err!s}", _LOGGER.error
            ) from err

        await self._update_await_activating()

        if self.state != UnitActiveState.ACTIVE:
            raise MountActivationError(
                f"Reloading {self.name} did not succeed. Check host logs for errors from mount or systemd unit {self.unit_name} for details.",
                _LOGGER.error,
            )


class NetworkMount(Mount, ABC):
    """A network mount."""

    def to_dict(self, *, skip_secrets: bool = True) -> MountData:
        """Return dictionary representation."""
        out = MountData(server=self.server, **super().to_dict())
        if self.port is not None:
            out[ATTR_PORT] = self.port
        return out

    @property
    def server(self) -> str:
        """Get server."""
        return self._data[ATTR_SERVER]

    @property
    def port(self) -> int | None:
        """Get port, returns none if using the protocol default."""
        return self._data.get(ATTR_PORT)

    @property
    def where(self) -> PurePath:
        """Where to mount."""
        return self.sys_config.path_extern_mounts / self.name

    @property
    def options(self) -> list[str]:
        """Options to use to mount."""
        return [f"port={self.port}"] if self.port else []


class CIFSMount(NetworkMount):
    """A CIFS type mount."""

    def to_dict(self, *, skip_secrets: bool = True) -> MountData:
        """Return dictionary representation."""
        out = MountData(share=self.share, **super().to_dict())
        if not skip_secrets and self.username is not None:
            out[ATTR_USERNAME] = self.username
            out[ATTR_PASSWORD] = self.password
        out[ATTR_VERSION] = self.version
        return out

    @property
    def share(self) -> str:
        """Get share."""
        return self._data[ATTR_SHARE]

    @property
    def username(self) -> str | None:
        """Get username, returns none if auth is not used."""
        return self._data.get(ATTR_USERNAME)

    @property
    def password(self) -> str | None:
        """Get password, returns none if auth is not used."""
        return self._data.get(ATTR_PASSWORD)

    @property
    def version(self) -> str | None:
        """Get password, returns none if auth is not used."""
        version = self._data.get(ATTR_VERSION)
        if version == MountCifsVersion.LEGACY_1_0:
            return "1.0"
        if version == MountCifsVersion.LEGACY_2_0:
            return "2.0"
        return None

    @property
    def what(self) -> str:
        """What to mount."""
        return f"//{self.server}/{self.share}"

    @property
    def options(self) -> list[str]:
        """Options to use to mount."""
        options = super().options
        if self.version:
            options.append(f"vers={self.version}")

        if self.username and self.password:
            options.extend([f"username={self.username}", f"password={self.password}"])
        else:
            options.append("guest")

        return options


class NFSMount(NetworkMount):
    """An NFS type mount."""

    def to_dict(self, *, skip_secrets: bool = True) -> MountData:
        """Return dictionary representation."""
        return MountData(path=self.path.as_posix(), **super().to_dict())

    @property
    def path(self) -> PurePath:
        """Get path."""
        return PurePath(self._data[ATTR_PATH])

    @property
    def what(self) -> str:
        """What to mount."""
        return f"{self.server}:{self.path.as_posix()}"

    @property
    def options(self) -> list[str]:
        """Options to use to mount."""
        return super().options + ["soft", "timeo=200"]


class BindMount(Mount):
    """A bind type mount."""

    def __init__(
        self, coresys: CoreSys, data: MountData, *, where: PurePath | None = None
    ) -> None:
        """Initialize object."""
        super().__init__(coresys, data)
        self._where = where

    @staticmethod
    def create(
        coresys: CoreSys,
        name: str,
        path: Path,
        usage: MountUsage | None = None,
        where: PurePath | None = None,
    ) -> "BindMount":
        """Create a new bind mount instance."""
        return BindMount(
            coresys,
            MountData(
                name=name,
                type=MountType.BIND.value,
                path=path.as_posix(),
                usage=usage and usage.value,
            ),
            where=where,
        )

    def to_dict(self, *, skip_secrets: bool = True) -> MountData:
        """Return dictionary representation."""
        return MountData(path=self.path.as_posix(), **super().to_dict())

    @property
    def path(self) -> PurePath:
        """Get path."""
        return PurePath(self._data[ATTR_PATH])

    @property
    def what(self) -> str:
        """What to mount."""
        return self.path.as_posix()

    @property
    def where(self) -> PurePath:
        """Where to mount."""
        return (
            self._where
            if self._where
            else self.sys_config.path_extern_mounts / self.name
        )

    @property
    def options(self) -> list[str]:
        """List of options to use to mount."""
        return ["bind"]
