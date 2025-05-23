"""Backup manager."""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable
import errno
import logging
from pathlib import Path
from shutil import copy
from typing import cast

from ..addons.addon import Addon
from ..const import (
    ATTR_DAYS_UNTIL_STALE,
    FILE_HASSIO_BACKUPS,
    FOLDER_HOMEASSISTANT,
    CoreState,
)
from ..coresys import CoreSys
from ..dbus.const import UnitActiveState
from ..exceptions import (
    BackupDataDiskBadMessageError,
    BackupError,
    BackupFileNotFoundError,
    BackupInvalidError,
    BackupJobError,
    BackupMountDownError,
)
from ..jobs.const import JOB_GROUP_BACKUP_MANAGER, JobCondition, JobExecutionLimit
from ..jobs.decorator import Job
from ..jobs.job_group import JobGroup
from ..mounts.mount import Mount
from ..resolution.const import UnhealthyReason
from ..utils.common import FileConfiguration
from ..utils.dt import utcnow
from ..utils.sentinel import DEFAULT
from ..utils.sentry import async_capture_exception
from .backup import Backup, BackupLocation
from .const import (
    DEFAULT_FREEZE_TIMEOUT,
    LOCATION_CLOUD_BACKUP,
    LOCATION_TYPE,
    BackupJobStage,
    BackupType,
    RestoreJobStage,
)
from .utils import create_slug
from .validate import ALL_FOLDERS, SCHEMA_BACKUPS_CONFIG

_LOGGER: logging.Logger = logging.getLogger(__name__)

JOB_FULL_RESTORE = "backup_manager_full_restore"
JOB_PARTIAL_RESTORE = "backup_manager_partial_restore"


