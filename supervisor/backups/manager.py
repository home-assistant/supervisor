"""Backup manager."""
from __future__ import annotations

import asyncio
import logging
from pathlib import Path

from ..addons.addon import Addon
from ..const import FOLDER_HOMEASSISTANT, CoreState
from ..coresys import CoreSysAttributes
from ..exceptions import AddonsError
from ..jobs.decorator import Job, JobCondition
from ..utils.dt import utcnow
from .backup import Backup
from .const import BackupType
from .utils import create_slug
from .validate import ALL_FOLDERS

_LOGGER: logging.Logger = logging.getLogger(__name__)


class BackupManager(CoreSysAttributes):
    """Manage backups."""

    def __init__(self, coresys):
        """Initialize a backup manager."""
        self.coresys = coresys
        self._backups = {}
        self.lock = asyncio.Lock()

    @property
    def list_backups(self) -> set[Backup]:
        """Return a list of all backup objects."""
        return set(self._backups.values())

    def get(self, slug):
        """Return backup object."""
        return self._backups.get(slug)

    def _create_backup(
        self,
        name: str,
        sys_type: BackupType,
        password: str | None,
        compressed: bool = True,
    ) -> Backup:
        """Initialize a new backup object from name."""
        date_str = utcnow().isoformat()
        slug = create_slug(name, date_str)
        tar_file = Path(self.sys_config.path_backup, f"{slug}.tar")

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
            _load_backup(tar_file)
            for tar_file in self.sys_config.path_backup.glob("*.tar")
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
        try:
            self.sys_core.state = CoreState.FREEZE

            async with backup:
                # Backup add-ons
                if addon_list:
                    _LOGGER.info("Backing up %s store Add-ons", backup.slug)
                    await backup.store_addons(addon_list)

                # Backup folders
                # HomeAssistant Folder is for v1
                if FOLDER_HOMEASSISTANT in folder_list or homeassistant:
                    await backup.store_homeassistant()
                    folder_list = list(folder_list)
                    folder_list.remove(FOLDER_HOMEASSISTANT)

                if folder_list:
                    _LOGGER.info("Backing up %s store folders", backup.slug)
                    await backup.store_folders(folder_list)

        except Exception as err:  # pylint: disable=broad-except
            _LOGGER.exception("Backup %s error", backup.slug)
            self.sys_capture_exception(err)
            return None
        else:
            self._backups[backup.slug] = backup
            return backup
        finally:
            self.sys_core.state = CoreState.RUNNING

    @Job(conditions=[JobCondition.FREE_SPACE, JobCondition.RUNNING])
    async def do_backup_full(self, name="", password=None, compressed=True):
        """Create a full backup."""
        if self.lock.locked():
            _LOGGER.error("A backup/restore process is already running")
            return None

        backup = self._create_backup(name, BackupType.FULL, password, compressed)

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
        name="",
        addons=None,
        folders=None,
        password=None,
        homeassistant=True,
        compressed=True,
    ):
        """Create a partial backup."""
        if self.lock.locked():
            _LOGGER.error("A backup/restore process is already running")
            return None

        addons = addons or []
        folders = folders or []

        if len(addons) == 0 and len(folders) == 0 and not homeassistant:
            _LOGGER.error("Nothing to create backup for")

        backup = self._create_backup(name, BackupType.PARTIAL, password, compressed)

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
        addon_list: list[Addon],
        folder_list: list[str],
        homeassistant: bool,
        replace: bool,
    ):
        # Version 1
        if FOLDER_HOMEASSISTANT in folder_list:
            folder_list.remove(FOLDER_HOMEASSISTANT)
            homeassistant = True

        try:
            task_hass = None
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
                    await backup.restore_addons(addon_list)

                # Wait for Home Assistant Core update/downgrade
                if task_hass:
                    _LOGGER.info("Restore %s wait for Home-Assistant", backup.slug)
                    await task_hass

        except Exception as err:  # pylint: disable=broad-except
            _LOGGER.exception("Restore %s error", backup.slug)
            self.sys_capture_exception(err)
            return False
        else:
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
        self, backup, homeassistant=False, addons=None, folders=None, password=None
    ):
        """Restore a backup."""
        if self.lock.locked():
            _LOGGER.error("A backup/restore process is already running")
            return False

        if backup.protected and not backup.set_password(password):
            _LOGGER.error("Invalid password for backup %s", backup.slug)
            return False

        addon_list = addons or []
        folder_list = folders or []

        _LOGGER.info("Partial-Restore %s start", backup.slug)
        async with self.lock:
            self.sys_core.state = CoreState.FREEZE

            success = await self._do_restore(
                backup, addon_list, folder_list, homeassistant, False
            )

            self.sys_core.state = CoreState.RUNNING

            if success:
                _LOGGER.info("Partial-Restore %s done", backup.slug)
