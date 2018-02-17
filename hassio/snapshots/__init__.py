"""Snapshot system control."""
import asyncio
import logging
from pathlib import Path
import tarfile

from .snapshot import Snapshot
from .utils import create_slug
from ..const import (
    ATTR_SLUG, FOLDER_HOMEASSISTANT, SNAPSHOT_FULL, SNAPSHOT_PARTIAL)
from ..coresys import CoreSysAttributes
from ..utils.dt import utcnow

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

    def _create_snapshot(self, name, sys_type):
        """Initialize a new snapshot object from name."""
        date_str = utcnow().isoformat()
        slug = create_slug(name, date_str)
        tar_file = Path(self._config.path_backup, "{}.tar".format(slug))

        # init object
        snapshot = Snapshot(self.coresys, tar_file)
        snapshot.create(slug, name, date_str, sys_type)

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
            snapshot.tar_file.unlink()
            self.snapshots_obj.pop(snapshot.slug, None)
        except OSError as err:
            _LOGGER.error("Can't remove snapshot %s: %s", snapshot.slug, err)
            return False

        return True

    async def do_snapshot_full(self, name=""):
        """Create a full snapshot."""
        if self.lock.locked():
            _LOGGER.error("It is already a snapshot/restore process running")
            return False

        snapshot = self._create_snapshot(name, SNAPSHOT_FULL)
        _LOGGER.info("Full-Snapshot %s start", snapshot.slug)
        try:
            self._scheduler.suspend = True
            await self.lock.acquire()

            async with snapshot:
                # snapshot addons
                tasks = []
                for addon in self._addons.list_addons:
                    if not addon.is_installed:
                        continue
                    tasks.append(snapshot.import_addon(addon))

                if tasks:
                    _LOGGER.info("Full-Snapshot %s run %d addons",
                                 snapshot.slug, len(tasks))
                    await asyncio.wait(tasks, loop=self._loop)

                # snapshot folders
                _LOGGER.info("Full-Snapshot %s store folders", snapshot.slug)
                await snapshot.store_folders()

        except (OSError, ValueError, tarfile.TarError) as err:
            _LOGGER.info("Full-Snapshot %s error: %s", snapshot.slug, err)
            return False

        else:
            _LOGGER.info("Full-Snapshot %s done", snapshot.slug)
            self.snapshots_obj[snapshot.slug] = snapshot
            return True

        finally:
            self._scheduler.suspend = False
            self.lock.release()

    async def do_snapshot_partial(self, name="", addons=None, folders=None):
        """Create a partial snapshot."""
        if self.lock.locked():
            _LOGGER.error("It is already a snapshot/restore process running")
            return False

        addons = addons or []
        folders = folders or []
        snapshot = self._create_snapshot(name, SNAPSHOT_PARTIAL)

        _LOGGER.info("Partial-Snapshot %s start", snapshot.slug)
        try:
            self._scheduler.suspend = True
            await self.lock.acquire()

            async with snapshot:
                # snapshot addons
                tasks = []
                for slug in addons:
                    addon = self._addons.get(slug)
                    if addon.is_installed:
                        tasks.append(snapshot.import_addon(addon))

                if tasks:
                    _LOGGER.info("Partial-Snapshot %s run %d addons",
                                 snapshot.slug, len(tasks))
                    await asyncio.wait(tasks, loop=self._loop)

                # snapshot folders
                _LOGGER.info("Partial-Snapshot %s store folders %s",
                             snapshot.slug, folders)
                await snapshot.store_folders(folders)

        except (OSError, ValueError, tarfile.TarError) as err:
            _LOGGER.info("Partial-Snapshot %s error: %s", snapshot.slug, err)
            return False

        else:
            _LOGGER.info("Partial-Snapshot %s done", snapshot.slug)
            self.snapshots_obj[snapshot.slug] = snapshot
            return True

        finally:
            self._scheduler.suspend = False
            self.lock.release()

    async def do_restore_full(self, snapshot):
        """Restore a snapshot."""
        if self.lock.locked():
            _LOGGER.error("It is already a snapshot/restore process running")
            return False

        if snapshot.sys_type != SNAPSHOT_FULL:
            _LOGGER.error(
                "Full-Restore %s is only a partial snapshot!", snapshot.slug)
            return False

        _LOGGER.info("Full-Restore %s start", snapshot.slug)
        try:
            self._scheduler.suspend = True
            await self.lock.acquire()

            async with snapshot:
                # stop system
                tasks = []
                tasks.append(self._homeassistant.stop())

                for addon in self._addons.list_addons:
                    if addon.is_installed:
                        tasks.append(addon.stop())

                await asyncio.wait(tasks, loop=self._loop)

                # restore folders
                _LOGGER.info("Full-Restore %s restore folders", snapshot.slug)
                await snapshot.restore_folders()

                # start homeassistant restore
                _LOGGER.info("Full-Restore %s restore Home-Assistant",
                             snapshot.slug)
                snapshot.restore_homeassistant()
                task_hass = self._loop.create_task(
                    self._homeassistant.update(snapshot.homeassistant_version))

                # restore repositories
                _LOGGER.info("Full-Restore %s restore Repositories",
                             snapshot.slug)
                await snapshot.restore_repositories()

                # restore addons
                tasks = []
                actual_addons = \
                    set(addon.slug for addon in self._addons.list_addons
                        if addon.is_installed)
                restore_addons = \
                    set(data[ATTR_SLUG] for data in snapshot.addons)
                remove_addons = actual_addons - restore_addons

                _LOGGER.info("Full-Restore %s restore addons %s, remove %s",
                             snapshot.slug, restore_addons, remove_addons)

                for slug in remove_addons:
                    addon = self._addons.get(slug)
                    if addon:
                        tasks.append(addon.uninstall())
                    else:
                        _LOGGER.warning("Can't remove addon %s", snapshot.slug)

                for slug in restore_addons:
                    addon = self._addons.get(slug)
                    if addon:
                        tasks.append(snapshot.export_addon(addon))
                    else:
                        _LOGGER.warning("Can't restore addon %s", slug)

                if tasks:
                    _LOGGER.info("Full-Restore %s restore addons tasks %d",
                                 snapshot.slug, len(tasks))
                    await asyncio.wait(tasks, loop=self._loop)

                # finish homeassistant task
                _LOGGER.info("Full-Restore %s wait until homeassistant ready",
                             snapshot.slug)
                await task_hass
                await self._homeassistant.start()

        except (OSError, ValueError, tarfile.TarError) as err:
            _LOGGER.info("Full-Restore %s error: %s", snapshot.slug, err)
            return False

        else:
            _LOGGER.info("Full-Restore %s done", snapshot.slug)
            return True

        finally:
            self._scheduler.suspend = False
            self.lock.release()

    async def do_restore_partial(self, snapshot, homeassistant=False,
                                 addons=None, folders=None):
        """Restore a snapshot."""
        if self.lock.locked():
            _LOGGER.error("It is already a snapshot/restore process running")
            return False

        addons = addons or []
        folders = folders or []

        _LOGGER.info("Partial-Restore %s start", snapshot.slug)
        try:
            self._scheduler.suspend = True
            await self.lock.acquire()

            async with snapshot:
                tasks = []

                if FOLDER_HOMEASSISTANT in folders:
                    await self._homeassistant.stop()

                if folders:
                    _LOGGER.info("Partial-Restore %s restore folders %s",
                                 snapshot.slug, folders)
                    await snapshot.restore_folders(folders)

                if homeassistant:
                    _LOGGER.info("Partial-Restore %s restore Home-Assistant",
                                 snapshot.slug)
                    snapshot.restore_homeassistant()
                    tasks.append(self._homeassistant.update(
                        snapshot.homeassistant_version))

                for slug in addons:
                    addon = self._addons.get(slug)
                    if addon:
                        tasks.append(snapshot.export_addon(addon))
                    else:
                        _LOGGER.warning("Can't restore addon %s",
                                        snapshot.slug)

                if tasks:
                    _LOGGER.info("Partial-Restore %s run %d tasks",
                                 snapshot.slug, len(tasks))
                    await asyncio.wait(tasks, loop=self._loop)

                # make sure homeassistant run agen
                await self._homeassistant.start()

        except (OSError, ValueError, tarfile.TarError) as err:
            _LOGGER.info("Partial-Restore %s error: %s", snapshot.slug, err)
            return False

        else:
            _LOGGER.info("Partial-Restore %s done", snapshot.slug)
            return True

        finally:
            self._scheduler.suspend = False
            self.lock.release()