class BackupManager(FileConfiguration, JobGroup):
    """Manage backups."""

    def __init__(self, coresys: CoreSys):
        """Initialize a backup manager."""
        super().__init__(FILE_HASSIO_BACKUPS, SCHEMA_BACKUPS_CONFIG)
        super(FileConfiguration, self).__init__(coresys, JOB_GROUP_BACKUP_MANAGER)
        self._backups: dict[str, Backup] = {}
        self._thaw_task: Awaitable[None] | None = None
        self._thaw_event: asyncio.Event = asyncio.Event()

    @property
    def list_backups(self) -> list[Backup]:
        """Return a list of all backup objects."""
        return list(self._backups.values())

    @property
    def days_until_stale(self) -> int:
        """Get days until backup is considered stale."""
        return self._data[ATTR_DAYS_UNTIL_STALE]

    @days_until_stale.setter
    def days_until_stale(self, value: int) -> None:
        """Set days until backup is considered stale."""
        self._data[ATTR_DAYS_UNTIL_STALE] = value

    @property
    def backup_locations(self) -> dict[str | None, Path]:
        """List of locations containing backups."""
        return {
            None: self.sys_config.path_backup,
            LOCATION_CLOUD_BACKUP: self.sys_config.path_core_backup,
        } | {
            mount.name: mount.local_where
            for mount in self.sys_mounts.backup_mounts
            if mount.state == UnitActiveState.ACTIVE and mount.local_where
        }

    @property
    def current_restore(self) -> str | None:
        """Return id of current restore job if a restore job is in progress."""
        job = self.sys_jobs.current
        while job.parent_id:
            job = self.sys_jobs.get_job(job.parent_id)
            if job.name in {JOB_FULL_RESTORE, JOB_PARTIAL_RESTORE}:
                return job.uuid
        return None

    def get(self, slug: str) -> Backup | None:
        """Return backup object."""
        return self._backups.get(slug)

    def _get_base_path(
        self,
        location: LOCATION_TYPE | type[DEFAULT] = DEFAULT,
    ) -> Path:
        """Get base path for backup using location or default location."""
        if location == LOCATION_CLOUD_BACKUP:
            return self.sys_config.path_core_backup

        if location == DEFAULT and self.sys_mounts.default_backup_mount:
            location = self.sys_mounts.default_backup_mount

        if location:
            return cast(Mount, location).local_where

        return self.sys_config.path_backup

    async def get_upload_path_for_location(self, location: LOCATION_TYPE) -> Path:
        """Get a path (temporary) upload path for a backup location."""
        target_path = self._get_base_path(location)

        # Return target path for mounts since tmp will always be local, mounts
        # will never be the same device.
        if location is not None and location != LOCATION_CLOUD_BACKUP:
            return target_path

        tmp_path = self.sys_config.path_tmp

        def check_same_mount() -> bool:
            """Check if the target path is on the same mount as the backup location."""
            return target_path.stat().st_dev == tmp_path.stat().st_dev

        if await self.sys_run_in_executor(check_same_mount):
            return tmp_path
        return target_path

    async def _check_location(self, location: LOCATION_TYPE | type[DEFAULT] = DEFAULT):
        """Check if backup location is accessible."""
        if location == DEFAULT and self.sys_mounts.default_backup_mount:
            location = self.sys_mounts.default_backup_mount

        if (
            location not in (DEFAULT, LOCATION_CLOUD_BACKUP, None)
            and not await (location_mount := cast(Mount, location)).is_mounted()
        ):
            raise BackupMountDownError(
                f"{location_mount.name} is down, cannot back-up to it",
                _LOGGER.error,
            )

    def _get_location_name(
        self,
        location: LOCATION_TYPE | type[DEFAULT] = DEFAULT,
    ) -> str | None:
        """Get name of location (or None for local backup folder)."""
        if location == LOCATION_CLOUD_BACKUP:
            return cast(str, location)

        if location == DEFAULT and self.sys_mounts.default_backup_mount:
            location = self.sys_mounts.default_backup_mount

        if location:
            return cast(Mount, location).name
        return None

    def _change_stage(
        self,
        stage: BackupJobStage | RestoreJobStage,
        backup: Backup | None = None,
    ):
        """Change the stage of the current job during backup/restore.

        Must be called from an existing backup/restore job.
        """
        job_name = cast(str, self.sys_jobs.current.name)
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

    async def _list_backup_files(self, path: Path) -> list[Path]:
        """Return iterable of backup files, suppress and log OSError for network mounts."""

        def find_backups() -> list[Path]:
            # is_dir does a stat syscall which raises if the mount is down
            # Returning an iterator causes I/O while iterating, coerce into list here
            if path.is_dir():
                return list(path.glob("*.tar"))
            return []

        try:
            return await self.sys_run_in_executor(find_backups)
        except OSError as err:
            if err.errno == errno.EBADMSG and path in {
                self.sys_config.path_backup,
                self.sys_config.path_core_backup,
            }:
                self.sys_resolution.add_unhealthy_reason(
                    UnhealthyReason.OSERROR_BAD_MESSAGE
                )
            _LOGGER.error("Could not list backups from %s: %s", path.as_posix(), err)

        return []

    def _create_backup(
        self,
        name: str,
        filename: str | None,
        sys_type: BackupType,
        password: str | None,
        compressed: bool = True,
        location: LOCATION_TYPE | type[DEFAULT] = DEFAULT,
        extra: dict | None = None,
    ) -> Backup:
        """Initialize a new backup object from name.

        Must be called from an existing backup job.
        """
        date_str = utcnow().isoformat()
        slug = create_slug(name, date_str)

        if filename:
            tar_file = Path(self._get_base_path(location), Path(filename).name)
        else:
            tar_file = Path(self._get_base_path(location), f"{slug}.tar")

        # init object
        backup = Backup(self.coresys, tar_file, slug, self._get_location_name(location))
        backup.new(name, date_str, sys_type, password, compressed, extra)

        # Add backup ID to job
        self.sys_jobs.current.reference = backup.slug

        self._change_stage(BackupJobStage.ADDON_REPOSITORIES, backup)
        backup.store_repositories()

        return backup

    async def load(self) -> None:
        """Load exists backups data."""
        await self.reload()

    async def reload(self, location: str | None | type[DEFAULT] = DEFAULT) -> bool:
        """Load exists backups."""

        backups: dict[str, Backup] = {}

        async def _load_backup(location_name: str | None, tar_file: Path) -> bool:
            """Load the backup."""
            backup = Backup(self.coresys, tar_file, "temp", location_name)
            if await backup.load():
                if backup.slug in backups:
                    try:
                        backups[backup.slug].consolidate(backup)
                    except BackupInvalidError as err:
                        _LOGGER.error(
                            "Ignoring backup %s in %s due to: %s",
                            backup.slug,
                            backup.location,
                            err,
                        )
                        return False

                else:
                    backups[backup.slug] = Backup(
                        self.coresys,
                        tar_file,
                        backup.slug,
                        location_name,
                        backup.data,
                        backup.size_bytes,
                    )
                return True

            return False

        # This is just so we don't have to cast repeatedly. Variable will only be used when location is not DEFAULT
        location_name = "" if location == DEFAULT else cast(str | None, location)
        locations = (
            self.backup_locations
            if location == DEFAULT
            else {location_name: self.backup_locations[location_name]}
        )
        tasks = [
            self.sys_create_task(_load_backup(_location, tar_file))
            for _location, path in locations.items()
            for tar_file in await self._list_backup_files(path)
        ]

        _LOGGER.info("Found %d backup files", len(tasks))
        if tasks:
            await asyncio.wait(tasks)

        # For a full reload, replace our cache with new one
        if location == DEFAULT:
            self._backups = backups
            return True

        # For a location reload, merge new cache in with existing
        for backup in list(self.list_backups):
            if backup.slug in backups:
                try:
                    backup.consolidate(backups[backup.slug])
                except BackupInvalidError as err:
                    _LOGGER.error(
                        "Ignoring backup %s in %s due to: %s",
                        backup.slug,
                        location,
                        err,
                    )

            elif location_name in backup.all_locations:
                if len(backup.all_locations) > 1:
                    del backup.all_locations[location_name]
                else:
                    del self._backups[backup.slug]

        return True

    async def remove(
        self,
        backup: Backup,
        locations: list[LOCATION_TYPE] | None = None,
    ):
        """Remove a backup."""
        targets = (
            [
                location_name
                for location in locations
                if (location_name := self._get_location_name(location))
                in backup.all_locations
            ]
            if locations
            else list(backup.all_locations.keys())
        )
        for location in targets:
            backup_tarfile = backup.all_locations[location].path
            try:
                await self.sys_run_in_executor(backup_tarfile.unlink)
                del backup.all_locations[location]
            except FileNotFoundError as err:
                self.sys_create_task(self.reload(location))
                raise BackupFileNotFoundError(
                    f"Cannot delete backup at {backup_tarfile.as_posix()}, file does not exist!",
                    _LOGGER.error,
                ) from err
            except OSError as err:
                msg = f"Could delete backup at {backup_tarfile.as_posix()}: {err!s}"
                if err.errno == errno.EBADMSG and location in {
                    None,
                    LOCATION_CLOUD_BACKUP,
                }:
                    self.sys_resolution.add_unhealthy_reason(
                        UnhealthyReason.OSERROR_BAD_MESSAGE
                    )
                raise BackupError(msg, _LOGGER.error) from err

        # If backup has been removed from all locations, remove it from cache
        if not backup.all_locations:
            del self._backups[backup.slug]

    @Job(name="backup_copy_to_location", cleanup=False)
    async def _copy_to_location(
        self, backup: Backup, location: LOCATION_TYPE
    ) -> tuple[str | None, Path]:
        """Copy a backup file to the default location."""
        location_name = location.name if isinstance(location, Mount) else location
        self.sys_jobs.current.reference = location_name
        try:
            if location == LOCATION_CLOUD_BACKUP:
                destination = self.sys_config.path_core_backup
            elif location:
                location_mount = cast(Mount, location)
                if not location_mount.local_where.is_mount():
                    raise BackupMountDownError(
                        f"{location_mount.name} is down, cannot copy to it",
                        _LOGGER.error,
                    )
                destination = location_mount.local_where
            else:
                destination = self.sys_config.path_backup

            path = await self.sys_run_in_executor(copy, backup.tarfile, destination)
            return (location_name, Path(path))
        except OSError as err:
            msg = f"Could not copy backup to {location_name} due to: {err!s}"

            if err.errno == errno.EBADMSG and location in {
                LOCATION_CLOUD_BACKUP,
                None,
            }:
                raise BackupDataDiskBadMessageError(msg, _LOGGER.error) from err
            raise BackupError(msg, _LOGGER.error) from err

    @Job(name="backup_copy_to_additional_locations", cleanup=False)
    async def _copy_to_additional_locations(
        self,
        backup: Backup,
        locations: list[LOCATION_TYPE],
    ):
        """Copy a backup file to additional locations."""
        all_new_locations: dict[str | None, Path] = {}
        for location in locations:
            try:
                location_name, path = await self._copy_to_location(backup, location)
                all_new_locations[location_name] = path
            except BackupDataDiskBadMessageError as err:
                self.sys_resolution.add_unhealthy_reason(
                    UnhealthyReason.OSERROR_BAD_MESSAGE
                )
                self.sys_jobs.current.capture_error(err)
            except BackupError as err:
                self.sys_jobs.current.capture_error(err)

        backup.all_locations.update(
            {
                loc: BackupLocation(
                    path=path,
                    protected=backup.protected,
                    size_bytes=backup.size_bytes,
                )
                for loc, path in all_new_locations.items()
            }
        )

    @Job(name="backup_manager_import_backup")
    async def import_backup(
        self,
        tar_file: Path,
        filename: str | None = None,
        location: LOCATION_TYPE = None,
        additional_locations: list[LOCATION_TYPE] | None = None,
    ) -> Backup | None:
        """Check backup tarfile and import it."""
        await self._check_location(location)

        backup = Backup(self.coresys, tar_file, "temp", None)

        # Read meta data
        if not await backup.load():
            return None

        # Move backup to destination folder
        if filename:
            tar_file = Path(self._get_base_path(location), Path(filename).name)
        else:
            tar_file = Path(self._get_base_path(location), f"{backup.slug}.tar")

        try:
            await self.sys_run_in_executor(backup.tarfile.rename, tar_file)
        except OSError as err:
            if err.errno == errno.EBADMSG and location in {LOCATION_CLOUD_BACKUP, None}:
                self.sys_resolution.add_unhealthy_reason(
                    UnhealthyReason.OSERROR_BAD_MESSAGE
                )
            _LOGGER.error("Can't move backup file to storage: %s", err)
            return None

        # Load new backup
        backup = Backup(
            self.coresys,
            tar_file,
            backup.slug,
            self._get_location_name(location),
            backup.data,
        )
        if not await backup.load():
            # Remove invalid backup from location it was moved to
            await self.sys_run_in_executor(backup.tarfile.unlink)
            return None
        _LOGGER.info("Successfully imported %s", backup.slug)

        # Already exists?
        if (
            backup.slug in self._backups
            and backup.all_locations != self._backups[backup.slug].all_locations
        ):
            _LOGGER.warning("Backup %s already exists! consolidating", backup.slug)
            try:
                self._backups[backup.slug].consolidate(backup)
            except BackupInvalidError as err:
                backup.tarfile.unlink()
                raise BackupInvalidError(
                    f"Cannot import backup {backup.slug} due to: {err!s}", _LOGGER.error
                ) from err
        else:
            self._backups[backup.slug] = backup

        if additional_locations:
            await self._copy_to_additional_locations(backup, additional_locations)

        return backup

    async def _do_backup(
        self,
        backup: Backup,
        addon_list: list[Addon],
        folder_list: list[str],
        homeassistant: bool,
        homeassistant_exclude_database: bool | None,
        additional_locations: list[LOCATION_TYPE] | None = None,
    ) -> Backup | None:
        """Create a backup.

        Must be called from an existing backup job. If the backup failed, the
        backup file is being deleted and None is returned.
        """
        addon_start_tasks: list[Awaitable[None]] | None = None

        try:
            await self.sys_core.set_state(CoreState.FREEZE)

            async with backup.create():
                # HomeAssistant Folder is for v1
                if homeassistant:
                    self._change_stage(BackupJobStage.HOME_ASSISTANT, backup)
                    await backup.store_homeassistant(
                        self.sys_homeassistant.backups_exclude_database
                        if homeassistant_exclude_database is None
                        else homeassistant_exclude_database
                    )

                # Backup add-ons
                if addon_list:
                    self._change_stage(BackupJobStage.ADDONS, backup)
                    addon_start_tasks = await backup.store_addons(addon_list)

                # Backup folders
                if folder_list:
                    self._change_stage(BackupJobStage.FOLDERS, backup)
                    await backup.store_folders(folder_list)

                self._change_stage(BackupJobStage.FINISHING_FILE, backup)

        except BackupError as err:
            await self.sys_run_in_executor(backup.tarfile.unlink, missing_ok=True)
            _LOGGER.error("Backup %s error: %s", backup.slug, err)
            self.sys_jobs.current.capture_error(err)
            return None
        except Exception as err:  # pylint: disable=broad-except
            await self.sys_run_in_executor(backup.tarfile.unlink, missing_ok=True)
            _LOGGER.exception("Backup %s error", backup.slug)
            await async_capture_exception(err)
            self.sys_jobs.current.capture_error(
                BackupError(f"Backup {backup.slug} error, see supervisor logs")
            )
            return None
        else:
            self._backups[backup.slug] = backup

            if additional_locations:
                self._change_stage(BackupJobStage.COPY_ADDITONAL_LOCATIONS, backup)
                await self._copy_to_additional_locations(backup, additional_locations)

            if addon_start_tasks:
                self._change_stage(BackupJobStage.AWAIT_ADDON_RESTARTS, backup)
                # Ignore exceptions from waiting for addon startup, addon errors handled elsewhere
                await asyncio.gather(*addon_start_tasks, return_exceptions=True)

            return backup
        finally:
            await self.sys_core.set_state(CoreState.RUNNING)

    @Job(
        name="backup_manager_full_backup",
        conditions=[JobCondition.RUNNING],
        limit=JobExecutionLimit.GROUP_ONCE,
        on_condition=BackupJobError,
        cleanup=False,
    )
    async def do_backup_full(
        self,
        name: str = "",
        filename: str | None = None,
        *,
        password: str | None = None,
        compressed: bool = True,
        location: LOCATION_TYPE | type[DEFAULT] = DEFAULT,
        homeassistant_exclude_database: bool | None = None,
        extra: dict | None = None,
        additional_locations: list[LOCATION_TYPE] | None = None,
    ) -> Backup | None:
        """Create a full backup."""
        await self._check_location(location)

        if self._get_base_path(location) in {
            self.sys_config.path_backup,
            self.sys_config.path_core_backup,
        }:
            await Job.check_conditions(
                self, {JobCondition.FREE_SPACE}, "BackupManager.do_backup_full"
            )

        new_backup = self._create_backup(
            name, filename, BackupType.FULL, password, compressed, location, extra
        )

        _LOGGER.info("Creating new full backup with slug %s", new_backup.slug)
        backup = await self._do_backup(
            new_backup,
            self.sys_addons.installed,
            ALL_FOLDERS,
            True,
            homeassistant_exclude_database,
            additional_locations,
        )
        if backup:
            _LOGGER.info("Creating full backup with slug %s completed", backup.slug)
        return backup

    @Job(
        name="backup_manager_partial_backup",
        conditions=[JobCondition.RUNNING],
        limit=JobExecutionLimit.GROUP_ONCE,
        on_condition=BackupJobError,
        cleanup=False,
    )
    async def do_backup_partial(
        self,
        name: str = "",
        filename: str | None = None,
        *,
        addons: list[str] | None = None,
        folders: list[str] | None = None,
        password: str | None = None,
        homeassistant: bool = False,
        compressed: bool = True,
        location: LOCATION_TYPE | type[DEFAULT] = DEFAULT,
        homeassistant_exclude_database: bool | None = None,
        extra: dict | None = None,
        additional_locations: list[LOCATION_TYPE] | None = None,
    ) -> Backup | None:
        """Create a partial backup."""
        await self._check_location(location)

        if self._get_base_path(location) in {
            self.sys_config.path_backup,
            self.sys_config.path_core_backup,
        }:
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

        new_backup = self._create_backup(
            name, filename, BackupType.PARTIAL, password, compressed, location, extra
        )

        _LOGGER.info("Creating new partial backup with slug %s", new_backup.slug)
        addon_list = []
        for addon_slug in addons:
            addon = self.sys_addons.get(addon_slug)
            if addon and addon.is_installed:
                addon_list.append(cast(Addon, addon))
                continue
            _LOGGER.warning("Add-on %s not found/installed", addon_slug)

        backup = await self._do_backup(
            new_backup,
            addon_list,
            folders,
            homeassistant,
            homeassistant_exclude_database,
            additional_locations,
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
        location: str | None | type[DEFAULT],
    ) -> bool:
        """Restore from a backup.

        Must be called from an existing restore job.
        """
        addon_start_tasks: list[Awaitable[None]] | None = None
        success = True

        try:
            task_hass: asyncio.Task | None = None
            async with backup.open(location):
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
                    success = success and await backup.remove_delta_addons()

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
                    await task_hass
        except BackupError:
            raise
        except Exception as err:  # pylint: disable=broad-except
            _LOGGER.exception("Restore %s error", backup.slug)
            await async_capture_exception(err)
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
                self._change_stage(RestoreJobStage.AWAIT_HOME_ASSISTANT_RESTART, backup)

                # Do we need start Home Assistant Core?
                if not await self.sys_homeassistant.core.is_running():
                    await self.sys_homeassistant.core.start(
                        _job_override__cleanup=False
                    )

                # Check If we can access to API / otherwise restart
                if not await self.sys_homeassistant.api.check_api_state():
                    _LOGGER.warning("Need restart HomeAssistant for API")
                    await self.sys_homeassistant.core.restart(
                        _job_override__cleanup=False
                    )

    async def _validate_backup_location(
        self,
        backup: Backup,
        password: str | None = None,
        location: str | None | type[DEFAULT] = DEFAULT,
    ) -> None:
        """Validate location and password for backup, raise if invalid."""
        if location != DEFAULT and location not in backup.all_locations:
            raise BackupInvalidError(
                f"Backup {backup.slug} does not exist in {location}", _LOGGER.error
            )

        location_name = (
            cast(str | None, location) if location != DEFAULT else backup.location
        )
        if backup.all_locations[location_name].protected:
            backup.set_password(password)
        else:
            backup.set_password(None)

        await backup.validate_backup(location_name)

    @Job(
        name=JOB_FULL_RESTORE,
        conditions=[
            JobCondition.FREE_SPACE,
            JobCondition.HEALTHY,
            JobCondition.INTERNET_HOST,
            JobCondition.INTERNET_SYSTEM,
            JobCondition.RUNNING,
        ],
        limit=JobExecutionLimit.GROUP_ONCE,
        on_condition=BackupJobError,
        cleanup=False,
    )
    async def do_restore_full(
        self,
        backup: Backup,
        password: str | None = None,
        location: str | None | type[DEFAULT] = DEFAULT,
    ) -> bool:
        """Restore a backup."""
        # Add backup ID to job
        self.sys_jobs.current.reference = backup.slug

        if backup.sys_type != BackupType.FULL:
            raise BackupInvalidError(
                f"{backup.slug} is only a partial backup!", _LOGGER.error
            )

        await self._validate_backup_location(backup, password, location)

        if backup.supervisor_version > self.sys_supervisor.version:
            raise BackupInvalidError(
                f"Backup was made on supervisor version {backup.supervisor_version}, "
                f"can't restore on {self.sys_supervisor.version}. Must update supervisor first.",
                _LOGGER.error,
            )

        _LOGGER.info("Full-Restore %s start", backup.slug)
        await self.sys_core.set_state(CoreState.FREEZE)

        try:
            # Stop Home-Assistant / Add-ons
            await self.sys_core.shutdown(remove_homeassistant_container=True)

            success = await self._do_restore(
                backup,
                backup.addon_list,
                backup.folders,
                homeassistant=True,
                replace=True,
                location=location,
            )
        finally:
            await self.sys_core.set_state(CoreState.RUNNING)

        if success:
            _LOGGER.info("Full-Restore %s done", backup.slug)
        return success

    @Job(
        name=JOB_PARTIAL_RESTORE,
        conditions=[
            JobCondition.FREE_SPACE,
            JobCondition.HEALTHY,
            JobCondition.INTERNET_HOST,
            JobCondition.INTERNET_SYSTEM,
            JobCondition.RUNNING,
        ],
        limit=JobExecutionLimit.GROUP_ONCE,
        on_condition=BackupJobError,
        cleanup=False,
    )
    async def do_restore_partial(
        self,
        backup: Backup,
        homeassistant: bool = False,
        addons: list[str] | None = None,
        folders: list[str] | None = None,
        password: str | None = None,
        location: str | None | type[DEFAULT] = DEFAULT,
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

        await self._validate_backup_location(backup, password, location)

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
        await self.sys_core.set_state(CoreState.FREEZE)

        try:
            success = await self._do_restore(
                backup,
                addon_list,
                folder_list,
                homeassistant=homeassistant,
                replace=False,
                location=location,
            )
        finally:
            await self.sys_core.set_state(CoreState.RUNNING)

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
        await self.sys_core.set_state(CoreState.FREEZE)

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
            await self.sys_core.set_state(CoreState.RUNNING)
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
