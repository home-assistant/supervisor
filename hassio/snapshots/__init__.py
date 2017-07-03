"""Snapshot system control."""
import asyncio
from datetime import datetime
from pathlib import Path

from .snapshot import Snapshot
from .util import create_slug


class SnapshotsManager(object):
    """Manage snapshots."""

    def __init__(self, config, loop, addons, homeassistant):
        """Initialize a snapshot manager."""
        self.config = config
        self.loop = loop
        self.addons = addons
        self.homeassistant = homeassistant
        self.snapshots = {}

    @property
    def list_snapshots(self):
        return set(self.snapshots.values())

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
        await with snapshot:
            snapshot.create(slug, name, date_str)

            # snapshot addons
            tasks = []
            for addon in addons.list_addons:
                if not addon.is_installed:
                    continue
                tasks.append(snapshot.import_addon(addon))

            _LOGGER.info("Snapshot %d addons on %s", len(tasks), slug)
            if tasks:
                await asyncio.wait(tasks, loop=self.loop)

            # snapshot metadata
            snapshot.homeassistant = homeassistant.version
            snapshot.repositories = self.config.addons_repositories

            # snapshot folders
            await snapshot.store_folders()

        self.snapshots.append(snapshot)

    async def do_restore(self):
        """Restore a snapshot."""
