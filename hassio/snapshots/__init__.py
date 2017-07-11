"""Snapshot system control."""
import asyncio
from datetime import datetime
import logging
from pathlib import Path
import tarfile

from .snapshot import Snapshot
from .util import create_slug
from ..const import (
    ATTR_SLUG, FOLDER_HOMEASSISTANT, SNAPSHOT_FULL, SNAPSHOT_PARTIAL)

_LOGGER = logging.getLogger(__name__)


class SnapshotsManager(object):
    """Manage snapshots."""

    def __init__(self, config, loop, sheduler, addons, homeassistant):
        """Initialize a snapshot manager."""
        self.config = config
        self.loop = loop
        self.sheduler = sheduler
        self.addons = addons
        self.homeassistant = homeassistant
        self.snapshots = {}
        self._lock = asyncio.Lock(loop=loop)

    @property
    def list_snapshots(self):
        """Return a list of all snapshot object."""
        return set(self.snapshots.values())

    def get(self, slug):
        """Return snapshot object."""
        return self.snapshots.get(slug)

    def _create_snapshot(self, name, sys_type):
        """Initialize a new snapshot object from name."""
        date_str = str(datetime.utcnow())
        slug = create_slug(name, date_str)
        tar_file = Path(self.config.path_backup, "{}.tar".format(slug))

        # init object
        snapshot = Snapshot(self.config, self.loop, tar_file)
        snapshot.create(slug, name, date_str, sys_type)

        # set general data
        snapshot.homeassistant_version = self.homeassistant.version
        snapshot.homeassistant_devices = self.homeassistant.devices
        snapshot.repositories = self.config.addons_repositories

        return snapshot

    async def reload(self):
        """Load exists backups."""
        self.snapshots = {}

        async def _load_snapshot(tar_file):
            """Internal function to load snapshot."""
            snapshot = Snapshot(self.config, self.loop, tar_file)
            if await snapshot.load():
                self.snapshots[snapshot.slug] = snapshot

        tasks = [_load_snapshot(tar_file) for tar_file in
                 self.config.path_backup.glob("*.tar")]

        _LOGGER.info("Found %d snapshot files", len(tasks))
        if tasks:
            await asyncio.wait(tasks, loop=self.loop)

    def remove(self, snapshot):
        """Remove a snapshot."""
        try:
            snapshot.tar_file.unlink()
            self.snapshots.pop(snapshot.slug, None)
        except OSError as err:
            _LOGGER.error("Can't remove snapshot %s -> %s", snapshot.slug, err)
            return False

        return True

    async def do_snapshot_full(self, name=""):
        """Create a full snapshot."""
        if self._lock.locked():
            _LOGGER.error("It is already a snapshot/restore process running")
            return False

        snapshot = self._create_snapshot(name, SNAPSHOT_FULL)
        _LOGGER.info("Full-Snapshot %s start", snapshot.slug)
        try:
            self.sheduler.suspend = True
            await self._lock.acquire()

            async with snapshot:
                # snapshot addons
                tasks = []
                for addon in self.addons.list_addons:
                    if not addon.is_installed:
                        continue
                    tasks.append(snapshot.import_addon(addon))

                if tasks:
                    _LOGGER.info("Full-Snapshot %s run %d addons",
                                 snapshot.slug, len(tasks))
                    await asyncio.wait(tasks, loop=self.loop)

                # snapshot folders
                _LOGGER.info("Full-Snapshot %s store folders", snapshot.slug)
                await snapshot.store_folders()

            _LOGGER.info("Full-Snapshot %s done", snapshot.slug)
            self.snapshots[snapshot.slug] = snapshot
            return True

        except (OSError, ValueError, tarfile.TarError) as err:
            _LOGGER.info("Full-Snapshot %s error -> %s", snapshot.slug, err)
            return False

        finally:
            self.sheduler.suspend = False
            self._lock.release()

    async def do_snapshot_partial(self, name="", addons=None, folders=None):
        """Create a partial snapshot."""
        if self._lock.locked():
            _LOGGER.error("It is already a snapshot/restore process running")
            return False

        addons = addons or []
        folders = folders or []
        snapshot = self._create_snapshot(name, SNAPSHOT_PARTIAL)

        _LOGGER.info("Partial-Snapshot %s start", snapshot.slug)
        try:
            self.sheduler.suspend = True
            await self._lock.acquire()

            async with snapshot:
                # snapshot addons
                tasks = []
                for slug in addons:
                    addon = self.addons.get(slug)
                    if addon.is_installed:
                        tasks.append(snapshot.import_addon(addon))

                if tasks:
                    _LOGGER.info("Partial-Snapshot %s run %d addons",
                                 snapshot.slug, len(tasks))
                    await asyncio.wait(tasks, loop=self.loop)

                # snapshot folders
                _LOGGER.info("Partial-Snapshot %s store folders %s",
                             snapshot.slug, folders)
                await snapshot.store_folders(folders)

            _LOGGER.info("Partial-Snapshot %s done", snapshot.slug)
            self.snapshots[snapshot.slug] = snapshot
            return True

        except (OSError, ValueError, tarfile.TarError) as err:
            _LOGGER.info("Partial-Snapshot %s error -> %s", snapshot.slug, err)
            return False

        finally:
            self.sheduler.suspend = False
            self._lock.release()

    async def do_restore_full(self, snapshot):
        """Restore a snapshot."""
        if self._lock.locked():
            _LOGGER.error("It is already a snapshot/restore process running")
            return False

        if snapshot.sys_type != SNAPSHOT_FULL:
            _LOGGER.error(
                "Full-Restore %s is only a partial snapshot!", snapshot.slug)
            return False

        _LOGGER.info("Full-Restore %s start", snapshot.slug)
        try:
            self.sheduler.suspend = True
            await self._lock.acquire()

            async with snapshot:
                # stop system
                tasks = []
                tasks.append(self.homeassistant.stop())

                for addon in self.addons.list_addons:
                    if addon.is_installed:
                        tasks.append(addon.stop())

                await asyncio.wait(tasks, loop=self.loop)

                # restore folders
                _LOGGER.info("Full-Restore %s restore folders", snapshot.slug)
                await snapshot.restore_folders()

                # start homeassistant restore
                self.homeassistant.devices = snapshot.homeassistant_devices
                task_hass = self.loop.create_task(
                    self.homeassistant.update(snapshot.homeassistant_version))

                # restore repositories
                await self.addons.load_repositories(snapshot.repositories)

                # restore addons
                tasks = []
                actual_addons = \
                    set(addon.slug for addon in self.addons.list_addons
                        if addon.is_installed)
                restore_addons = \
                    set(data[ATTR_SLUG] for data in snapshot.addons)
                remove_addons = actual_addons - restore_addons

                _LOGGER.info("Full-Restore %s restore addons %s, remove %s",
                             snapshot.slug, restore_addons, remove_addons)

                for slug in remove_addons:
                    addon = self.addons.get(slug)
                    if addon:
                        tasks.append(addon.uninstall())
                    else:
                        _LOGGER.warning("Can't remove addon %s", slug)

                for slug in restore_addons:
                    addon = self.addons.get(slug)
                    if addon:
                        tasks.append(snapshot.export_addon(addon))
                    else:
                        _LOGGER.warning("Can't restore addon %s", slug)

                if tasks:
                    _LOGGER.info("Full-Restore %s restore addons tasks %d",
                                 snapshot.slug, len(tasks))
                    await asyncio.wait(tasks, loop=self.loop)

                # finish homeassistant task
                _LOGGER.info("Full-Restore %s wait until homeassistant ready",
                             snapshot.slug)
                await task_hass
                await self.homeassistant.run()

            _LOGGER.info("Full-Restore %s done", snapshot.slug)
            return True

        except (OSError, ValueError, tarfile.TarError) as err:
            _LOGGER.info("Full-Restore %s error -> %s", slug, err)
            return False

        finally:
            self.sheduler.suspend = False
            self._lock.release()

    async def do_restore_partial(self, snapshot, homeassistant=False,
                                 addons=None, folders=None):
        """Restore a snapshot."""
        if self._lock.locked():
            _LOGGER.error("It is already a snapshot/restore process running")
            return False

        addons = addons or []
        folders = folders or []

        _LOGGER.info("Partial-Restore %s start", snapshot.slug)
        try:
            self.sheduler.suspend = True
            await self._lock.acquire()

            async with snapshot:
                tasks = []

                if FOLDER_HOMEASSISTANT in folders:
                    await self.homeassistant.stop()

                if folders:
                    _LOGGER.info("Partial-Restore %s restore folders %s",
                                 snapshot.slug, folders)
                    await snapshot.restore_folders(folders)

                if homeassistant:
                    self.homeassistant.devices = snapshot.homeassistant_devices
                    tasks.append(self.homeassistant.update(
                        snapshot.homeassistant_version))

                for slug in addons:
                    addon = self.addons.get(slug)
                    if addon:
                        tasks.append(snapshot.export_addon(addon))
                    else:
                        _LOGGER.warning("Can't restore addon %s", slug)

                if tasks:
                    _LOGGER.info("Partial-Restore %s run %d tasks",
                                 snapshot.slug, len(tasks))
                    await asyncio.wait(tasks, loop=self.loop)

                # make sure homeassistant run agen
                await self.homeassistant.run()

            _LOGGER.info("Partial-Restore %s done", snapshot.slug)
            return True

        except (OSError, ValueError, tarfile.TarError) as err:
            _LOGGER.info("Partial-Restore %s error -> %s", slug, err)
            return False

        finally:
            self.sheduler.suspend = False
            self._lock.release()
