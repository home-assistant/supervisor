"""Snapshot system control."""
import asyncio
from datetime import datetime
from pathlib import Path
import tarfile

from .snapshot import Snapshot
from .util import create_slug
from ..const import FOLDER_CONFIG


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

    @property
    def list_snapshots(self):
        """Return a list of all snapshot object."""
        return set(self.snapshots.values())

    @property
    def get(self, slug):
        """Return snapshot object."""
        return self.snapshots.get(slug)

    async def prepare(self):
        """Load exists backups."""
        async def _load_snapshot(tar_file):
            """Internal function to load snapshot."""
            snapshot = Snapshot(self.config, self.loop, tar_file)
            if await snapshot.load():
                self.snapshots[snapshot.slug] = snapshot

        tasks = [_load_snapshot(tar_file) for tar_file in
                 self.config.path_backup.glob("*.tar.xz")]

        _LOGGER.info("Found %d snapshot files", len(tasks))
        if tasks:
            await asyncio.wait(tasks, loop=self.loop)

    async def do_snapshot(self, name):
        """Create a snapshot."""
        date_str = str(datetime.utcnow())
        slug = create_slug(name, date_str)
        tar_file Path(self.config.path_backup, "{}.tar.xz".foramt(slug))
        snapshot = Snapshot(self.config, self.loop, tar_file)

        _LOGGER.info("Snapshot %s start", slug)
        try:
            self.sheduler.suspend = True
            await with snapshot:
                snapshot.create(slug, name, date_str)
                snapshot.homeassistant = homeassistant.version
                snapshot.repositories = self.config.addons_repositories

                # snapshot addons
                tasks = []
                for addon in addons.list_addons:
                    if not addon.is_installed:
                        continue
                    tasks.append(snapshot.import_addon(addon))

                _LOGGER.info("Snapshot %d addons on %s", len(tasks), slug)
                if tasks:
                    await asyncio.wait(tasks, loop=self.loop)

                # snapshot folders
                _LOGGER.info("Snapshot all hassio folders on %s", slug)
                await snapshot.store_folders()

            _LOGGER.info("Snapshot %s done", slug)
            self.snapshots.append(snapshot)
            return True

        except (OSError, tarfile.TarError) as err:
            _LOGGER.info("Snapshot %s error -> %s", slug, err)
            return False

        finally:
            self.sheduler.suspend = False

    async def do_restore(self, snapshot):
        """Restore a snapshot."""
        _LOGGER.info("Full-Restore %s start", snapshot.slug)
        try:
            self.sheduler.suspend = True
            await with snapshot:
                # stop system
                tasks = []
                tasks.append(self.homeassistant.stop())

                for addon in self.addons.list_addons:
                    if addon.is_installed:
                        tasks.append(addon.stop())

                await asyncio.wait(tasks, loop=self.loop)

                # restore folders
                await snapshot.restore_folders()

                # start homeassistant restore
                task_hass = self.loop.create_task(
                    self.homeassistant.update(snapshot.homeassistant))

                # restore repositories
                await self.addons.laod_repositories(snapshot.repositories)

                # restore addons
                tasks = []
                actual_addons = (addon.slug for addon in
                                 self.addons.list_addons if addon.is_installed)
                restor_addons = set(snapshot.addons.keys())
                remove_addons = actual_addons - restor_addons

                for slug in remove_addons:
                    addon = self.addons.get(slug)
                    if addon:
                        tasks.append(addon.uninstall())
                    else:
                        _LOGGER.warning("Can't remove addon %s", slug)

                for addon in restor_addons:
                    addon = self.addons.get(slug)
                    if addon:
                        tasks.append(snapshot.export_addon(addon))
                    else:
                        _LOGGER.warning("Can't restore addon %s", slug)

                if tasks:
                    await asyncio.wait(tasks, loop=self.loop)

                # finish homeassistant task
                await task_hass
                await self.homeassistant.run()

            _LOGGER.info("Full-Restore %s done", snapshot.slug)
            return True

        except (OSError, tarfile.TarError) as err:
            _LOGGER.info("Full-Restore %s error -> %s", slug, err)
            return False

        finally:
            self.sheduler.suspend = False

    async def do_pickup(self, snapshot, options):
        """Restore a snapshot."""
        _LOGGER.info("Pick-Restore %s start", snapshot.slug)
        try:
            self.sheduler.suspend = True
            await with snapshot:
                tasks = []

                if FOLDER_CONFIG in options.get(ATTR_FOLDERS, {}):
                    await self.homeassistant.stop()

                if options.get(ATTR_FOLDERS):
                    await snapshot.restore_folders(options[ATTR_FOLDERS])

                if options.get(ATTR_HOMEASSISTANT):
                    tasks.append(self.homeassistant.update(
                        snapshot.homeassistant))

                if options.get(ATTR_ADDONS):
                    for slug in options[ATTR_ADDONS]:
                        addon = self.addons.get(slug)
                        if addon:
                            tasks.append(snapshot.export_addon(addon))
                        else:
                            _LOGGER.warning("Can't restore addon %s", slug)

                if tasks:
                    await asyncio.wait(tasks, loop=self.loop)

            _LOGGER.info("Pick-Restore %s done", snapshot.slug)
            return True

        except (OSError, tarfile.TarError) as err:
            _LOGGER.info("Pick-Restore %s error -> %s", slug, err)
            return False

        finally:
            self.sheduler.suspend = False
