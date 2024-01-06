"""Backup manager."""
from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Iterable
import errno
import logging
from pathlib import Path

from ..addons.addon import Addon
from ..const import (
    ATTR_DAYS_UNTIL_STALE,
    FILE_HASSIO_BACKUPS,
    FOLDER_HOMEASSISTANT,
    CoreState,
)
from ..dbus.const import UnitActiveState
from ..exceptions import AddonsError, BackupError, BackupInvalidError, BackupJobError
from ..jobs.const import JOB_GROUP_BACKUP_MANAGER, JobCondition, JobExecutionLimit
from ..jobs.decorator import Job
from ..jobs.job_group import JobGroup
from ..mounts.mount import Mount
from ..resolution.const import UnhealthyReason
from ..utils.common import FileConfiguration
from ..utils.dt import utcnow
from ..utils.sentinel import DEFAULT
from ..utils.sentry import capture_exception
from .backup import Backup
from .const import DEFAULT_FREEZE_TIMEOUT, BackupJobStage, BackupType, RestoreJobStage
from .utils import create_slug
from .validate import ALL_FOLDERS, SCHEMA_BACKUPS_CONFIG

_LOGGER: logging.Logger = logging.getLogger(__name__)


class BackupManager(FileConfiguration, JobGroup):
    """Manage backups."""

    def __init__(self, coresys):
        """Initialize a backup manager."""
        super().__init__(FILE_HASSIO_BACKUPS, SCHEMA_BACKUPS_CONFIG)
        super(FileConfiguration, self).__init__(coresys, JOB_GROUP_BACKUP_MANAGER)
        self._backups: dict[str, Backup] = {}
        self._thaw_task: Awaitable[None] | None = None
        self._thaw_event: asyncio.Event = asyncio.Event()

    @property
    def list_backups(self) -> set[Backup]:
        """Return a list of all backup objects."""
        return set(self._backups.values())

    @property
    def days_until_stale(self) -> int:
        """Get days until backup is considered stale."""
        return self._data[ATTR_DAYS_UNTIL_STALE]

    @days_until_stale.setter
    def days_until_stale(self, value: int) -> None:
        """Set days until backup is considered stale."""
        self._data[ATTR_DAYS_UNTIL_STALE] = value

    @property
    def backup_locations(self) -> list[Path]:
        """List of locations containing backups."""
        return [self.sys_config.path_backup] + [
            mount.local_where
            for mount in self.sys_mounts.backup_mounts
            if mount.state == UnitActiveState.ACTIVE
        ]

    def get(self, slug: str) -> Backup:
        """Return backup object."""
        return self._backups.get(slug)

    def _get_base_path(self, location: Mount | type[DEFAULT] | None = DEFAULT) -> Path:
        """Get base path for backup using location or default location."""
        if location:
            return location.local_where

        if location == DEFAULT and self.sys_mounts.default_backup_mount:
            return self.sys_mounts.default_backup_mount.local_where

        return self.sys_config.path_backup

    def _change_stage(
        self,
        stage: BackupJobStage | RestoreJobStage,
        backup: Backup | None = None,
    ):
        """Change the stage of the current job during backup/restore.

        Must be called from an existing backup/restore job.
        """
        job_name = self.sys_jobs.current.name
        if "restore" in job_name:
            action = "Restore"
        elif "freeze" in job_name:
            action = "Freeze"
        elif "thaw" in job_name:
            action = "Thaw"
        else:
            action = "Backup"

        _LOGGER.info(
            "%s %sstarting stage %s",
            action,
            f"{backup.slug} " if backup else "",
            stage,
        )
        self.sys_jobs.current.stage = stage

    def _list_backup_files(self, path: Path) -> Iterable[Path]:
        """Return iterable of backup files, suppress and log OSError for network mounts."""
        try:
            # is_dir does a stat syscall which raises if the mount is down
            if path.is_dir():
                return path.glob("*.tar")
        except OSError as err:
            if err.errno == errno.EBADMSG and path == self.sys_config.path_backup:
                self.sys_resolution.unhealthy = UnhealthyReason.OSERROR_BAD_MESSAGE
            _LOGGER.error("Could not list backups from %s: %s", path.as_posix(), err)

        return []

    def _create_backup(
        self,
        name: str,
        sys_type: BackupType,
        password: str | None,
        compressed: bool = True,
        location: Mount | type[DEFAULT] | None = DEFAULT,
    ) -> Backup:
        """Initialize a new backup object from name.

        Must be called from an existing backup job.
        """
        date_str = utcnow().isoformat()
        slug = create_slug(name, date_str)
        tar_file = Path(self._get_base_path(location), f"{slug}.tar")

        # init object
        backup = Backup(self.coresys, tar_file, slug)
        backup.new(name, date_str, sys_type, password, compressed)

        # Add backup ID to job
        self.sys_jobs.current.reference = backup.slug

        self._change_stage(BackupJobStage.ADDON_REPOSITORIES, backup)
        backup.store_repositories()
        self._change_stage(BackupJobStage.DOCKER_CONFIG, backup)
        backup.store_dockerconfig()

        return backup

    def load(self) -> Awaitable[None]:
        """Load exists backups data.

        Return a coroutine.
        """
        return self.reload()

    async def reload(self) -> None:
        """Load exists backups."""
        self._backups = {}

        async def _load_backup(tar_file):
            """Load the backup."""
            backup = Backup(self.coresys, tar_file, "temp")
            if await backup.load():
                self._backups[backup.slug] = Backup(
                    self.coresys, tar_file, backup.slug, backup.data
                )

        tasks = [
            self.sys_create_task(_load_backup(tar_file))
            for path in self.backup_locations
            for tar_file in self._list_backup_files(path)
        ]

        _LOGGER.info("Found %d backup files", len(tasks))
        if tasks:
            await asyncio.wait(tasks)

    def remove(self, backup: Backup) -> bool:
        """Remove a backup."""
        try:
            backup.tarfile.unlink()
            self._backups.pop(backup.slug, None)
            _LOGGER.info("Removed backup file %s", backup.slug)

        except OSError as err:
            if (
                err.errno == errno.EBADMSG
                and backup.tarfile.parent == self.sys_config.path_backup
            ):
                self.sys_resolution.unhealthy = UnhealthyReason.OSERROR_BAD_MESSAGE
            _LOGGER.error("Can't remove backup %s: %s", backup.slug, err)
            return False

        return True

    async def import_backup(self, tar_file: Path) -> Backup | None:
        """Check backup tarfile and import it."""
        backup = Backup(self.coresys, tar_file, "temp")

        # Read meta data
        if not await backup.load():
            return None

        # Already exists?
        if backup.slug in self._backups:
            _LOGGER.warning("Backup %s already exists! overwriting", backup.slug)
            self.remove(self.get(backup.slug))

        # Move backup to backup
        tar_origin = Path(self.sys_config.path_backup, f"{backup.slug}.tar")
        try:
            backup.tarfile.rename(tar_origin)

        except OSError as err:
            if err.errno == errno.EBADMSG:
                self.sys_resolution.unhealthy = UnhealthyReason.OSERROR_BAD_MESSAGE
            _LOGGER.error("Can't move backup file to storage: %s", err)
            return None

        # Load new backup
        backup = Backup(self.coresys, tar_origin, backup.slug, backup.data)
        if not await backup.load():
            return None
        _LOGGER.info("Successfully imported %s", backup.slug)

        self._backups[backup.slug] = backup
        return backup

    async def _do_backup(
        self,
        backup: Backup,
        addon_list: list[Addon],
        folder_list: list[str],
        homeassistant: bool,
        homeassistant_exclude_database: bool | None,
    ) -> Backup | None:
        """Create a backup.

        Must be called from an existing backup job.
        """
        addon_start_tasks: list[Awaitable[None]] | None = None

        try:
            self.sys_core.state = CoreState.FREEZE

            async with backup:
                # Backup add-ons
                if addon_list:
                    self._change_stage(BackupJobStage.ADDONS, backup)
                    addon_start_tasks = await backup.store_addons(addon_list)

                # HomeAssistant Folder is for v1
                if homeassistant:
                    self._change_stage(BackupJobStage.HOME_ASSISTANT, backup)
                    await backup.store_homeassistant(
                        self.sys_homeassistant.backups_exclude_database
                        if homeassistant_exclude_database is None
                        else homeassistant_exclude_database
                    )

                # Backup folders
                if folder_list:
                    self._change_stage(BackupJobStage.FOLDERS, backup)
                    await backup.store_folders(folder_list)

                self._change_stage(BackupJobStage.FINISHING_FILE, backup)

        except BackupError as err:
            self.sys_jobs.current.capture_error(err)
            return None
        except Exception as err:  # pylint: disable=broad-except
            _LOGGER.exception("Backup %s error", backup.slug)
            capture_exception(err)
            self.sys_jobs.current.capture_error(
                BackupError(f"Backup {backup.slug} error, see supervisor logs")
            )
            return None
        else:
            self._backups[backup.slug] = backup

            if addon_start_tasks:
                self._change_stage(BackupJobStage.AWAIT_ADDON_RESTARTS, backup)
                # Ignore exceptions from waiting for addon startup, addon errors handled elsewhere
                await asyncio.gather(*addon_start_tasks, return_exceptions=True)

            return backup
        finally:
            self.sys_core.state = CoreState.RUNNING

    @Job(
        name="backup_manager_full_backup",
        conditions=[JobCondition.RUNNING],
        limit=JobExecutionLimit.GROUP_ONCE,
        on_condition=BackupJobError,
    )
    async def do_backup_full(
        self,
        name: str = "",
        password: str | None = None,
        compressed: bool = True,
        location: Mount | type[DEFAULT] | None = DEFAULT,
        homeassistant_exclude_database: bool | None = None,
    ) -> Backup | None:
        """Create a full backup."""
        if self._get_base_path(location) == self.sys_config.path_backup:
            await Job.check_conditions(
                self, {JobCondition.FREE_SPACE}, "BackupManager.do_backup_full"
            )

        backup = self._create_backup(
            name, BackupType.FULL, password, compressed, location
        )

        _LOGGER.info("Creating new full backup with slug %s", backup.slug)
        backup = await self._do_backup(
            backup,
            self.sys_addons.installed,
            ALL_FOLDERS,
            True,
            homeassistant_exclude_database,
        )
        if backup:
            _LOGGER.info("Creating full backup with slug %s completed", backup.slug)
        return backup

    @Job(
        name="backup_manager_partial_backup",
        conditions=[JobCondition.RUNNING],
        limit=JobExecutionLimit.GROUP_ONCE,
        on_condition=BackupJobError,
    )
    async def do_backup_partial(
        self,
        name: str = "",
        addons: list[str] | None = None,
        folders: list[str] | None = None,
        password: str | None = None,
        homeassistant: bool = False,
        compressed: bool = True,
        location: Mount | type[DEFAULT] | None = DEFAULT,
        homeassistant_exclude_database: bool | None = None,
    ) -> Backup | None:
        """Create a partial backup."""
        if self._get_base_path(location) == self.sys_config.path_backup:
            await Job.check_conditions(
                self, {JobCondition.FREE_SPACE}, "BackupManager.do_backup_partial"
            )

        addons = addons or []
        folders = folders or []

        # HomeAssistant Folder is for v1
        if FOLDER_HOMEASSISTANT in folders:
            folders.remove(FOLDER_HOMEASSISTANT)
            homeassistant = True

        if len(addons) == 0 and len(folders) == 0 and not homeassistant:
            _LOGGER.error("Nothing to create backup for")

        backup = self._create_backup(
            name, BackupType.PARTIAL, password, compressed, location
        )

        _LOGGER.info("Creating new partial backup with slug %s", backup.slug)
        addon_list = []
        for addon_slug in addons:
            addon = self.sys_addons.get(addon_slug)
            if addon and addon.is_installed:
                addon_list.append(addon)
                continue
            _LOGGER.warning("Add-on %s not found/installed", addon_slug)

        backup = await self._do_backup(
            backup, addon_list, folders, homeassistant, homeassistant_exclude_database
        )
        if backup:
            _LOGGER.info("Creating partial backup with slug %s completed", backup.slug)
        return backup

    async def _do_restore(
        self,
        backup: Backup,
        addon_list: list[str],
        folder_list: list[str],
        homeassistant: bool,
        replace: bool,
    ) -> bool:
        """Restore from a backup.

        Must be called from an existing restore job.
        """
        addon_start_tasks: list[Awaitable[None]] | None = None
        success = True

        try:
            task_hass: asyncio.Task | None = None
            async with backup:
                # Restore docker config
                self._change_stage(RestoreJobStage.DOCKER_CONFIG, backup)
                backup.restore_dockerconfig(replace)

                # Process folders
                if folder_list:
                    self._change_stage(RestoreJobStage.FOLDERS, backup)
                    success = await backup.restore_folders(folder_list)

                # Process Home-Assistant
                if homeassistant:
                    self._change_stage(RestoreJobStage.HOME_ASSISTANT, backup)
                    task_hass = await backup.restore_homeassistant()

                # Delete delta add-ons
                if replace:
                    self._change_stage(RestoreJobStage.REMOVE_DELTA_ADDONS, backup)
                    for addon in self.sys_addons.installed:
                        if addon.slug in backup.addon_list:
                            continue

                        # Remove Add-on because it's not a part of the new env
                        # Do it sequential avoid issue on slow IO
                        try:
                            await self.sys_addons.uninstall(addon.slug)
                        except AddonsError:
                            _LOGGER.warning("Can't uninstall Add-on %s", addon.slug)
                            success = False

                if addon_list:
                    self._change_stage(RestoreJobStage.ADDON_REPOSITORIES, backup)
                    await backup.restore_repositories(replace)

                    self._change_stage(RestoreJobStage.ADDONS, backup)
                    restore_success, addon_start_tasks = await backup.restore_addons(
                        addon_list
                    )
                    success = success and restore_success

                # Wait for Home Assistant Core update/downgrade
                if task_hass:
                    self._change_stage(
                        RestoreJobStage.AWAIT_HOME_ASSISTANT_RESTART, backup
                    )
                    await task_hass
        except BackupError:
            raise
        except Exception as err:  # pylint: disable=broad-except
            _LOGGER.exception("Restore %s error", backup.slug)
            capture_exception(err)
            raise BackupError(
                f"Restore {backup.slug} error, see supervisor logs"
            ) from err
        else:
            if addon_start_tasks:
                self._change_stage(RestoreJobStage.AWAIT_ADDON_RESTARTS, backup)
                # Failure to resume addons post restore is still a restore failure
                if any(
                    await asyncio.gather(*addon_start_tasks, return_exceptions=True)
                ):
                    return False

            return success
        finally:
            # Leave Home Assistant alone if it wasn't part of the restore
            if homeassistant:
                self._change_stage(RestoreJobStage.CHECK_HOME_ASSISTANT, backup)

                # Do we need start Home Assistant Core?
                if not await self.sys_homeassistant.core.is_running():
                    await self.sys_homeassistant.core.start()

                # Check If we can access to API / otherwise restart
                if not await self.sys_homeassistant.api.check_api_state():
                    _LOGGER.warning("Need restart HomeAssistant for API")
                    await self.sys_homeassistant.core.restart()

    @Job(
        name="backup_manager_full_restore",
        conditions=[
            JobCondition.FREE_SPACE,
            JobCondition.HEALTHY,
            JobCondition.INTERNET_HOST,
            JobCondition.INTERNET_SYSTEM,
            JobCondition.RUNNING,
        ],
        limit=JobExecutionLimit.GROUP_ONCE,
        on_condition=BackupJobError,
    )
    async def do_restore_full(
        self, backup: Backup, password: str | None = None
    ) -> bool:
        """Restore a backup."""
        # Add backup ID to job
        self.sys_jobs.current.reference = backup.slug

        if backup.sys_type != BackupType.FULL:
            raise BackupInvalidError(
                f"{backup.slug} is only a partial backup!", _LOGGER.error
            )

        if backup.protected and not backup.set_password(password):
            raise BackupInvalidError(
                f"Invalid password for backup {backup.slug}", _LOGGER.error
            )

        if backup.supervisor_version > self.sys_supervisor.version:
            raise BackupInvalidError(
                f"Backup was made on supervisor version {backup.supervisor_version}, "
                f"can't restore on {self.sys_supervisor.version}. Must update supervisor first.",
                _LOGGER.error,
            )

        _LOGGER.info("Full-Restore %s start", backup.slug)
        self.sys_core.state = CoreState.FREEZE

        try:
            # Stop Home-Assistant / Add-ons
            await self.sys_core.shutdown()

            success = await self._do_restore(
                backup, backup.addon_list, backup.folders, True, True
            )
        finally:
            self.sys_core.state = CoreState.RUNNING

        if success:
            _LOGGER.info("Full-Restore %s done", backup.slug)
        return success

    @Job(
        name="backup_manager_partial_restore",
        conditions=[
            JobCondition.FREE_SPACE,
            JobCondition.HEALTHY,
            JobCondition.INTERNET_HOST,
            JobCondition.INTERNET_SYSTEM,
            JobCondition.RUNNING,
        ],
        limit=JobExecutionLimit.GROUP_ONCE,
        on_condition=BackupJobError,
    )
    async def do_restore_partial(
        self,
        backup: Backup,
        homeassistant: bool = False,
        addons: list[str] | None = None,
        folders: list[Path] | None = None,
        password: str | None = None,
    ) -> bool:
        """Restore a backup."""
        # Add backup ID to job
        self.sys_jobs.current.reference = backup.slug

        addon_list = addons or []
        folder_list = folders or []

        # Version 1
        if FOLDER_HOMEASSISTANT in folder_list:
            folder_list.remove(FOLDER_HOMEASSISTANT)
            homeassistant = True

        if backup.protected and not backup.set_password(password):
            raise BackupInvalidError(
                f"Invalid password for backup {backup.slug}", _LOGGER.error
            )

        if backup.homeassistant is None and homeassistant:
            raise BackupInvalidError(
                "No Home Assistant Core data inside the backup", _LOGGER.error
            )

        if backup.supervisor_version > self.sys_supervisor.version:
            raise BackupInvalidError(
                f"Backup was made on supervisor version {backup.supervisor_version}, "
                f"can't restore on {self.sys_supervisor.version}. Must update supervisor first.",
                _LOGGER.error,
            )

        _LOGGER.info("Partial-Restore %s start", backup.slug)
        self.sys_core.state = CoreState.FREEZE

        try:
            success = await self._do_restore(
                backup, addon_list, folder_list, homeassistant, False
            )
        finally:
            self.sys_core.state = CoreState.RUNNING

        if success:
            _LOGGER.info("Partial-Restore %s done", backup.slug)
        return success

    @Job(
        name="backup_manager_freeze_all",
        conditions=[JobCondition.RUNNING],
        limit=JobExecutionLimit.GROUP_ONCE,
        on_condition=BackupJobError,
    )
    async def freeze_all(self, timeout: float = DEFAULT_FREEZE_TIMEOUT) -> None:
        """Freeze system to prepare for an external backup such as an image snapshot."""
        self.sys_core.state = CoreState.FREEZE

        # Determine running addons
        installed = self.sys_addons.installed.copy()
        is_running: list[bool] = await asyncio.gather(
            *[addon.is_running() for addon in installed]
        )
        running_addons = [
            installed[ind] for ind in range(len(installed)) if is_running[ind]
        ]

        # Create thaw task first to ensure we eventually undo freezes even if the below fails
        self._thaw_task = asyncio.shield(
            self.sys_create_task(self._thaw_all(running_addons, timeout))
        )

        # Tell Home Assistant to freeze for a backup
        self._change_stage(BackupJobStage.HOME_ASSISTANT)
        await self.sys_homeassistant.begin_backup()

        # Run all pre-backup tasks for addons
        self._change_stage(BackupJobStage.ADDONS)
        await asyncio.gather(*[addon.begin_backup() for addon in running_addons])

    @Job(
        name="backup_manager_thaw_all",
        conditions=[JobCondition.FROZEN],
        on_condition=BackupJobError,
    )
    async def _thaw_all(
        self, running_addons: list[Addon], timeout: float = DEFAULT_FREEZE_TIMEOUT
    ) -> None:
        """Thaw system after user signal or timeout."""
        try:
            try:
                await asyncio.wait_for(self._thaw_event.wait(), timeout)
            except TimeoutError:
                _LOGGER.warning(
                    "Timeout waiting for signal to thaw after manual freeze, beginning thaw now"
                )

            self._change_stage(BackupJobStage.HOME_ASSISTANT)
            await self.sys_homeassistant.end_backup()

            self._change_stage(BackupJobStage.ADDONS)
            addon_start_tasks: list[asyncio.Task] = [
                task
                for task in await asyncio.gather(
                    *[addon.end_backup() for addon in running_addons]
                )
                if task
            ]
        finally:
            self.sys_core.state = CoreState.RUNNING
            self._thaw_event.clear()
            self._thaw_task = None

        if addon_start_tasks:
            self._change_stage(BackupJobStage.AWAIT_ADDON_RESTARTS)
            await asyncio.gather(*addon_start_tasks, return_exceptions=True)

    @Job(
        name="backup_manager_signal_thaw",
        conditions=[JobCondition.FROZEN],
        limit=JobExecutionLimit.GROUP_ONCE,
        on_condition=BackupJobError,
        internal=True,
    )
    async def thaw_all(self) -> None:
        """Signal thaw task to begin unfreezing the system."""
        if not self._thaw_task:
            raise BackupError(
                "Freeze was not initiated by freeze API, cannot thaw this way"
            )

        self._thaw_event.set()
        await self._thaw_task
