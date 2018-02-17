"""Snapshot system control."""
import asyncio
from datetime import datetime
import logging
from pathlib import Path

from .snapshot import Snapshot
from .utils import create_slug
from ..const import (
    ATTR_SLUG, FOLDER_HOMEASSISTANT, SNAPSHOT_FULL, SNAPSHOT_PARTIAL)
from ..coresys import CoreSysAttributes

_LOGGER = logging.getLogger(__name__)


class SnapshotManager(CoreSysAttributes):
    """Manage snapshots."""

    def __init__(self, coresys):
        """Initialize a snapshot manager."""
        self.coresys = coresys
        self.snapshots_obj = {}
        self.lock = asyncio.Lock(loop=coresys.loop)

    @property
    def list_snapshots(self):
        """Return a list of all snapshot object."""
        return set(self.snapshots_obj.values())

    def get(self, slug):
        """Return snapshot object."""
        return self.snapshots_obj.get(slug)

    def _create_snapshot(self, name, sys_type, password):
        """Initialize a new snapshot object from name."""
        date_str = datetime.utcnow().isoformat()
        slug = create_slug(name, date_str)
        tar_file = Path(self._config.path_backup, f"{slug}.tar")

        # init object
        snapshot = Snapshot(self.coresys, tar_file)
        snapshot.new(slug, name, date_str, sys_type, password)

        # set general data
        snapshot.store_homeassistant()
        snapshot.store_repositories()

        return snapshot

    def load(self):
        """Load exists snapshots data.

        Return a coroutine.
        """
        return self.reload()

    async def reload(self):
        """Load exists backups."""
        self.snapshots_obj = {}

        async def _load_snapshot(tar_file):
            """Internal function to load snapshot."""
            snapshot = Snapshot(self.coresys, tar_file)
            if await snapshot.load():
                self.snapshots_obj[snapshot.slug] = snapshot

        tasks = [_load_snapshot(tar_file) for tar_file in
                 self._config.path_backup.glob("*.tar")]

        _LOGGER.info("Found %d snapshot files", len(tasks))
        if tasks:
            await asyncio.wait(tasks, loop=self._loop)

    def remove(self, snapshot):
        """Remove a snapshot."""
        try:
            snapshot.tarfile.unlink()
            self.snapshots_obj.pop(snapshot.slug, None)
            _LOGGER.info("Removed snapshot file %s", snapshot.slug)

        except OSError as err:
            _LOGGER.error("Can't remove snapshot %s: %s", snapshot.slug, err)
            return False

        return True

    async def import_snapshot(self, tar_file):
        """Check snapshot tarfile and import it."""
        snapshot = Snapshot(self.coresys, tar_file)

        # Read meta data
        if not await snapshot.load():
            return False

        # Allready exists?
        if snapshot.slug in self.snapshots_obj:
            _LOGGER.error("Snapshot %s allready exists!", snapshot.slug)
            return False

        # Move snapshot to backup
        try:
            snapshot.tarfile.rename(
                Path(self._config.path_backup, f"{snapshot.slug}.tar"))

        except OSError as err:
            _LOGGER.error("Can't move snapshot file to storage: %s", err)
            return False

        await self.reload()
        return True

    async def do_snapshot_full(self, name="", password=None):
        """Create a full snapshot."""
        if self.lock.locked():
            _LOGGER.error("It is already a snapshot/restore process running")
            return False

        snapshot = self._create_snapshot(name, SNAPSHOT_FULL, password)
        _LOGGER.info("Full-Snapshot %s start", snapshot.slug)
        try:
            self._scheduler.suspend = True
            await self.lock.acquire()

            async with snapshot:
                # Snapshot add-ons
                _LOGGER.info("Snapshot %s store Add-ons", snapshot.slug)
                await snapshot.store_addons()

                # Snapshot folders
                _LOGGER.info("Snapshot %s store folders", snapshot.slug)
                await snapshot.store_folders()

        except Exception:  # pylint: disable=broad-except
            _LOGGER.exception("Snapshot %s error", snapshot.slug)
            return False

        else:
            _LOGGER.info("Full-Snapshot %s done", snapshot.slug)
            self.snapshots_obj[snapshot.slug] = snapshot
            return True

        finally:
            self._scheduler.suspend = False
            self.lock.release()

    async def do_snapshot_partial(self, name="", addons=None, folders=None,
                                  password=None):
        """Create a partial snapshot."""
        if self.lock.locked():
            _LOGGER.error("It is already a snapshot/restore process running")
            return False

        addons = addons or []
        folders = folders or []
        snapshot = self._create_snapshot(name, SNAPSHOT_PARTIAL, password)

        _LOGGER.info("Partial-Snapshot %s start", snapshot.slug)
        try:
            self._scheduler.suspend = True
            await self.lock.acquire()

            async with snapshot:
                # Snapshot add-ons
                addon_list = []
                for addon_slug in addons:
                    addon = self._addons.get(addon_slug)
                    if addon and addon.is_installed:
                        addon_list.append(addon)
                        continue
                    _LOGGER.warning("Add-on %s not found", addon_slug)

                _LOGGER.info("Snapshot %s store Add-ons", snapshot.slug)
                await snapshot.store_addons(addon_list)

                # snapshot folders
                _LOGGER.info("Snapshot %s store folders", snapshot.slug)
                await snapshot.store_folders(folders)

        except Exception:  # pylint: disable=broad-except
            _LOGGER.exception("Snapshot %s error", snapshot.slug)
            return False

        else:
            _LOGGER.info("Partial-Snapshot %s done", snapshot.slug)
            self.snapshots_obj[snapshot.slug] = snapshot
            return True

        finally:
            self._scheduler.suspend = False
            self.lock.release()

    async def do_restore_full(self, snapshot, password=None):
        """Restore a snapshot."""
        if self.lock.locked():
            _LOGGER.error("It is already a snapshot/restore process running")
            return False

        if snapshot.sys_type != SNAPSHOT_FULL:
            _LOGGER.error("Restore %s is only a partial snapshot!",
                          snapshot.slug)
            return False

        if snapshot.protected and not snapshot.set_password(password):
            _LOGGER.error("Invalid password for snapshot %s", snapshot.slug)
            return False

        _LOGGER.info("Full-Restore %s start", snapshot.slug)
        try:
            self._scheduler.suspend = True
            await self.lock.acquire()

            async with snapshot:
                tasks = []

                # Stop Home-Assistant / Add-ons
                tasks.append(self._homeassistant.stop())
                for addon in self._addons.list_addons:
                    if addon.is_installed:
                        tasks.append(addon.stop())

                _LOGGER.info("Restore %s stop running tasks", snapshot.slug)
                await asyncio.wait(tasks, loop=self._loop)

                # Restore folders
                _LOGGER.info("Restore %s run folders", snapshot.slug)
                await snapshot.restore_folders()

                # Start homeassistant restore
                _LOGGER.info("Restore %s run Home-Assistant", snapshot.slug)
                snapshot.restore_homeassistant()
                task_hass = self._loop.create_task(
                    self._homeassistant.update(snapshot.homeassistant_version))

                # Restore repositories
                _LOGGER.info("Restore %s run Repositories", snapshot.slug)
                await snapshot.restore_repositories()

                # Delete delta add-ons
                tasks.clear()
                addon_list = set(addon[ATTR_SLUG] for addon in snapshot.addons)
                for addon in self._addons.list_installed:
                    if addon.slug not in addon_list:
                        tasks.append(addon.uninstall())
                _LOGGER.info("Restore %s remove add-ons", snapshot.slug)
                await asyncio.wait(tasks, loop=self._loop)

                # Restore add-ons
                _LOGGER.info("Restore %s old add-ons", snapshot.slug)
                await snapshot.restore_addons()

                # finish homeassistant task
                _LOGGER.info("Restore %s wait until homeassistant ready",
                             snapshot.slug)
                await task_hass
                await self._homeassistant.start()

        except Exception:  # pylint: disable=broad-except
            _LOGGER.exception("Restore %s error", snapshot.slug)
            return False

        else:
            _LOGGER.info("Full-Restore %s done", snapshot.slug)
            return True

        finally:
            self._scheduler.suspend = False
            self.lock.release()

    async def do_restore_partial(self, snapshot, homeassistant=False,
                                 addons=None, folders=None, password=None):
        """Restore a snapshot."""
        if self.lock.locked():
            _LOGGER.error("It is already a snapshot/restore process running")
            return False

        if snapshot.protected and not snapshot.set_password(password):
            _LOGGER.error("Invalid password for snapshot %s", snapshot.slug)
            return False

        addons = addons or []
        folders = folders or []

        _LOGGER.info("Partial-Restore %s start", snapshot.slug)
        try:
            self._scheduler.suspend = True
            await self.lock.acquire()

            async with snapshot:
                if FOLDER_HOMEASSISTANT in folders:
                    await self._homeassistant.stop()

                if folders:
                    _LOGGER.info("Restore %s run folders", snapshot.slug)
                    await snapshot.restore_folders(folders)

                if homeassistant:
                    _LOGGER.info("Restore %s run Home-Assistant",
                                 snapshot.slug)
                    snapshot.restore_homeassistant()
                    task_hass = self._loop.create_task(
                        self._homeassistant.update(
                            snapshot.homeassistant_version))

                addon_list = []
                for slug in addons:
                    addon = self._addons.get(slug)
                    if addon:
                        addon_list.append(addon)
                        continue
                    _LOGGER.warning("Can't restore addon %s", snapshot.slug)

                if addon_list:
                    _LOGGER.info("Restore %s old add-ons", snapshot.slug)
                    await snapshot.restore_addons(addon_list)

                # make sure homeassistant run agen
                if task_hass:
                    _LOGGER.info("Restore %s wait for Home-Assistant",
                                 snapshot.slug)
                    await task_hass
                await self._homeassistant.start()

        except Exception:  # pylint: disable=broad-except
            _LOGGER.exception("Restore %s error", snapshot.slug)
            return False

        else:
            _LOGGER.info("Partial-Restore %s done", snapshot.slug)
            return True

        finally:
            self._scheduler.suspend = False
            self.lock.release()
