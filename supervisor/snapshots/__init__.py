"""Snapshot system control."""
import asyncio
import logging
from pathlib import Path

from ..const import FOLDER_HOMEASSISTANT, SNAPSHOT_FULL, SNAPSHOT_PARTIAL, CoreState
from ..coresys import CoreSysAttributes
from ..exceptions import AddonsError
from ..utils.dt import utcnow
from .snapshot import Snapshot
from .utils import create_slug

_LOGGER: logging.Logger = logging.getLogger(__name__)


class SnapshotManager(CoreSysAttributes):
    """Manage snapshots."""

    def __init__(self, coresys):
        """Initialize a snapshot manager."""
        self.coresys = coresys
        self.snapshots_obj = {}
        self.lock = asyncio.Lock()

    @property
    def list_snapshots(self):
        """Return a list of all snapshot object."""
        return set(self.snapshots_obj.values())

    def get(self, slug):
        """Return snapshot object."""
        return self.snapshots_obj.get(slug)

    def _create_snapshot(self, name, sys_type, password):
        """Initialize a new snapshot object from name."""
        date_str = utcnow().isoformat()
        slug = create_slug(name, date_str)
        tar_file = Path(self.sys_config.path_backup, f"{slug}.tar")

        # init object
        snapshot = Snapshot(self.coresys, tar_file)
        snapshot.new(slug, name, date_str, sys_type, password)

        # set general data
        snapshot.store_homeassistant()
        snapshot.store_repositories()
        snapshot.store_dockerconfig()

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
            """Load the snapshot."""
            snapshot = Snapshot(self.coresys, tar_file)
            if await snapshot.load():
                self.snapshots_obj[snapshot.slug] = snapshot

        tasks = [
            _load_snapshot(tar_file)
            for tar_file in self.sys_config.path_backup.glob("*.tar")
        ]

        _LOGGER.info("Found %d snapshot files", len(tasks))
        if tasks:
            await asyncio.wait(tasks)

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
            return None

        # Already exists?
        if snapshot.slug in self.snapshots_obj:
            _LOGGER.error("Snapshot %s already exists!", snapshot.slug)
            return None

        # Move snapshot to backup
        tar_origin = Path(self.sys_config.path_backup, f"{snapshot.slug}.tar")
        try:
            snapshot.tarfile.rename(tar_origin)

        except OSError as err:
            _LOGGER.error("Can't move snapshot file to storage: %s", err)
            return None

        # Load new snapshot
        snapshot = Snapshot(self.coresys, tar_origin)
        if not await snapshot.load():
            return None
        _LOGGER.info("Success import %s", snapshot.slug)

        self.snapshots_obj[snapshot.slug] = snapshot
        return snapshot

    async def do_snapshot_full(self, name="", password=None):
        """Create a full snapshot."""
        if self.lock.locked():
            _LOGGER.error("A snapshot/restore process is already running")
            return None

        snapshot = self._create_snapshot(name, SNAPSHOT_FULL, password)
        _LOGGER.info("Full-Snapshot %s start", snapshot.slug)
        try:
            self.sys_core.state = CoreState.FREEZE
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
            return None

        else:
            _LOGGER.info("Full-Snapshot %s done", snapshot.slug)
            self.snapshots_obj[snapshot.slug] = snapshot
            return snapshot

        finally:
            self.sys_core.state = CoreState.RUNNING
            self.lock.release()

    async def do_snapshot_partial(
        self, name="", addons=None, folders=None, password=None
    ):
        """Create a partial snapshot."""
        if self.lock.locked():
            _LOGGER.error("A snapshot/restore process is already running")
            return None

        addons = addons or []
        folders = folders or []
        snapshot = self._create_snapshot(name, SNAPSHOT_PARTIAL, password)

        _LOGGER.info("Partial-Snapshot %s start", snapshot.slug)
        try:
            self.sys_core.state = CoreState.FREEZE
            await self.lock.acquire()

            async with snapshot:
                # Snapshot add-ons
                addon_list = []
                for addon_slug in addons:
                    addon = self.sys_addons.get(addon_slug)
                    if addon and addon.is_installed:
                        addon_list.append(addon)
                        continue
                    _LOGGER.warning("Add-on %s not found/installed", addon_slug)

                if addon_list:
                    _LOGGER.info("Snapshot %s store Add-ons", snapshot.slug)
                    await snapshot.store_addons(addon_list)

                # Snapshot folders
                if folders:
                    _LOGGER.info("Snapshot %s store folders", snapshot.slug)
                    await snapshot.store_folders(folders)

        except Exception:  # pylint: disable=broad-except
            _LOGGER.exception("Snapshot %s error", snapshot.slug)
            return None

        else:
            _LOGGER.info("Partial-Snapshot %s done", snapshot.slug)
            self.snapshots_obj[snapshot.slug] = snapshot
            return snapshot

        finally:
            self.sys_core.state = CoreState.RUNNING
            self.lock.release()

    async def do_restore_full(self, snapshot, password=None):
        """Restore a snapshot."""
        if self.lock.locked():
            _LOGGER.error("A snapshot/restore process is already running")
            return False

        if snapshot.sys_type != SNAPSHOT_FULL:
            _LOGGER.error("Restore %s is only a partial snapshot!", snapshot.slug)
            return False

        if snapshot.protected and not snapshot.set_password(password):
            _LOGGER.error("Invalid password for snapshot %s", snapshot.slug)
            return False

        _LOGGER.info("Full-Restore %s start", snapshot.slug)
        try:
            self.sys_core.state = CoreState.FREEZE
            await self.lock.acquire()

            async with snapshot:
                # Stop Home-Assistant / Add-ons
                await self.sys_core.shutdown()

                # Restore folders
                _LOGGER.info("Restore %s run folders", snapshot.slug)
                await snapshot.restore_folders()

                # Start homeassistant restore
                _LOGGER.info("Restore %s run Home-Assistant", snapshot.slug)
                snapshot.restore_homeassistant()
                task_hass = self.sys_create_task(
                    self.sys_homeassistant.core.update(snapshot.homeassistant_version)
                )

                # Restore docker config
                _LOGGER.info("Restore %s run Docker Config", snapshot.slug)
                await snapshot.restore_dockerconfig()

                # Restore repositories
                _LOGGER.info("Restore %s run Repositories", snapshot.slug)
                await snapshot.restore_repositories()

                # Delete delta add-ons
                _LOGGER.info("Restore %s remove add-ons", snapshot.slug)
                for addon in self.sys_addons.installed:
                    if addon.slug in snapshot.addon_list:
                        continue

                    # Remove Add-on because it's not a part of the new env
                    # Do it sequential avoid issue on slow IO
                    try:
                        await addon.uninstall()
                    except AddonsError:
                        _LOGGER.warning("Can't uninstall Add-on %s", addon.slug)

                # Restore add-ons
                _LOGGER.info("Restore %s old add-ons", snapshot.slug)
                await snapshot.restore_addons()

                # finish homeassistant task
                _LOGGER.info("Restore %s wait until homeassistant ready", snapshot.slug)
                await task_hass
                await self.sys_homeassistant.core.start()

        except Exception:  # pylint: disable=broad-except
            _LOGGER.exception("Restore %s error", snapshot.slug)
            return False

        else:
            _LOGGER.info("Full-Restore %s done", snapshot.slug)
            return True

        finally:
            self.sys_core.state = CoreState.RUNNING
            self.lock.release()

    async def do_restore_partial(
        self, snapshot, homeassistant=False, addons=None, folders=None, password=None
    ):
        """Restore a snapshot."""
        if self.lock.locked():
            _LOGGER.error("A snapshot/restore process is already running")
            return False

        if snapshot.protected and not snapshot.set_password(password):
            _LOGGER.error("Invalid password for snapshot %s", snapshot.slug)
            return False

        addons = addons or []
        folders = folders or []

        _LOGGER.info("Partial-Restore %s start", snapshot.slug)
        try:
            self.sys_core.state = CoreState.FREEZE
            await self.lock.acquire()

            async with snapshot:
                # Stop Home-Assistant for config restore
                if FOLDER_HOMEASSISTANT in folders:
                    await self.sys_homeassistant.core.stop()
                    snapshot.restore_homeassistant()
                    snapshot.restore_dockerconfig()

                # Process folders
                if folders:
                    _LOGGER.info("Restore %s run folders", snapshot.slug)
                    await snapshot.restore_folders(folders)

                # Process Home-Assistant
                task_hass = None
                if homeassistant:
                    _LOGGER.info("Restore %s run Home-Assistant", snapshot.slug)
                    task_hass = self.sys_create_task(
                        self.sys_homeassistant.core.update(
                            snapshot.homeassistant_version
                        )
                    )

                if addons:
                    _LOGGER.info("Restore %s run Repositories", snapshot.slug)
                    await snapshot.restore_repositories()

                    _LOGGER.info("Restore %s old add-ons", snapshot.slug)
                    await snapshot.restore_addons(addons)

                # Make sure homeassistant run agen
                if task_hass:
                    _LOGGER.info("Restore %s wait for Home-Assistant", snapshot.slug)
                    await task_hass

                # Do we need start HomeAssistant?
                if not await self.sys_homeassistant.core.is_running():
                    await self.sys_homeassistant.core.start()

                # Check If we can access to API / otherwise restart
                if not await self.sys_homeassistant.api.check_api_state():
                    _LOGGER.warning("Need restart HomeAssistant for API")
                    await self.sys_homeassistant.core.restart()

        except Exception:  # pylint: disable=broad-except
            _LOGGER.exception("Restore %s error", snapshot.slug)
            return False

        else:
            _LOGGER.info("Partial-Restore %s done", snapshot.slug)
            return True

        finally:
            self.sys_core.state = CoreState.RUNNING
            self.lock.release()
