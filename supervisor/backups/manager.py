"""Backup manager."""
from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Iterable
import logging
from pathlib import Path

from ..addons.addon import Addon
from ..const import (
    ATTR_DAYS_UNTIL_STALE,
    FILE_HASSIO_BACKUPS,
    FOLDER_HOMEASSISTANT,
    CoreState,
)
from ..coresys import CoreSysAttributes
from ..dbus.const import UnitActiveState
from ..exceptions import AddonsError
from ..jobs.decorator import Job, JobCondition
from ..mounts.mount import Mount
from ..utils.common import FileConfiguration
from ..utils.dt import utcnow
from ..utils.sentinel import DEFAULT
from ..utils.sentry import capture_exception
from .backup import Backup
from .const import BackupType
from .utils import create_slug
from .validate import ALL_FOLDERS, SCHEMA_BACKUPS_CONFIG

_LOGGER: logging.Logger = logging.getLogger(__name__)


def _list_backup_files(path: Path) -> Iterable[Path]:
    """Return iterable of backup files, suppress and log OSError for network mounts."""
    try:
        # is_dir does a stat syscall which raises if the mount is down
        if path.is_dir():
            return path.glob("*.tar")
    except OSError as err:
        _LOGGER.error("Could not list backups from %s: %s", path.as_posix(), err)

    return []


