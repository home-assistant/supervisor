"""Network mounts in supervisor."""

from abc import ABC, abstractmethod
import asyncio
from collections.abc import Awaitable, Callable
from contextlib import suppress
import errno
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
    DBUS_ATTR_LAZY_UNMOUNT,
    DBUS_ATTR_OPTIONS,
    DBUS_ATTR_START_LIMIT_INTERVAL_USEC,
    DBUS_ATTR_TIMEOUT_USEC,
    DBUS_ATTR_TYPE,
    DBUS_ATTR_WHAT,
    DBUS_ATTR_WHERE,
    DBUS_SIGNAL_SYSTEMD_JOB_REMOVED,
    StartUnitMode,
    StopUnitMode,
    UnitActiveState,
)
from ..dbus.systemd import SystemdUnit, job_removed_filter
from ..docker.const import PATH_MEDIA, PATH_SHARE
from ..exceptions import (
    DBusError,
    DBusSystemdNoSuchUnit,
    MountActivationError,
    MountError,
    MountInvalidError,
    MountReloadError,
    MountSetupError,
    MountTargetNotDirectoryError,
    MountTargetNotEmptyError,
    MountUnmountError,
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

    statvfs is the trigger-and-probe primitive: the statfs syscall
    walks with LOOKUP_AUTOMOUNT (fs/statfs.c), so it activates a
    dormant autofs trigger, and it forces an RPC for both NFS
    (FSSTAT) and CIFS (QUERY_FS_INFO) — per-filesystem fields with
    no client-side cache, so the kernel must reach the server or
    fail.

    Raises OSError when the mount cannot be activated or the server
    is unreachable. Typical errnos: ENODEV (systemd reported the
    triggered .mount start as failed), EHOSTDOWN (the .automount was
    stopped while we waited), ETIMEDOUT / ECONNABORTED (established
    mount, server gone), ELOOP (the autofs trigger cannot propagate
    into the caller's mount namespace — a propagation misconfig).

    Returns False when statvfs succeeded but the path does not cross
    a filesystem boundary — e.g. a disarmed trigger that reverted to
    a plain directory. The follow-up stat calls run with
    AT_NO_AUTOMOUNT forced by the kernel (fs/stat.c), so they
    observe rather than re-trigger.
    """
    os.statvfs(path)
    return path.stat().st_dev != path.parent.stat().st_dev


# Layered timeouts, ordered so each layer gives up before the one above it
# (see #6827): the kernel RPC timeout (~30 s from timeo=100,retrans=2) lets
# the mount helper exit, systemd's unit timeout then kills whatever is left,
# and only after that does Supervisor stop awaiting the unit state.
MOUNT_UNIT_TIMEOUT_USEC = 35 * 1_000_000
UPDATE_STATE_TIMEOUT = 40
# Maximum time to wait for a systemd job to leave the queue, comfortably
# above the unit timeout so a job against a dead server fails on its own
# terms rather than here.
SYSTEMD_JOB_TIMEOUT = 90

COERCE_MOUNT_TYPE: Callable[[str], MountType] = Coerce(MountType)
COERCE_MOUNT_USAGE: Callable[[str], MountUsage] = Coerce(MountUsage)


def _unit_name_from_path(path: PurePath, unit_type: str = "mount") -> str:
    """Return the systemd unit name for a mount path.

    Matches systemd's unit_name_from_path() for the simple paths used
    here (no characters needing escaping beyond '/').
    """
    return f"{path.as_posix()[1:].replace('/', '-')}.{unit_type}"


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
        raise MountInvalidError(f"Unsupported mount type: {type_}", _LOGGER.error)

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
        """Systemd unit name for the .mount unit."""
        return _unit_name_from_path(self.where)

    @property
    def automount_unit_name(self) -> str:
        """Systemd unit name for the companion .automount unit."""
        return _unit_name_from_path(self.where, "automount")

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
        """Initialize object.

        Transient units don't persist across host reboots, so on a fresh
        host start both units are missing and we create the `.automount`
        + `.mount` pair. On a Supervisor-only restart the pair may still
        exist and is adopted.
        """
        unit = await self._update_unit()
        automount_state = await self._automount_state()

        if automount_state is None:
            # A unit at the automount's path without a trigger is a
            # leftover from the eager-mount design (Supervisor restart
            # without a host reboot). It has to go before arming: the unit
            # name collides, and mount() would misread the mounted share's
            # contents as blocking local data
            if unit:
                await self._stop_legacy_unit(self.unit_name, strict=True)
            try:
                await self.mount()
            finally:
                # Arming is what orphans the eager-mount-era share, so it
                # has to go even when the probe found the server down
                await self._cleanup_legacy_data_mount()
            return

        if automount_state != UnitActiveState.ACTIVE:
            # A dead trigger (failed, or stopped out-of-band) leaves the
            # path a plain writable directory, so never adopt one
            _LOGGER.info(
                "Automount trigger for %s is %s on load, re-arming",
                self.name,
                automount_state,
            )
            await self.unmount()
            await self.mount()
            return

        if unit:
            await self._update_state_await(unit)
        # The .mount unit is inactive until something triggers it, so only
        # the probe tells reachability apart from a dormant trigger
        if not await self.is_mounted():
            _LOGGER.error(
                "Mount %s is not reachable. Check host logs for errors from "
                "mount or systemd unit %s for details",
                self.name,
                self.unit_name,
            )
            raise MountActivationError(name=self.name)

    async def _automount_state(self) -> UnitActiveState | None:
        """Return the .automount unit state, or None if no unit is loaded."""
        try:
            unit = await self.sys_dbus.systemd.get_unit(self.automount_unit_name)
            return UnitActiveState(await unit.get_active_state())
        except DBusSystemdNoSuchUnit:
            return None
        except DBusError as err:
            await async_capture_exception(err)
            raise MountError(f"Could not get automount unit due to: {err!s}") from err

    async def _stop_legacy_unit(self, unit_name: str, *, strict: bool) -> None:
        """Stop a mount unit left over from the eager-mount design.

        Strict for the unit occupying the automount's path: a failed stop
        leaves the path covered, which is safe and retryable, while arming
        over a still mounted share would misread its contents as local
        data. Best effort for the mount at the mounts data directory: it
        conflicts with neither the path nor the unit names, and its
        unmount can time out against an unreachable server (legacy units
        have no LazyUnmount).
        """
        try:
            result = await self._run_systemd_job(
                "stop_unit",
                self.sys_dbus.systemd.stop_unit(unit_name, StopUnitMode.FAIL),
            )
        except DBusSystemdNoSuchUnit:
            return
        except DBusError as err:
            if strict:
                _LOGGER.error(
                    "Could not stop legacy unit %s for %s due to: %s",
                    unit_name,
                    self.name,
                    err,
                )
                raise MountSetupError(name=self.name) from err
            _LOGGER.warning(
                "Could not stop legacy unit %s for %s: %s", unit_name, self.name, err
            )
            return

        if result != "done":
            if strict:
                _LOGGER.error(
                    "Could not stop legacy unit %s for %s (systemd result: %s)",
                    unit_name,
                    self.name,
                    result,
                )
                raise MountSetupError(name=self.name)
            _LOGGER.warning(
                "Could not stop legacy unit %s for %s (systemd result: %s)",
                unit_name,
                self.name,
                result,
            )
            return

        _LOGGER.info("Removed legacy mount unit %s for mount %s", unit_name, self.name)
        with suppress(DBusError):
            await self.sys_dbus.systemd.reset_failed_unit(unit_name)

    async def _cleanup_legacy_data_mount(self) -> None:
        """Unmount the eager-mount-era share at the mounts data directory.

        Runs after the automount is armed, so a failure here cannot leave
        the container-facing path unprotected. An orphaned mount is
        retried on the next Supervisor restart and cleared by a reboot.
        """
        legacy_data_unit = _unit_name_from_path(
            self.sys_config.path_extern_mounts / self.name
        )
        if legacy_data_unit == self.unit_name:
            return

        # Ask systemd rather than stat'ing the path: with the server gone
        # the stat blocks until the mount's soft timeout, and its error
        # would fail a load that armed the trigger just fine
        try:
            await self.sys_dbus.systemd.get_unit(legacy_data_unit)
        except DBusSystemdNoSuchUnit:
            return
        except DBusError as err:
            _LOGGER.warning(
                "Could not check legacy unit %s for %s: %s",
                legacy_data_unit,
                self.name,
                err,
            )
            return

        await self._stop_legacy_unit(legacy_data_unit, strict=False)

    async def repair_trigger(self) -> None:
        """Ensure the automount trigger is armed, re-creating units if needed.

        Covers the "trigger died" scenarios: the `.automount` failed (e.g.
        the autofs mount was unmounted out-of-band), was stopped, or is
        gone entirely. Resets any failure state so the transient units can
        be re-created, then arms a fresh pair.
        """
        state = await self._automount_state()
        if state == UnitActiveState.ACTIVE:
            return

        _LOGGER.info(
            "Automount trigger for %s is %s, re-arming",
            self.name,
            state or "missing",
        )
        # Full teardown first: the .mount may still be attached (e.g. the
        # .automount was stopped out-of-band while the share stayed
        # mounted). Arming over it would fail — or worse, mount() would
        # misread the mounted share's contents as blocking local data.
        await self.unmount()
        await self.mount()

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
        # Late-bound: dispatch hasn't run yet when we subscribe; the
        # filter reads job_path each time it's evaluated, so it picks
        # up the assignment below before any JobRemoved is consumed.
        job_path: str | None = None
        async with self.sys_dbus.systemd.connected_dbus.signal(
            DBUS_SIGNAL_SYSTEMD_JOB_REMOVED,
            job_removed_filter(lambda: job_path),
        ) as signal:
            job_path = await dispatch
            try:
                async with asyncio.timeout(SYSTEMD_JOB_TIMEOUT):
                    _id, _path, _unit, result = await signal.wait_for_signal()
            except TimeoutError:
                _LOGGER.warning(
                    "Systemd %s job for mount %s did not complete within %d seconds",
                    op_name,
                    self.name,
                    SYSTEMD_JOB_TIMEOUT,
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
                raise MountTargetNotDirectoryError(
                    _LOGGER.error, name=self.name, path=self.local_where.as_posix()
                )
            elif any(self.local_where.iterdir()):
                raise MountTargetNotEmptyError(
                    _LOGGER.error, name=self.name, path=self.local_where.as_posix()
                )

        await self.sys_run_in_executor(ensure_empty_folder)

        options = (
            [(DBUS_ATTR_OPTIONS, Variant("s", ",".join(self.options)))]
            if self.options
            else []
        )
        mount_properties = options + [
            (DBUS_ATTR_TYPE, Variant("s", self.type)),
            (DBUS_ATTR_DESCRIPTION, Variant("s", self.description)),
            (DBUS_ATTR_WHAT, Variant("s", self.what)),
            (DBUS_ATTR_TIMEOUT_USEC, Variant("t", MOUNT_UNIT_TIMEOUT_USEC)),
            # MNT_DETACH on umount, so teardown never blocks on an
            # unreachable server. Open fds error out on their next
            # operation through softerr (NFS) / soft (CIFS).
            (DBUS_ATTR_LAZY_UNMOUNT, Variant("b", True)),
            # No start rate limiting: hitting the default limit (5 starts
            # in 10 s, successful ones included) makes systemd detach the
            # autofs trigger entirely and the path degrades to a plain,
            # writable directory. TimeoutUSec paces retries instead.
            (DBUS_ATTR_START_LIMIT_INTERVAL_USEC, Variant("t", 0)),
        ]

        # The .automount has to be the primary unit — its start job is what
        # arms the trigger, and aux units get no start job of their own.
        # TimeoutIdleUSec stays at its default of never: kernel idle expiry
        # counts only the host namespace, so it would unmount shares from
        # under add-ons holding files open in their own namespace.
        await self._arm_automount(aux=[(self.unit_name, mount_properties)])

        if unit := await self._update_unit():
            await self._update_state(unit)

        # After creation only the `.automount` is active; the `.mount`
        # stays inactive until first access. is_mounted() — a statvfs probe
        # through the autofs trigger — both forces the initial activation
        # and confirms the server answers, surfacing problems immediately
        # rather than letting them lurk until the next consumer hits the
        # path.
        if not await self.is_mounted():
            _LOGGER.error(
                "Mounting %s did not succeed. Check host logs for errors from "
                "mount or systemd unit %s for details",
                self.name,
                self.unit_name,
            )
            raise MountActivationError(name=self.name)

    async def _arm_automount(
        self, aux: list[tuple[str, list[tuple[str, Variant]]]] | None = None
    ) -> None:
        """Create the transient .automount, optionally with its .mount aux unit.

        Without ``aux`` the trigger is armed against an already loaded
        `.mount` definition, which systemd would reject as an aux unit
        because transient creation requires a pristine one.
        """
        automount_properties = [
            (
                DBUS_ATTR_DESCRIPTION,
                Variant("s", f"{self.description} (automount)"),
            ),
            (DBUS_ATTR_WHERE, Variant("s", self.where.as_posix())),
        ]

        try:
            result = await self._run_systemd_job(
                "start_transient_unit",
                self.sys_dbus.systemd.start_transient_unit(
                    self.automount_unit_name,
                    StartUnitMode.FAIL,
                    automount_properties,
                    aux=aux,
                ),
            )
        except DBusError as err:
            _LOGGER.error("Could not mount %s due to: %s", self.name, err)
            raise MountSetupError(name=self.name) from err
        # A failed start job means the trigger never armed and the path is
        # a plain writable directory — a hard setup failure, distinct from
        # the armed-but-unreachable MountActivationError the probe raises
        if result != "done":
            _LOGGER.error(
                "Could not arm automount for %s (systemd job result: %s)",
                self.name,
                result,
            )
            raise MountSetupError(name=self.name)

    async def unmount(self) -> None:
        """Unmount using systemd."""
        # Stop the .automount first: it disarms the trigger so nothing can
        # re-mount during cleanup, and it lazily detaches the whole stack
        # at the path (systemd's unmount_autofs() uses MNT_DETACH), so the
        # stop cannot block on an unreachable server. Stopping an automount
        # is synchronous and cannot fail on its own — an error here means
        # systemd could not be reached, which must not pass silently: it
        # would leave an armed trigger at the path of a removed mount.
        try:
            result = await self._run_systemd_job(
                "stop_unit",
                self.sys_dbus.systemd.stop_unit(
                    self.automount_unit_name, StopUnitMode.FAIL
                ),
            )
            if result != "done":
                _LOGGER.error(
                    "Could not stop automount unit for %s (systemd result: %s)",
                    self.name,
                    result,
                )
                raise MountUnmountError(name=self.name)
        except DBusSystemdNoSuchUnit:
            pass
        except DBusError as err:
            _LOGGER.error(
                "Could not stop automount unit for %s due to: %s", self.name, err
            )
            raise MountUnmountError(name=self.name) from err

        # Resolve the .mount unit only after the automount stop: the lazy
        # detach can take the active .mount down with it, and systemd then
        # garbage-collects the transient unit — a proxy fetched earlier
        # would point at a vanished D-Bus object.
        unit = await self._update_unit()
        if not unit:
            _LOGGER.info("Mount %s is not mounted, skipping unmount", self.name)
        else:
            await self._update_state(unit)
            try:
                if self.state != UnitActiveState.FAILED:
                    result = await self._run_systemd_job(
                        "stop_unit",
                        self.sys_dbus.systemd.stop_unit(
                            self.unit_name, StopUnitMode.FAIL
                        ),
                    )
                    # A failed stop job is an error, not a success — treating
                    # it as done is how a stale mount once survived a
                    # "successful" cleanup (see #6938).
                    if result != "done":
                        _LOGGER.error(
                            "Could not unmount %s (systemd result: %s)",
                            self.name,
                            result,
                        )
                        await self._rearm_after_failed_unmount()
                        raise MountUnmountError(name=self.name)
            except DBusSystemdNoSuchUnit:
                # Unit went away with the automount detach — fine.
                pass
            except DBusError as err:
                _LOGGER.error("Could not unmount %s due to: %s", self.name, err)
                await self._rearm_after_failed_unmount()
                raise MountUnmountError(name=self.name) from err

        # Clear any failure state so the dead transient units get
        # garbage-collected instead of lingering.
        for unit_name in (self.automount_unit_name, self.unit_name):
            with suppress(DBusError):
                await self.sys_dbus.systemd.reset_failed_unit(unit_name)

        self._unit = None
        self._state = None

    async def _rearm_after_failed_unmount(self) -> None:
        """Cover the path again after the .mount could not be stopped.

        The automount stop already detached the whole stack, so a failing
        .mount stop leaves a plain writable directory behind. One attempt
        to arm a fresh pair, best effort — if that fails too the local
        data repair picks up whatever lands there.
        """
        for unit_name in (self.automount_unit_name, self.unit_name):
            with suppress(DBusError):
                await self.sys_dbus.systemd.reset_failed_unit(unit_name)

        try:
            await self.mount()
            return
        except MountActivationError:
            # Armed, the server just did not answer the probe
            return
        except MountInvalidError as err:
            # Something wrote into the path while it was uncovered. Arming
            # over that data would hide it: reconciliation sees a healthy
            # trigger and the repair skips mount points. Leave the path as
            # it is so the next reconcile offers to move the data away
            _LOGGER.warning(
                "Could not re-arm automount for %s after a failed unmount: %s",
                self.name,
                err,
            )
            return
        except (MountError, OSError) as err:
            _LOGGER.debug(
                "Could not re-create the unit pair for %s, arming the trigger "
                "against the existing mount unit instead: %s",
                self.name,
                err,
            )

        # The .mount definition is still loaded whenever stopping it is
        # what failed, so the pair above is rejected. The trigger on its
        # own covers the path and fires that surviving definition.
        try:
            await self._arm_automount()
        except MountError as err:
            _LOGGER.warning(
                "Could not re-arm automount for %s after a failed unmount, "
                "its path is a local directory until the next reload: %s",
                self.name,
                err,
            )

    async def discard_session(self) -> None:
        """Stop the .mount unit while keeping the automount trigger armed.

        Used when an established mount's session is permanently dead
        (e.g. the server was replaced): the kernel cannot recover it,
        and since the path stays covered the trigger never re-fires.
        Stopping only the `.mount` (LazyUnmount detaches immediately)
        makes systemd re-install the autofs trigger over the path — the
        same mechanism idle-expiry uses, and the automount's Triggers=
        reference keeps the transient `.mount` definition alive — so
        the path is never exposed as a writable directory. The next
        access mounts fresh, establishing a new session.
        """
        try:
            result = await self._run_systemd_job(
                "stop_unit",
                self.sys_dbus.systemd.stop_unit(self.unit_name, StopUnitMode.FAIL),
            )
            if result != "done":
                _LOGGER.error(
                    "Could not stop %s to force re-creation of the mount "
                    "(systemd result: %s)",
                    self.name,
                    result,
                )
                raise MountReloadError(name=self.name)
        except DBusSystemdNoSuchUnit:
            # Nothing mounted — the trigger alone covers the path
            pass
        except DBusError as err:
            _LOGGER.error(
                "Could not stop %s to force re-creation of the mount due to: %s",
                self.name,
                err,
            )
            raise MountReloadError(name=self.name) from err

        with suppress(DBusError):
            await self.sys_dbus.systemd.reset_failed_unit(self.unit_name)

        self._unit = None
        self._state = None

    def dismiss_failed_issue(self) -> None:
        """Dismiss the failed-mount resolution issue if present."""
        if issue := self.sys_resolution.get_issue_if_present(self.failed_issue):
            self.sys_resolution.dismiss_issue(issue)


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
        """Where to mount.

        Media and share mounts live directly under the container-facing
        media/share dirs — containers see them via the parent-dir RSLAVE
        bind and the autofs trigger sits inside the propagated
        namespace. Backup mounts have no container-facing path; they
        stay under path_extern_mounts/.
        """
        match self.usage:
            case MountUsage.MEDIA:
                return self.sys_config.path_extern_media / self.name
            case MountUsage.SHARE:
                return self.sys_config.path_extern_share / self.name
            case _:
                return self.sys_config.path_extern_mounts / self.name

    @property
    def options(self) -> list[str]:
        """Options to use to mount."""
        options = super().options
        if self.port:
            options.append(f"port={self.port}")
        return options

    async def is_mounted(self) -> bool:
        """Return true if the mount is reachable.

        Under autofs the underlying `.mount` is dormant until first
        access, so systemd state alone is meaningless for "is the
        share usable"; we have to actually access the path. statvfs
        both triggers a dormant automount (the statfs syscall walks
        with LOOKUP_AUTOMOUNT) and forces an RPC for both NFS and
        CIFS, so the kernel must reach the server or fail with
        ETIMEDOUT / EHOSTDOWN / ECONNABORTED / ENODEV.

        After a successful probe we update `self._state` to ACTIVE
        so the API surface reports "active" for healthy mounts. A
        failed probe sets it to INACTIVE.

        No asyncio timeout — the kernel-side bound is authoritative,
        and adding one would only orphan the executor thread on a
        stuck syscall without unblocking it.
        """
        local_where = self.local_where
        _LOGGER.debug("Probing mount %s at %s", self.name, local_where)
        start = time.monotonic()
        try:
            is_real_mount = await self.sys_run_in_executor(
                _probe_network_mount, local_where
            )
        except OSError as err:
            if err.errno == errno.ELOOP:
                # The kernel returns ELOOP when a process loops on an
                # autofs trigger whose activation cannot propagate into
                # its mount namespace — a mount propagation
                # misconfiguration, not a server problem.
                _LOGGER.error(
                    "Probe of mount %s failed with ELOOP — the automount "
                    "cannot propagate into this mount namespace. Check "
                    "mount propagation configuration",
                    self.name,
                )
            _LOGGER.debug(
                "Probe of mount %s failed after %.2fs: %s",
                self.name,
                time.monotonic() - start,
                err,
            )
            self._state = UnitActiveState.INACTIVE
            return False
        elapsed = time.monotonic() - start
        if not is_real_mount:
            _LOGGER.debug(
                "Probe of mount %s succeeded but %s is not a mount point (%.2fs)",
                self.name,
                local_where,
                elapsed,
            )
            self._state = UnitActiveState.INACTIVE
            return False
        _LOGGER.debug("Probe of mount %s succeeded in %.2fs", self.name, elapsed)
        self._state = UnitActiveState.ACTIVE
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
        # soft + echo_interval=10 + retrans=0 give a ~30 s budget per
        # operation before the syscall returns EHOSTDOWN instead of blocking,
        # which is what makes the statvfs probe a reliable health check. It
        # matches the NFS budget above so both protocols behave alike. soft
        # is the kernel default, set explicitly to record the intent.
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
