"""Backup manager."""
import asyncio
import logging
from pathlib import Path
from typing import Awaitable

from awesomeversion.awesomeversion import AwesomeVersion
from awesomeversion.exceptions import AwesomeVersionCompareException

from ..const import FOLDER_HOMEASSISTANT, CoreState
from ..coresys import CoreSysAttributes
from ..exceptions import AddonsError
from ..jobs.decorator import Job, JobCondition
from ..utils.dt import utcnow
from .backup import Backup
from .const import BackupType
from .utils import create_slug

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

    def _create_backup(self, name, sys_type, password, homeassistant=True):
        """Initialize a new backup object from name."""
        date_str = utcnow().isoformat()
        slug = create_slug(name, date_str)
        tar_file = Path(self.sys_config.path_backup, f"{slug}.tar")

        # init object
        backup = Backup(self.coresys, tar_file)
        backup.new(slug, name, date_str, sys_type, password)

        # set general data
        if homeassistant:
            backup.store_homeassistant()

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

    @Job(conditions=[JobCondition.FREE_SPACE, JobCondition.RUNNING])
    async def do_backup_full(self, name="", password=None):
        """Create a full backup."""
        if self.lock.locked():
            _LOGGER.error("A backup/restore process is already running")
            return None

        backup = self._create_backup(name, BackupType.FULL, password)
        _LOGGER.info("Creating new full backup with slug %s", backup.slug)
        try:
            self.sys_core.state = CoreState.FREEZE
            await self.lock.acquire()

            async with backup:
                # Backup add-ons
                _LOGGER.info("Backing up %s store Add-ons", backup.slug)
                await backup.store_addons()

                # Backup folders
                _LOGGER.info("Backing up %s store folders", backup.slug)
                await backup.store_folders()

        except Exception as err:  # pylint: disable=broad-except
            _LOGGER.exception("Backup %s error", backup.slug)
            self.sys_capture_exception(err)
            return None

        else:
            _LOGGER.info("Creating full backup with slug %s completed", backup.slug)
            self._backups[backup.slug] = backup
            return backup

        finally:
            self.sys_core.state = CoreState.RUNNING
            self.lock.release()

    @Job(conditions=[JobCondition.FREE_SPACE, JobCondition.RUNNING])
    async def do_backup_partial(
        self, name="", addons=None, folders=None, password=None, homeassistant=True
    ):
        """Create a partial backup."""
        if self.lock.locked():
            _LOGGER.error("A backup/restore process is already running")
            return None

        addons = addons or []
        folders = folders or []

        if len(addons) == 0 and len(folders) == 0 and not homeassistant:
            _LOGGER.error("Nothing to create backup for")
            return

        backup = self._create_backup(name, BackupType.PARTIAL, password, homeassistant)

        _LOGGER.info("Creating new partial backup with slug %s", backup.slug)
        try:
            self.sys_core.state = CoreState.FREEZE
            await self.lock.acquire()

            async with backup:
                # Backup add-ons
                addon_list = []
                for addon_slug in addons:
                    addon = self.sys_addons.get(addon_slug)
                    if addon and addon.is_installed:
                        addon_list.append(addon)
                        continue
                    _LOGGER.warning("Add-on %s not found/installed", addon_slug)

                if addon_list:
                    _LOGGER.info("Backing up %s store Add-ons", backup.slug)
                    await backup.store_addons(addon_list)

                # Backup folders
                if folders:
                    _LOGGER.info("Backing up %s store folders", backup.slug)
                    await backup.store_folders(folders)

        except Exception as err:  # pylint: disable=broad-except
            _LOGGER.exception("Backup %s error", backup.slug)
            self.sys_capture_exception(err)
            return None

        else:
            _LOGGER.info("Creating partial backup with slug %s completed", backup.slug)
            self._backups[backup.slug] = backup
            return backup

        finally:
            self.sys_core.state = CoreState.RUNNING
            self.lock.release()

    @Job(
        conditions=[
            JobCondition.FREE_SPACE,
            JobCondition.HEALTHY,
            JobCondition.INTERNET_HOST,
            JobCondition.INTERNET_SYSTEM,
            JobCondition.RUNNING,
        ]
    )
    async def do_restore_full(self, backup, password=None):
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
        try:
            self.sys_core.state = CoreState.FREEZE
            await self.lock.acquire()

            async with backup:
                # Stop Home-Assistant / Add-ons
                await self.sys_core.shutdown()

                # Restore folders
                _LOGGER.info("Restoring %s folders", backup.slug)
                await backup.restore_folders()

                # Restore docker config
                _LOGGER.info("Restoring %s Docker Config", backup.slug)
                backup.restore_dockerconfig()

                # Start homeassistant restore
                _LOGGER.info("Restoring %s Home-Assistant", backup.slug)
                backup.restore_homeassistant()
                task_hass = self._update_core_task(backup.homeassistant_version)

                # Restore repositories
                _LOGGER.info("Restoring %s Repositories", backup.slug)
                await backup.restore_repositories()

                # Delete delta add-ons
                _LOGGER.info("Removing add-ons not in the backup %s", backup.slug)
                for addon in self.sys_addons.installed:
                    if addon.slug in backup.addon_list:
                        continue

                    # Remove Add-on because it's not a part of the new env
                    # Do it sequential avoid issue on slow IO
                    try:
                        await addon.uninstall()
                    except AddonsError:
                        _LOGGER.warning("Can't uninstall Add-on %s", addon.slug)

                # Restore add-ons
                _LOGGER.info("Restore %s old add-ons", backup.slug)
                await backup.restore_addons()

                # finish homeassistant task
                _LOGGER.info("Restore %s wait until homeassistant ready", backup.slug)
                await task_hass
                await self.sys_homeassistant.core.start()

        except Exception as err:  # pylint: disable=broad-except
            _LOGGER.exception("Restore %s error", backup.slug)
            self.sys_capture_exception(err)
            return False

        else:
            _LOGGER.info("Full-Restore %s done", backup.slug)
            return True

        finally:
            self.sys_core.state = CoreState.RUNNING
            self.lock.release()

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

        addons = addons or []
        folders = folders or []

        _LOGGER.info("Partial-Restore %s start", backup.slug)
        try:
            self.sys_core.state = CoreState.FREEZE
            await self.lock.acquire()

            async with backup:
                # Restore docker config
                _LOGGER.info("Restoring %s Docker Config", backup.slug)
                backup.restore_dockerconfig()

                # Stop Home-Assistant for config restore
                if FOLDER_HOMEASSISTANT in folders:
                    await self.sys_homeassistant.core.stop()
                    backup.restore_homeassistant()

                # Process folders
                if folders:
                    _LOGGER.info("Restoring %s folders", backup.slug)
                    await backup.restore_folders(folders)

                # Process Home-Assistant
                task_hass = None
                if homeassistant:
                    _LOGGER.info("Restoring %s Home-Assistant", backup.slug)
                    task_hass = self._update_core_task(backup.homeassistant_version)

                if addons:
                    _LOGGER.info("Restoring %s Repositories", backup.slug)
                    await backup.restore_repositories()

                    _LOGGER.info("Restoring %s old add-ons", backup.slug)
                    await backup.restore_addons(addons)

                # Make sure homeassistant run agen
                if task_hass:
                    _LOGGER.info("Restore %s wait for Home-Assistant", backup.slug)
                    await task_hass

                # Do we need start HomeAssistant?
                if not await self.sys_homeassistant.core.is_running():
                    await self.sys_homeassistant.core.start()

                # Check If we can access to API / otherwise restart
                if not await self.sys_homeassistant.api.check_api_state():
                    _LOGGER.warning("Need restart HomeAssistant for API")
                    await self.sys_homeassistant.core.restart()

        except Exception as err:  # pylint: disable=broad-except
            _LOGGER.exception("Restore %s error", backup.slug)
            self.sys_capture_exception(err)
            return False

        else:
            _LOGGER.info("Partial-Restore %s done", backup.slug)
            return True

        finally:
            self.sys_core.state = CoreState.RUNNING
            self.lock.release()

    def _update_core_task(self, version: AwesomeVersion) -> Awaitable[None]:
        """Process core update if needed and make awaitable object."""

        async def _core_update():
            try:
                if version == self.sys_homeassistant.version:
                    return
            except (AwesomeVersionCompareException, TypeError):
                pass
            await self.sys_homeassistant.core.update(version)

        return self.sys_create_task(_core_update())
