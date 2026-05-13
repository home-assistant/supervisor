"""Network mounts in supervisor."""

from abc import ABC, abstractmethod
import asyncio
from collections.abc import Awaitable, Callable
from functools import cached_property
import logging
import os
from pathlib import Path, PurePath
import time

from dbus_fast import Variant
from voluptuous import Coerce

from ..coresys import CoreSys, CoreSysAttributes
from ..dbus.const import (
    DBUS_ATTR_DESCRIPTION,
    DBUS_ATTR_OPTIONS,
    DBUS_ATTR_TIMEOUT_USEC,
    DBUS_ATTR_TYPE,
    DBUS_ATTR_WHAT,
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
from .const import MountCifsVersion, MountType, MountUsage
from .validate import MountData

_LOGGER: logging.Logger = logging.getLogger(__name__)


def _probe_network_mount(path: Path) -> bool:
    """Verify `path` is a live mount on a reachable server.

    Run inside an executor — both syscalls share one thread and
    benefit from the kernel's warm session state on a real mount.

    Raises OSError (typically ETIMEDOUT / EHOSTDOWN / ECONNABORTED)
    when the server is unreachable. Returns False when statvfs
    succeeded but the path is not actually a mount point (the
    "ghost mount" case where statvfs returns the underlying root
    filesystem's stats). Returns True only when statvfs forced an
    RPC that the server answered AND the path actually crosses a
    filesystem boundary.
    """
    os.statvfs(path)
    return path.stat().st_dev != path.parent.stat().st_dev


# Three layered timeouts cooperate to keep the host alive when an NFS server
# becomes unreachable while a `.mount` unit is being reloaded (see #6827):
#
#   NFS RPC timeout (timeo=100,retrans=2) ~30 s
#     < systemd unit TimeoutSec (MOUNT_UNIT_TIMEOUT_USEC)  35 s
#     < supervisor state-await (UPDATE_STATE_TIMEOUT)      40 s
#
# Ordering is what matters. The kernel RPC layer fails first so the mount
# helper can exit; systemd then SIGTERMs anything that didn't and moves the
# unit to `failed` before supervisor abandons its observation. Any later
# restart then runs from `failed` (no in-flight helper, no pinned kernel
# task) — the safe path.
MOUNT_UNIT_TIMEOUT_USEC = 35 * 1_000_000
UPDATE_STATE_TIMEOUT = 40

COERCE_MOUNT_TYPE: Callable[[str], MountType] = Coerce(MountType)
COERCE_MOUNT_USAGE: Callable[[str], MountUsage] = Coerce(MountUsage)


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
    def from_dict(cls, coresys: CoreSys, data: MountData) -> Mount:
        """Make dictionary into mount object."""
        if cls not in [Mount, NetworkMount]:
            return cls(coresys, data)

        type_ = COERCE_MOUNT_TYPE(data["type"])
        if type_ == MountType.CIFS:
            return CIFSMount(coresys, data)
        if type_ == MountType.NFS:
            return NFSMount(coresys, data)
        return BindMount(coresys, data)

    def to_dict(self, *, skip_secrets: bool = True) -> MountData:
        """Return dictionary representation."""
        return MountData(
            name=self.name,
            type=self.type,
            usage=self.usage and self.usage.value,
            read_only=self.read_only,
        )

    @property
    def name(self) -> str:
        """Get name."""
        return self._data["name"]

    @property
    def type(self) -> MountType:
        """Get mount type."""
        return COERCE_MOUNT_TYPE(self._data["type"])

    @property
    def usage(self) -> MountUsage | None:
        """Get mount usage."""
        if self._data["usage"] is None:
            return None
        return COERCE_MOUNT_USAGE(self._data["usage"])

    @property
    def read_only(self) -> bool:
        """Is mount read-only."""
        return self._data.get("read_only", False)

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
        return UnitActiveState(self._state) if self._state is not None else None

    @cached_property
    def local_where(self) -> Path:
        """Return where this is mounted within supervisor container."""
        return self.sys_config.extern_to_local_path(self.where)

    @property
    def container_where(self) -> PurePath | None:
        """Return where this is made available in managed containers (core, apps, etc.).

        This returns none if it is not made available in managed containers.
        """
        match self.usage:
            case MountUsage.MEDIA:
                return PurePath(PATH_MEDIA, self.name)
            case MountUsage.SHARE:
                return PurePath(PATH_SHARE, self.name)
            case MountUsage.BACKUP | None:
                return None

    @property
    def failed_issue(self) -> Issue:
        """Get issue used if this mount has failed."""
        return self._failed_issue

    async def is_mounted(self) -> bool:
        """Return true if successfully mounted and available."""
        return self.state == UnitActiveState.ACTIVE

    def __eq__(self, other: object) -> bool:
        """Return true if mounts are the same."""
        return isinstance(other, Mount) and self.name == other.name

    def __hash__(self) -> int:
        """Return hash of mount."""
        return hash(self.name)

    async def load(self) -> None:
        """Initialize object."""
        # If there's no mount unit, mount it to make one
        if not (unit := await self._update_unit()):
            await self.mount()
            return

        await self._update_state_await(unit)

        # If mount is not available, try to reload it
        if not await self.is_mounted():
            await self.reload()

    async def _update_state(self, unit: SystemdUnit) -> None:
        """Update mount unit state."""
        try:
            self._state = await unit.get_active_state()
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
        if not (unit := await self._update_unit()):
            return False

        await self._update_state(unit)

        if not await self.is_mounted():
            return False

        if issue := self.sys_resolution.get_issue_if_present(self.failed_issue):
            self.sys_resolution.dismiss_issue(issue)
        return True

    async def _update_state_await(
        self,
        unit: SystemdUnit,
        expected_states: set[UnitActiveState] | None = None,
    ) -> None:
        """Update state info about mount from dbus. Wait for one of expected_states to appear.

        Used for the initial `load()` observation where no systemd job is
        in flight — we're just polling for the unit to settle out of any
        transitional state. Job-dispatching paths (mount/unmount/reload/
        restart) instead subscribe to JobRemoved before dispatching and
        wait for that signal — see `_run_systemd_job`.
        """
        if expected_states is None:
            expected_states = {
                UnitActiveState.ACTIVE,
                UnitActiveState.FAILED,
                UnitActiveState.INACTIVE,
            }
        try:
            async with asyncio.timeout(UPDATE_STATE_TIMEOUT):
                self._state = await unit.wait_for_active_state(expected_states)
        except TimeoutError:
            await self._update_state(unit)
            _LOGGER.warning(
                "Mount %s still in state %s after waiting for %d seconds to complete",
                self.name,
                str(self.state).lower(),
                UPDATE_STATE_TIMEOUT,
            )

    async def _run_systemd_job(
        self,
        op_name: str,
        dispatch: Awaitable[str],
    ) -> str | None:
        """Dispatch a systemd job and wait for its JobRemoved signal.

        Subscribing before dispatching closes the race where a fast job
        could complete (and emit JobRemoved) before we set up the signal
        match. The returned result string is the systemd job outcome
        ("done", "failed", "canceled", "timeout", "dependency", "skipped").

        Returns None on timeout — callers should re-read state to decide
        what to do next.
        """
        async with self.sys_dbus.systemd.job_removed() as jobs:
            job_path = await dispatch
            try:
                async with asyncio.timeout(UPDATE_STATE_TIMEOUT):
                    result = await jobs.wait_for_job(job_path)
            except TimeoutError:
                _LOGGER.warning(
                    "Systemd %s job for mount %s did not complete within %d seconds",
                    op_name,
                    self.name,
                    UPDATE_STATE_TIMEOUT,
                )
                return None
        _LOGGER.debug(
            "Systemd %s job for mount %s completed: %s", op_name, self.name, result
        )
        return result

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

        options = (
            [(DBUS_ATTR_OPTIONS, Variant("s", ",".join(self.options)))]
            if self.options
            else []
        )
        if self.type != MountType.BIND:
            options += [(DBUS_ATTR_TYPE, Variant("s", self.type))]
        properties = options + [
            (DBUS_ATTR_DESCRIPTION, Variant("s", self.description)),
            (DBUS_ATTR_WHAT, Variant("s", self.what)),
            (DBUS_ATTR_TIMEOUT_USEC, Variant("t", MOUNT_UNIT_TIMEOUT_USEC)),
        ]

        try:
            await self._run_systemd_job(
                "start_transient_unit",
                self.sys_dbus.systemd.start_transient_unit(
                    self.unit_name, StartUnitMode.FAIL, properties
                ),
            )
        except DBusError as err:
            raise MountError(
                f"Could not mount {self.name} due to: {err!s}", _LOGGER.error
            ) from err

        if unit := await self._update_unit():
            await self._update_state(unit)

        if not await self.is_mounted():
            raise MountActivationError(
                f"Mounting {self.name} did not succeed. Check host logs for errors from mount or systemd unit {self.unit_name} for details.",
                _LOGGER.error,
            )

    async def unmount(self) -> None:
        """Unmount using systemd."""
        if not (unit := await self._update_unit()):
            _LOGGER.info("Mount %s is not mounted, skipping unmount", self.name)
            return

        await self._update_state(unit)
        try:
            if self.state != UnitActiveState.FAILED:
                await self._run_systemd_job(
                    "stop_unit",
                    self.sys_dbus.systemd.stop_unit(self.unit_name, StopUnitMode.FAIL),
                )
                await self._update_state(unit)

            if self.state == UnitActiveState.FAILED:
                await self.sys_dbus.systemd.reset_failed_unit(self.unit_name)
        except DBusError as err:
            raise MountError(
                f"Could not unmount {self.name} due to: {err!s}", _LOGGER.error
            ) from err

        self._unit = None
        self._state = None

    async def reload(self) -> None:
        """Verify the mount is reachable; reload/restart as needed.

        `is_mounted()` is the source of truth here: for network mounts it
        runs a statvfs probe that forces an RPC, so a passing return value
        proves the share is live right now — systemd's "active/mounted"
        state alone does not (CIFS reload is local-only — smb3_reconfigure
        never contacts the server). The reload → restart escalation only
        runs when the probe fails.
        """
        if await self.is_mounted():
            self._dismiss_failed_issue()
            return

        try:
            await self._run_systemd_job(
                "reload_or_restart_unit",
                self.sys_dbus.systemd.reload_unit(self.unit_name, StartUnitMode.FAIL),
            )
        except DBusSystemdNoSuchUnit:
            _LOGGER.info(
                "Mount %s is not mounted, mounting instead of reloading", self.name
            )
            await self.mount()
            return
        except DBusError as err:
            _LOGGER.error(
                "Could not reload mount %s due to: %s. Trying a restart", self.name, err
            )
            await self._restart()
            self._dismiss_failed_issue()
            return

        if unit := await self._update_unit():
            await self._update_state(unit)

        # Safety net for #6827: with the layered timeouts above
        # (RPC < TimeoutSec < state-await) the unit should always have
        # left RELOADING by the time we get here. If it has not, the
        # systemd-side cleanup did not complete in time; escalating to
        # RestartUnit while a mount/umount helper is still pinned in the
        # kernel is the destructive pattern that wedges PID 1, so refuse
        # to escalate and surface the failure instead.
        if self.state == UnitActiveState.RELOADING:
            raise MountActivationError(
                f"Reloading {self.name} did not complete in time and the "
                f"unit is still in RELOADING. Refusing to escalate to a "
                f"restart while the mount helper may be pinned in the "
                f"kernel — this should not happen with the configured "
                f"unit timeout. Check host logs for the systemd unit "
                f"{self.unit_name} for details.",
                _LOGGER.critical,
            )

        if not await self.is_mounted():
            _LOGGER.info(
                "Mount %s not correctly mounted after a reload. Trying a restart",
                self.name,
            )
            await self._restart()

        self._dismiss_failed_issue()

    def _dismiss_failed_issue(self) -> None:
        """Dismiss the failed-mount resolution issue if present."""
        if issue := self.sys_resolution.get_issue_if_present(self.failed_issue):
            self.sys_resolution.dismiss_issue(issue)

    async def _restart(self) -> None:
        """Restart mount unit to re-mount."""
        try:
            await self._run_systemd_job(
                "restart_unit",
                self.sys_dbus.systemd.restart_unit(self.unit_name, StartUnitMode.FAIL),
            )
        except DBusSystemdNoSuchUnit:
            _LOGGER.info(
                "Mount %s is not mounted, mounting instead of restarting", self.name
            )
            await self.mount()
            return
        except DBusError as err:
            raise MountError(
                f"Could not restart mount {self.name} due to: {err!s}", _LOGGER.error
            ) from err

        if unit := await self._update_unit():
            await self._update_state(unit)

        if not await self.is_mounted():
            raise MountActivationError(
                f"Restarting {self.name} did not succeed. Check host logs for errors from mount or systemd unit {self.unit_name} for details.",
                _LOGGER.error,
            )


class NetworkMount(Mount, ABC):
    """A network mount."""

    def to_dict(self, *, skip_secrets: bool = True) -> MountData:
        """Return dictionary representation."""
        out = MountData(server=self.server, **super().to_dict())
        if self.port is not None:
            out["port"] = self.port
        return out

    @property
    def server(self) -> str:
        """Get server."""
        return self._data["server"]

    @property
    def port(self) -> int | None:
        """Get port, returns none if using the protocol default."""
        return self._data.get("port")

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
        """Return true if the mount is active and the server actually answers.

        Three checks compose the verdict:

        1. systemd reports the unit ACTIVE — cheap, may be stale.
        2. `os.statvfs()` forces an RPC for both NFS (FSSTAT) and CIFS
           (QUERY_FS_INFO). Those per-filesystem fields aren't cached
           client-side, so the kernel must reach the server or fail
           with ETIMEDOUT / EHOSTDOWN / ECONNABORTED. We do this
           first because on a dead server it fails fast within the
           protocol budget (~30s, bounded by softerr,timeo=100,retrans=2
           for NFS and soft,echo_interval=10 for CIFS) — and on a
           ghost mount (path no longer mounted, e.g. after a failed
           restart whose umount succeeded but mount step failed) it
           returns the underlying root filesystem's stats without
           touching the network.
        3. A parent vs. path `st_dev` comparison distinguishes the
           ghost-mount case from a real live mount: statvfs succeeds
           for both, but only a real mount crosses a filesystem
           boundary. These stat calls are cheap on success — the
           attrs were just revalidated by the successful statvfs.

        Both syscalls run in a single executor hop so they share one
        thread and the kernel's warm session state. No asyncio
        timeout — the kernel-side bound is authoritative.
        """
        if self.state != UnitActiveState.ACTIVE:
            return False

        local_where = self.local_where
        _LOGGER.debug("Probing mount %s at %s", self.name, local_where)
        start = time.monotonic()
        try:
            is_real_mount = await self.sys_run_in_executor(
                _probe_network_mount, local_where
            )
        except OSError as err:
            _LOGGER.debug(
                "Probe of mount %s failed after %.2fs: %s",
                self.name,
                time.monotonic() - start,
                err,
            )
            return False
        elapsed = time.monotonic() - start
        if not is_real_mount:
            _LOGGER.debug(
                "Mount %s reported active but %s is not a mount point (probe %.2fs)",
                self.name,
                local_where,
                elapsed,
            )
            return False
        _LOGGER.debug("Probe of mount %s succeeded in %.2fs", self.name, elapsed)
        return True


class CIFSMount(NetworkMount):
    """A CIFS type mount."""

    def to_dict(self, *, skip_secrets: bool = True) -> MountData:
        """Return dictionary representation."""
        out = MountData(share=self.share, **super().to_dict())
        if not skip_secrets and self.username is not None and self.password is not None:
            out["username"] = self.username
            out["password"] = self.password
        out["version"] = self.version
        return out

    @property
    def share(self) -> str:
        """Get share."""
        return self._data["share"]

    @property
    def username(self) -> str | None:
        """Get username, returns none if auth is not used."""
        return self._data.get("username")

    @property
    def password(self) -> str | None:
        """Get password, returns none if auth is not used."""
        return self._data.get("password")

    @property
    def version(self) -> str | None:
        """Get cifs version, returns none if using default."""
        version = self._data.get("version")
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
        # soft + echo_interval=10 + retrans=0 give a ~30s per-operation budget
        # before the kernel reports the server unreachable (3 × echo_interval
        # since last server response). This roughly matches the NFS budget
        # from `softerr,timeo=100,retrans=2` so the userspace probe behaves
        # symmetrically across both protocols. On give-up the syscall
        # returns EHOSTDOWN / ECONNABORTED rather than blocking forever,
        # which is what makes the statvfs probe a reliable health check.
        # `soft` is the kernel default but is set explicitly so the
        # behavior is part of the recorded mount options rather than an
        # implicit assumption.
        options = super().options + [
            "noserverino",
            "soft",
            "echo_interval=10",
            "retrans=0",
        ]
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
        return PurePath(self._data["path"])

    @property
    def what(self) -> str:
        """What to mount."""
        return f"{self.server}:{self.path.as_posix()}"

    @property
    def options(self) -> list[str]:
        """Options to use to mount."""
        return super().options + ["softerr", "timeo=100", "retrans=2"]


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
        path: PurePath,
        usage: MountUsage | None = None,
        where: PurePath | None = None,
        read_only: bool = False,
    ) -> BindMount:
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
        return PurePath(self._data["path"])

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
