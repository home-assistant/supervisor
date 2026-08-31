"""Supervisor mount manager."""

import asyncio
from collections.abc import Awaitable
from contextlib import suppress
from dataclasses import replace
import logging
from pathlib import Path
from typing import Self

from ..const import ATTR_NAME
from ..coresys import CoreSys, CoreSysAttributes
from ..exceptions import (
    MountActivationError,
    MountError,
    MountJobError,
    MountNotFound,
    MountTargetNotDirectoryError,
    MountTargetNotEmptyError,
)
from ..host.const import HostFeature
from ..jobs.const import JobCondition
from ..jobs.decorator import Job
from ..resolution.const import ContextType, SuggestionType
from ..utils.common import FileConfiguration
from ..utils.sentry import async_capture_exception
from .const import (
    ATTR_DEFAULT_BACKUP_MOUNT,
    ATTR_MOUNTS,
    FILE_CONFIG_MOUNTS,
    MountUsage,
)
from .mount import Mount
from .validate import SCHEMA_MOUNTS_CONFIG

_LOGGER: logging.Logger = logging.getLogger(__name__)


class MountManager(FileConfiguration, CoreSysAttributes):
    """Mount manager for supervisor.

    Loads the saved mount configs at startup, creates and removes the
    transient `.mount` + `.automount` unit pairs, and surfaces failures as
    resolution issues. Activation and reconnect are left to the kernel;
    the periodic reconcile only re-arms dead triggers and keeps the
    reported state and the resolution issues in sync.
    """

    def __init__(self, coresys: CoreSys):
        """Initialize object."""
        super().__init__(
            coresys.config.path_supervisor / FILE_CONFIG_MOUNTS, SCHEMA_MOUNTS_CONFIG
        )

        self.coresys: CoreSys = coresys
        self._mounts: dict[str, Mount] = {}

    async def load_config(self) -> Self:
        """Load config in executor."""
        await super().load_config()
        self._mounts = {
            mount[ATTR_NAME]: Mount.from_dict(self.coresys, mount)
            for mount in self._data[ATTR_MOUNTS]
        }
        return self

    @property
    def mounts(self) -> list[Mount]:
        """Return list of mounts."""
        return list(self._mounts.values())

    @property
    def backup_mounts(self) -> list[Mount]:
        """Return list of backup mounts."""
        return [mount for mount in self.mounts if mount.usage == MountUsage.BACKUP]

    @property
    def media_mounts(self) -> list[Mount]:
        """Return list of media mounts."""
        return [mount for mount in self.mounts if mount.usage == MountUsage.MEDIA]

    @property
    def share_mounts(self) -> list[Mount]:
        """Return list of share mounts."""
        return [mount for mount in self.mounts if mount.usage == MountUsage.SHARE]

    @property
    def default_backup_mount(self) -> Mount | None:
        """Get default backup mount if set."""
        if ATTR_DEFAULT_BACKUP_MOUNT not in self._data:
            return None
        return self.get(self._data[ATTR_DEFAULT_BACKUP_MOUNT])

    @default_backup_mount.setter
    def default_backup_mount(self, value: Mount | None):
        """Set or unset default backup mount."""
        if value:
            self._data[ATTR_DEFAULT_BACKUP_MOUNT] = value.name
        else:
            self._data.pop(ATTR_DEFAULT_BACKUP_MOUNT, None)

    def get(self, name: str) -> Mount:
        """Get mount by name."""
        if name not in self._mounts:
            raise MountNotFound(f"No mount exists with name '{name}'")
        return self._mounts[name]

    def __contains__(self, item: Mount | str) -> bool:
        """Return true if specified mount exists."""
        if isinstance(item, str):
            return item in self._mounts
        return item.name in self._mounts

    async def load(self) -> None:
        """Set up transient mount units for all saved mounts."""
        if not self.mounts:
            return

        if HostFeature.MOUNT not in self.sys_host.features:
            _LOGGER.error(
                "Cannot load configured mounts because mounting not supported on system!"
            )
            return

        _LOGGER.info("Initializing all user-configured mounts")
        await self._mount_errors_to_issues(
            self.mounts.copy(), [mount.load() for mount in self.mounts]
        )

    async def _mount_errors_to_issues(
        self, mounts: list[Mount], mount_tasks: list[Awaitable[None]]
    ) -> None:
        """Await a list of tasks on mounts and turn each error into a resolution issue."""
        errors = await asyncio.gather(*mount_tasks, return_exceptions=True)

        for i in range(len(errors)):  # pylint: disable=consider-using-enumerate
            if not (err := errors[i]):
                continue
            if isinstance(err, MountTargetNotEmptyError | MountTargetNotDirectoryError):
                self._add_local_data_issue(mounts[i])
                continue
            if mounts[i].failed_issue in self.sys_resolution.issues:
                continue
            if not isinstance(err, MountError):
                await async_capture_exception(err)

            self.sys_resolution.add_issue(
                replace(mounts[i].failed_issue),
                suggestions=[
                    SuggestionType.EXECUTE_RELOAD,
                    SuggestionType.EXECUTE_REMOVE,
                ],
            )

    def _add_local_data_issue(self, mount: Mount) -> None:
        """Add mount failed issue offering to move blocking local data.

        Uses the same mount failed issue as other mount failures so at most
        one issue exists per mount, with an additional suggestion to move the
        blocking data aside. Reload stays available for users who prefer to
        clear the data themselves. Adding is idempotent: an existing issue
        just gains the extra suggestion.
        """
        self.sys_resolution.add_issue(
            replace(mount.failed_issue),
            suggestions=[
                SuggestionType.MOVE_LOCAL_DATA,
                SuggestionType.EXECUTE_RELOAD,
                SuggestionType.EXECUTE_REMOVE,
            ],
        )

    @Job(
        name="mount_manager_create_mount",
        conditions=[JobCondition.MOUNT_AVAILABLE],
        on_condition=MountJobError,
    )
    async def create_mount(self, mount: Mount) -> None:
        """Add/update a mount."""
        # Add mount name to job
        self.sys_jobs.current.reference = mount.name

        await self._check_local_data_conflict(mount)

        if mount.name in self._mounts:
            _LOGGER.debug(
                "Mount '%s' exists, unmounting then mounting from new config",
                mount.name,
            )
            await self.remove_mount(mount.name, retain_entry=True)

        _LOGGER.info("Creating or updating mount: %s", mount.name)
        try:
            await mount.load()
        except MountError:
            # Roll back so a failed add/update does not leave a half-created
            # mount behind: units active and the mount listed, but never
            # persisted to the configuration.
            with suppress(MountError):
                await mount.unmount()
            raise

        self._mounts[mount.name] = mount

    async def _check_local_data_conflict(self, mount: Mount) -> None:
        """Fail fast if a target directory of the mount contains local data.

        The authoritative check happens when each unit is mounted, but by
        then the data mount is already active. Checking upfront lets an
        add/update whose target directory holds local data (e.g. written by
        an add-on while no mount was in place) fail cleanly before anything
        is touched. Paths that are already mount points are skipped — they
        get unmounted before reuse.
        """
        paths = [mount.local_where]

        def check_conflict() -> None:
            for path in paths:
                try:
                    if path.is_mount() or not path.exists():
                        continue
                    if not path.is_dir():
                        raise MountTargetNotDirectoryError(
                            _LOGGER.error, name=mount.name, path=path.as_posix()
                        )
                    if any(path.iterdir()):
                        raise MountTargetNotEmptyError(
                            _LOGGER.error, name=mount.name, path=path.as_posix()
                        )
                except OSError:
                    # Not inspectable (e.g. an unreachable network mount) —
                    # leave it to the mount-time check
                    continue

        await self.sys_run_in_executor(check_conflict)

    @Job(
        name="mount_manager_remove_mount",
        conditions=[JobCondition.MOUNT_AVAILABLE],
        on_condition=MountJobError,
    )
    async def remove_mount(self, name: str, *, retain_entry: bool = False) -> Mount:
        """Remove a mount."""
        # Add mount name to job
        self.sys_jobs.current.reference = name

        if name not in self._mounts:
            raise MountNotFound(
                f"Cannot remove '{name}', no mount exists with that name"
            )

        _LOGGER.info("Removing mount: %s", name)
        mount = self._mounts[name]
        await mount.unmount()
        if not retain_entry:
            del self._mounts[name]

        if self._data.get(ATTR_DEFAULT_BACKUP_MOUNT) == mount.name:
            self.default_backup_mount = None

        return mount

    @Job(name="mount_manager_reload", conditions=[JobCondition.MOUNT_AVAILABLE])
    async def reload(self) -> None:
        """Reconcile mount triggers, state, and resolution issues.

        Deliberately no reload/restart of established mounts — the kernel
        recovers those on its own. This re-arms dead autofs triggers (so
        the path never degrades to a plain writable directory), refreshes
        the probe-based state that the API and backup locations report,
        and syncs the mount failed issue in both directions.
        """
        if not self.mounts:
            return

        await asyncio.gather(
            *[self._reconcile_mount(mount) for mount in self.mounts.copy()]
        )

    async def _reconcile_mount(self, mount: Mount) -> None:
        """Reconcile a single mount's trigger, state, and issue."""
        try:
            await mount.repair_trigger()
        except MountTargetNotEmptyError, MountTargetNotDirectoryError:
            self._add_local_data_issue(mount)
            return
        except MountError as err:
            _LOGGER.warning(
                "Could not repair automount trigger for %s: %s", mount.name, err
            )
            self._add_failed_issue(mount)
            return

        if await mount.is_mounted():
            mount.dismiss_failed_issue()
        else:
            self._add_failed_issue(mount)

    @Job(
        name="mount_manager_reload_mount",
        conditions=[JobCondition.MOUNT_AVAILABLE],
        on_condition=MountJobError,
    )
    async def reload_mount(self, name: str) -> None:
        """Probe a mount's health and surface the result.

        Re-arms the trigger if it died, probes the path so the kernel
        activates the mount, and updates the resolution issue from the
        outcome. A healthy mount is left alone, autofs repeats that work
        whenever something accesses the path.
        """
        # Add mount name to job
        self.sys_jobs.current.reference = name

        if name not in self._mounts:
            raise MountNotFound(
                f"Cannot reload '{name}', no mount exists with that name"
            )

        mount = self._mounts[name]
        try:
            await mount.repair_trigger()
        except MountTargetNotEmptyError, MountTargetNotDirectoryError:
            # Local data blocks re-creating the mount — offer moving it
            self._add_local_data_issue(mount)
            raise
        except MountError:
            self._add_failed_issue(mount)
            raise

        _LOGGER.info("Probing mount: %s", name)
        if await mount.is_mounted():
            mount.dismiss_failed_issue()
            return

        # A permanently dead session (e.g. the server was replaced) keeps
        # the path mounted, so the trigger never re-fires. Stopping just
        # the .mount makes systemd re-install the trigger — the path stays
        # covered and the re-probe mounts fresh.
        _LOGGER.info(
            "Mount %s is unreachable, discarding its session for a fresh mount", name
        )
        try:
            await mount.discard_session()
        except MountError:
            self._add_failed_issue(mount)
            raise

        if not await mount.is_mounted():
            self._add_failed_issue(mount)
            _LOGGER.error(
                "Mount %s is not reachable. Check host logs for errors from "
                "mount or systemd unit %s for details",
                name,
                mount.unit_name,
            )
            raise MountActivationError(name=name)

        mount.dismiss_failed_issue()

    def _add_failed_issue(self, mount: Mount) -> None:
        """Surface a failed mount as resolution issue if not already there."""
        if mount.failed_issue not in self.sys_resolution.issues:
            self.sys_resolution.add_issue(
                replace(mount.failed_issue),
                suggestions=[
                    SuggestionType.EXECUTE_RELOAD,
                    SuggestionType.EXECUTE_REMOVE,
                ],
            )

    @Job(
        name="mount_manager_relocate_local_data",
        conditions=[JobCondition.MOUNT_AVAILABLE],
        on_condition=MountJobError,
    )
    async def relocate_local_data(self, name: str) -> None:
        """Move local data out of a mount's target directory, then remount.

        Local data ends up in the mount's target directory when something
        wrote into it while the mount was not in place (e.g. an add-on
        recording to its media directory before network storage was set
        up). The data is moved to a `<name>_local_recovery` folder in a
        user-accessible location (media, share or local backup storage)
        instead of being deleted.
        """
        # Add mount name to job
        self.sys_jobs.current.reference = name

        if name not in self._mounts:
            raise MountNotFound(
                f"Cannot relocate local data for '{name}', no mount exists with that name"
            )
        mount = self._mounts[name]

        if mount.usage == MountUsage.MEDIA:
            recovery_base = self.sys_config.path_media
        elif mount.usage == MountUsage.SHARE:
            recovery_base = self.sys_config.path_share
        else:
            # The data mount directory of backup mounts is not
            # user-accessible — move the data to local backup storage,
            # which is reachable via the backup share and add-ons.
            recovery_base = self.sys_config.path_backup

        path = mount.local_where

        def move_aside() -> Path | None:
            try:
                if path.is_mount() or not path.exists():
                    return None
                if path.is_dir() and not any(path.iterdir()):
                    return None
            except OSError:
                return None

            target = recovery_base / f"{name}_local_recovery"
            counter = 1
            while target.exists():
                counter += 1
                target = recovery_base / f"{name}_local_recovery_{counter}"

            path.rename(target)
            # Keep the path present for consumers even if the remount
            # below fails: an empty directory instead of a missing one
            path.mkdir()
            return target

        try:
            target = await self.sys_run_in_executor(move_aside)
        except OSError as err:
            self.sys_resolution.check_oserror(err)
            raise MountError(
                f"Could not move local data for mount {name}: {err!s}", _LOGGER.error
            ) from err

        if target:
            _LOGGER.info(
                "Moved local data blocking mount %s from %s to %s",
                name,
                path.as_posix(),
                target.as_posix(),
            )

        # Moving again cannot help now, so drop the suggestion even if the
        # remount below fails. Detection re-adds it if local data blocks
        # the target again.
        for suggestion in self.sys_resolution.suggestions:
            if (
                suggestion.type == SuggestionType.MOVE_LOCAL_DATA
                and suggestion.context == ContextType.MOUNT
                and suggestion.reference == name
            ):
                self.sys_resolution.dismiss_suggestion(suggestion)

        await self.reload_mount(name)

    async def save_data(self) -> None:
        """Store data to configuration file."""
        self._data[ATTR_MOUNTS] = [
            mount.to_dict(skip_secrets=False) for mount in self.mounts
        ]
        await super().save_data()

    async def restore_mount(self, mount: Mount) -> asyncio.Task:
        """Restore a mount from backup.

        Adds mount to internal state without activating it.
        Returns an asyncio.Task for activating the mount in the background.
        If a mount with the same name exists, it is replaced.
        """
        if mount.name in self._mounts:
            _LOGGER.info(
                "Mount '%s' already exists, replacing with backup config", mount.name
            )
            old_mount = self._mounts[mount.name]
            await old_mount.unmount()

        self._mounts[mount.name] = mount
        return self.sys_create_task(self._activate_restored_mount(mount))

    async def _activate_restored_mount(self, mount: Mount) -> None:
        """Activate a restored mount. Logs errors but doesn't raise."""
        if HostFeature.MOUNT not in self.sys_host.features:
            _LOGGER.warning(
                "Cannot activate mount %s, mounting not supported on system",
                mount.name,
            )
            return

        try:
            _LOGGER.info("Activating restored mount: %s", mount.name)
            await mount.load()
            _LOGGER.info("Mount %s activated successfully", mount.name)
        except MountError as err:
            _LOGGER.warning(
                "Failed to activate mount %s (config was restored, "
                "mount may come online later): %s",
                mount.name,
                err,
            )