class BackupManager(FileConfiguration, CoreSysAttributes):
    """Manage backups."""

    def __init__(self, coresys):
        """Initialize a backup manager."""
        super().__init__(FILE_HASSIO_BACKUPS, SCHEMA_BACKUPS_CONFIG)
        self.coresys = coresys
        self._backups = {}
        self.lock = asyncio.Lock()

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

    def get(self, slug):
        """Return backup object."""
        return self._backups.get(slug)

    def _get_base_path(self, location: Mount | type[DEFAULT] | None = DEFAULT) -> Path:
        """Get base path for backup using location or default location."""
        if location:
            return location.local_where

        if location == DEFAULT and self.sys_mounts.default_backup_mount:
            return self.sys_mounts.default_backup_mount.local_where

        return self.sys_config.path_backup

    def _create_backup(
        self,
        name: str,
        sys_type: BackupType,
        password: str | None,
        compressed: bool = True,
        location: Mount | type[DEFAULT] | None = DEFAULT,
    ) -> Backup:
        """Initialize a new backup object from name."""
        date_str = utcnow().isoformat()
        slug = create_slug(name, date_str)
        tar_file = Path(self._get_base_path(location), f"{slug}.tar")

        # init object
        backup = Backup(self.coresys, tar_file)
        backup.new(slug, name, date_str, sys_type, password, compressed)

        backup.store_repositories()
        backup.store_dockerconfig()

        return backup

    def load(self):
        """Load exists backups data.

        Return a coroutine.
        """
        return self.reload()

    async def reload(self):
        """Load exists backups."""
        self._backups = {}

        async def _load_backup(tar_file):
            """Load the backup."""
            backup = Backup(self.coresys, tar_file)
            if await backup.load():
                self._backups[backup.slug] = backup

        tasks = [
            self.sys_create_task(_load_backup(tar_file))
            for path in self.backup_locations
            for tar_file in _list_backup_files(path)
        ]

        _LOGGER.info("Found %d backup files", len(tasks))
        if tasks:
            await asyncio.wait(tasks)

    def remove(self, backup):
        """Remove a backup."""
        try:
            backup.tarfile.unlink()
            self._backups.pop(backup.slug, None)
            _LOGGER.info("Removed backup file %s", backup.slug)

        except OSError as err:
            _LOGGER.error("Can't remove backup %s: %s", backup.slug, err)
            return False

        return True

    async def import_backup(self, tar_file):
        """Check backup tarfile and import it."""
        backup = Backup(self.coresys, tar_file)

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
            _LOGGER.error("Can't move backup file to storage: %s", err)
            return None

        # Load new backup
        backup = Backup(self.coresys, tar_origin)
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
    ):
        addon_start_tasks: list[Awaitable[None]] | None = None
        try:
            self.sys_core.state = CoreState.FREEZE

            async with backup:
                # Backup add-ons
                if addon_list:
                    _LOGGER.info("Backing up %s store Add-ons", backup.slug)
                    addon_start_tasks = await backup.store_addons(addon_list)

                # HomeAssistant Folder is for v1
                if homeassistant:
                    await backup.store_homeassistant()

                # Backup folders
                if folder_list:
                    _LOGGER.info("Backing up %s store folders", backup.slug)
                    await backup.store_folders(folder_list)

        except Exception as err:  # pylint: disable=broad-except
            _LOGGER.exception("Backup %s error", backup.slug)
            capture_exception(err)
            return None
        else:
            self._backups[backup.slug] = backup

            if addon_start_tasks:
                # Ignore exceptions from waiting for addon startup, addon errors handled elsewhere
                await asyncio.gather(*addon_start_tasks, return_exceptions=True)

            return backup
        finally:
            self.sys_core.state = CoreState.RUNNING

    @Job(conditions=[JobCondition.FREE_SPACE, JobCondition.RUNNING])
    async def do_backup_full(
        self,
        name="",
        password=None,
        compressed=True,
        location: Mount | type[DEFAULT] | None = DEFAULT,
    ):
        """Create a full backup."""
        if self.lock.locked():
            _LOGGER.error("A backup/restore process is already running")
            return None

        backup = self._create_backup(
            name, BackupType.FULL, password, compressed, location
        )

        _LOGGER.info("Creating new full backup with slug %s", backup.slug)
        async with self.lock:
            backup = await self._do_backup(
                backup, self.sys_addons.installed, ALL_FOLDERS, True
            )
            if backup:
                _LOGGER.info("Creating full backup with slug %s completed", backup.slug)
            return backup

    @Job(conditions=[JobCondition.FREE_SPACE, JobCondition.RUNNING])
    async def do_backup_partial(
        self,
        name: str = "",
        addons: list[str] | None = None,
        folders: list[str] | None = None,
        password: str | None = None,
        homeassistant: bool = False,
        compressed: bool = True,
        location: Mount | type[DEFAULT] | None = DEFAULT,
    ):
        """Create a partial backup."""
        if self.lock.locked():
            _LOGGER.error("A backup/restore process is already running")
            return None

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
        async with self.lock:
            addon_list = []
            for addon_slug in addons:
                addon = self.sys_addons.get(addon_slug)
                if addon and addon.is_installed:
                    addon_list.append(addon)
                    continue
                _LOGGER.warning("Add-on %s not found/installed", addon_slug)

            backup = await self._do_backup(backup, addon_list, folders, homeassistant)
            if backup:
                _LOGGER.info(
                    "Creating partial backup with slug %s completed", backup.slug
                )
            return backup

    async def _do_restore(
        self,
        backup: Backup,
        addon_list: list[str],
        folder_list: list[str],
        homeassistant: bool,
        replace: bool,
    ):
        addon_start_tasks: list[Awaitable[None]] | None = None
        try:
            task_hass: asyncio.Task | None = None
            async with backup:
                # Restore docker config
                _LOGGER.info("Restoring %s Docker config", backup.slug)
                backup.restore_dockerconfig(replace)

                # Process folders
                if folder_list:
                    _LOGGER.info("Restoring %s folders", backup.slug)
                    await backup.restore_folders(folder_list)

                # Process Home-Assistant
                if homeassistant:
                    _LOGGER.info("Restoring %s Home Assistant Core", backup.slug)
                    task_hass = await backup.restore_homeassistant()

                # Delete delta add-ons
                if replace:
                    _LOGGER.info("Removing Add-ons not in the backup %s", backup.slug)
                    for addon in self.sys_addons.installed:
                        if addon.slug in backup.addon_list:
                            continue

                        # Remove Add-on because it's not a part of the new env
                        # Do it sequential avoid issue on slow IO
                        try:
                            await addon.uninstall()
                        except AddonsError:
                            _LOGGER.warning("Can't uninstall Add-on %s", addon.slug)

                if addon_list:
                    _LOGGER.info("Restoring %s Repositories", backup.slug)
                    await backup.restore_repositories(replace)

                    _LOGGER.info("Restoring %s Add-ons", backup.slug)
                    addon_start_tasks = await backup.restore_addons(addon_list)

                # Wait for Home Assistant Core update/downgrade
                if task_hass:
                    _LOGGER.info("Restore %s wait for Home-Assistant", backup.slug)
                    await task_hass

        except Exception as err:  # pylint: disable=broad-except
            _LOGGER.exception("Restore %s error", backup.slug)
            capture_exception(err)
            return False
        else:
            if addon_start_tasks:
                # Ignore exceptions from waiting for addon startup, addon errors handled elsewhere
                await asyncio.gather(*addon_start_tasks, return_exceptions=True)

            return True
        finally:
            # Do we need start Home Assistant Core?
            if not await self.sys_homeassistant.core.is_running():
                await self.sys_homeassistant.core.start()

            # Check If we can access to API / otherwise restart
            if not await self.sys_homeassistant.api.check_api_state():
                _LOGGER.warning("Need restart HomeAssistant for API")
                await self.sys_homeassistant.core.restart()

    @Job(
        conditions=[
            JobCondition.FREE_SPACE,
            JobCondition.HEALTHY,
            JobCondition.INTERNET_HOST,
            JobCondition.INTERNET_SYSTEM,
            JobCondition.RUNNING,
        ]
    )
    async def do_restore_full(self, backup: Backup, password=None):
        """Restore a backup."""
        if self.lock.locked():
            _LOGGER.error("A backup/restore process is already running")
            return False

        if backup.sys_type != BackupType.FULL:
            _LOGGER.error("%s is only a partial backup!", backup.slug)
            return False

        if backup.protected and not backup.set_password(password):
            _LOGGER.error("Invalid password for backup %s", backup.slug)
            return False

        if backup.supervisor_version > self.sys_supervisor.version:
            _LOGGER.error(
                "Backup was made on supervisor version %s, can't restore on %s. Must update supervisor first.",
                backup.supervisor_version,
                self.sys_supervisor.version,
            )
            return False

        _LOGGER.info("Full-Restore %s start", backup.slug)
        async with self.lock:
            self.sys_core.state = CoreState.FREEZE

            # Stop Home-Assistant / Add-ons
            await self.sys_core.shutdown()

            success = await self._do_restore(
                backup, backup.addon_list, backup.folders, True, True
            )

            self.sys_core.state = CoreState.RUNNING

            if success:
                _LOGGER.info("Full-Restore %s done", backup.slug)

    @Job(
        conditions=[
            JobCondition.FREE_SPACE,
            JobCondition.HEALTHY,
            JobCondition.INTERNET_HOST,
            JobCondition.INTERNET_SYSTEM,
            JobCondition.RUNNING,
        ]
    )
    async def do_restore_partial(
        self,
        backup: Backup,
        homeassistant: bool = False,
        addons: list[str] | None = None,
        folders: list[Path] | None = None,
        password: str | None = None,
    ):
        """Restore a backup."""
        if self.lock.locked():
            _LOGGER.error("A backup/restore process is already running")
            return False

        addon_list = addons or []
        folder_list = folders or []

        # Version 1
        if FOLDER_HOMEASSISTANT in folder_list:
            folder_list.remove(FOLDER_HOMEASSISTANT)
            homeassistant = True

        if backup.protected and not backup.set_password(password):
            _LOGGER.error("Invalid password for backup %s", backup.slug)
            return False

        if backup.homeassistant is None and homeassistant:
            _LOGGER.error("No Home Assistant Core data inside the backup")
            return False

        if backup.supervisor_version > self.sys_supervisor.version:
            _LOGGER.error(
                "Backup was made on supervisor version %s, can't restore on %s. Must update supervisor first.",
                backup.supervisor_version,
                self.sys_supervisor.version,
            )
            return False

        _LOGGER.info("Partial-Restore %s start", backup.slug)
        async with self.lock:
            self.sys_core.state = CoreState.FREEZE

            success = await self._do_restore(
                backup, addon_list, folder_list, homeassistant, False
            )

            self.sys_core.state = CoreState.RUNNING

            if success:
                _LOGGER.info("Partial-Restore %s done", backup.slug)
