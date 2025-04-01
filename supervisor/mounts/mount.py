"""Network mounts in supervisor."""

from abc import ABC, abstractmethod
import asyncio
from functools import cached_property
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
    DBUS_ATTR_ACTIVE_STATE,
    DBUS_ATTR_DESCRIPTION,
    DBUS_ATTR_OPTIONS,
    DBUS_ATTR_TYPE,
    DBUS_ATTR_WHAT,
    DBUS_IFACE_SYSTEMD_UNIT,
    StartUnitMode,
    StopUnitMode,
    UnitActiveState,
)
from ..dbus.systemd import SystemdUnit
from ..docker.const import PATH_MEDIA, PATH_SHARE
from ..exceptions import (
    DBusError,
    DBusSystemdNoSuchUnit,
    MountActivationError,
    MountError,
    MountInvalidError,
)
from ..resolution.const import ContextType, IssueType
from ..resolution.data import Issue
from ..utils.sentry import async_capture_exception
from .const import (
    ATTR_PATH,
    ATTR_READ_ONLY,
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
        self._failed_issue = Issue(
            IssueType.MOUNT_FAILED, ContextType.MOUNT, reference=self.name
        )

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
        return MountData(
            name=self.name, type=self.type, usage=self.usage, read_only=self.read_only
        )

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
    def read_only(self) -> bool:
        """Is mount read-only."""
        return self._data.get(ATTR_READ_ONLY, False)

    @property
    @abstractmethod
    def what(self) -> str:
        """What to mount."""

    @property
    @abstractmethod
    def where(self) -> PurePath:
        """Where to mount (on host)."""

    @property
    def options(self) -> list[str]:
        """List of options to use to mount."""
        return ["ro"] if self.read_only else []

    @property
    def description(self) -> str:
        """Description of mount."""
        return f"Supervisor {self.type} mount: {self.name}"

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

    @cached_property
    def local_where(self) -> Path:
        """Return where this is mounted within supervisor container."""
        return self.sys_config.extern_to_local_path(self.where)

    @property
    def container_where(self) -> PurePath | None:
        """Return where this is made available in managed containers (core, addons, etc.).

        This returns none if it is not made available in managed containers.
        """
        match self.usage:
            case MountUsage.MEDIA:
                return PurePath(PATH_MEDIA, self.name)
            case MountUsage.SHARE:
                return PurePath(PATH_SHARE, self.name)
        return None

    @property
    def failed_issue(self) -> Issue:
        """Get issue used if this mount has failed."""
        return self._failed_issue

    async def is_mounted(self) -> bool:
        """Return true if successfully mounted and available."""
        return self.state == UnitActiveState.ACTIVE

    def __eq__(self, other):
        """Return true if mounts are the same."""
        return isinstance(other, Mount) and self.name == other.name

    async def load(self) -> None:
        """Initialize object."""
        # If there's no mount unit, mount it to make one
        if not await self._update_unit():
            await self.mount()
            return

        await self._update_state_await(not_state=UnitActiveState.ACTIVATING)

        # If mount is not available, try to reload it
        if not await self.is_mounted():
            await self.reload()

    async def _update_state(self) -> UnitActiveState | None:
        """Update mount unit state."""
        try:
            self._state = await self.unit.get_active_state()
        except DBusError as err:
            await async_capture_exception(err)
            raise MountError(
                f"Could not get active state of mount due to: {err!s}"
            ) from err

    async def _update_unit(self) -> SystemdUnit | None:
        """Get systemd unit from dbus."""
        try:
            self._unit = await self.sys_dbus.systemd.get_unit(self.unit_name)
        except DBusSystemdNoSuchUnit:
            self._unit = None
            self._state = None
        except DBusError as err:
            await async_capture_exception(err)
            raise MountError(f"Could not get mount unit due to: {err!s}") from err
        return self.unit

    async def update(self) -> bool:
        """Update info about mount from dbus. Return true if it is mounted and available."""
        if not await self._update_unit():
            return False

        await self._update_state()

        # If active, dismiss corresponding failed mount issue if found
        if (
            mounted := await self.is_mounted()
        ) and self.failed_issue in self.sys_resolution.issues:
            self.sys_resolution.dismiss_issue(self.failed_issue)

        return mounted

    async def _update_state_await(
        self,
        expected_states: list[UnitActiveState] | None = None,
        not_state: UnitActiveState = UnitActiveState.ACTIVATING,
    ) -> None:
        """Update state info about mount from dbus. Wait for one of expected_states to appear or state to change from not_state."""
        if not self.unit:
            return

        try:
            async with asyncio.timeout(30), self.unit.properties_changed() as signal:
                await self._update_state()
                while (
                    expected_states
                    and self.state not in expected_states
                    or not expected_states
                    and self.state == not_state
                ):
                    prop_change_signal = await signal.wait_for_signal()
                    if (
                        prop_change_signal[0] == DBUS_IFACE_SYSTEMD_UNIT
                        and DBUS_ATTR_ACTIVE_STATE in prop_change_signal[1]
                    ):
                        self._state = prop_change_signal[1][
                            DBUS_ATTR_ACTIVE_STATE
                        ].value

        except TimeoutError:
            _LOGGER.warning(
                "Mount %s still in state %s after waiting for 30 seconds to complete",
                self.name,
                str(self.state).lower(),
            )

    async def mount(self) -> None:
        """Mount using systemd."""

        def ensure_empty_folder() -> None:
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

        await self.sys_run_in_executor(ensure_empty_folder)

        try:
            options = (
                [(DBUS_ATTR_OPTIONS, Variant("s", ",".join(self.options)))]
                if self.options
                else []
            )
            if self.type != MountType.BIND:
                options += [(DBUS_ATTR_TYPE, Variant("s", self.type))]

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

        if await self._update_unit():
            await self._update_state_await(not_state=UnitActiveState.ACTIVATING)

        if not await self.is_mounted():
            raise MountActivationError(
                f"Mounting {self.name} did not succeed. Check host logs for errors from mount or systemd unit {self.unit_name} for details.",
                _LOGGER.error,
            )

    async def unmount(self) -> None:
        """Unmount using systemd."""
        if not await self._update_unit():
            _LOGGER.info("Mount %s is not mounted, skipping unmount", self.name)
            return

        await self._update_state()
        try:
            if self.state != UnitActiveState.FAILED:
                await self.sys_dbus.systemd.stop_unit(self.unit_name, StopUnitMode.FAIL)

            await self._update_state_await(
                [UnitActiveState.INACTIVE, UnitActiveState.FAILED]
            )

            if self.state == UnitActiveState.FAILED:
                await self.sys_dbus.systemd.reset_failed_unit(self.unit_name)
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
        except DBusError as err:
            raise MountError(
                f"Could not reload mount {self.name} due to: {err!s}", _LOGGER.error
            ) from err
        else:
            if await self._update_unit():
                await self._update_state_await(not_state=UnitActiveState.ACTIVATING)

            if not await self.is_mounted():
                raise MountActivationError(
                    f"Reloading {self.name} did not succeed. Check host logs for errors from mount or systemd unit {self.unit_name} for details.",
                    _LOGGER.error,
                )

        # If it is mounted now, dismiss corresponding issue if present
        if self.failed_issue in self.sys_resolution.issues:
            self.sys_resolution.dismiss_issue(self.failed_issue)


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
        options = super().options
        if self.port:
            options.append(f"port={self.port}")
        return options

    async def is_mounted(self) -> bool:
        """Return true if successfully mounted and available."""
        return self.state == UnitActiveState.ACTIVE and await self.sys_run_in_executor(
            self.local_where.is_mount
        )


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
        options = super().options + ["noserverino"]
        if self.version:
            options.append(f"vers={self.version}")

        if self.username and self.password:
            options.append(f"credentials={self.path_extern_credentials.as_posix()}")
        else:
            options.append("guest")

        return options

    @property
    def path_credentials(self) -> Path:
        """Path to credentials file."""
        return self.sys_config.path_mounts_credentials / self.name

    @property
    def path_extern_credentials(self) -> PurePath:
        """Path to credentials file external to Docker."""
        return self.sys_config.path_extern_mounts_credentials / self.name

    async def mount(self) -> None:
        """Mount using systemd."""
        if self.username and self.password:

            def write_credentials() -> None:
                if not self.path_credentials.exists():
                    self.path_credentials.touch(mode=0o600)

                with self.path_credentials.open(mode="w") as cred_file:
                    cred_file.write(
                        f"username={self.username}\npassword={self.password}"
                    )

            await self.sys_run_in_executor(write_credentials)

        await super().mount()

    async def unmount(self) -> None:
        """Unmount using systemd."""
        await self.sys_run_in_executor(self.path_credentials.unlink, missing_ok=True)
        await super().unmount()


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
        if where and not where.is_relative_to(coresys.config.path_extern_supervisor):
            raise ValueError("Path must be within Supervisor's host data directory!")

        super().__init__(coresys, data)
        self._where = where

    @staticmethod
    def create(
        coresys: CoreSys,
        name: str,
        path: Path,
        usage: MountUsage | None = None,
        where: PurePath | None = None,
        read_only: bool = False,
    ) -> "BindMount":
        """Create a new bind mount instance."""
        return BindMount(
            coresys,
            MountData(
                name=name,
                type=MountType.BIND,
                path=path.as_posix(),
                usage=usage and usage,
                read_only=read_only,
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
        return super().options + ["bind"]
