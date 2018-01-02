"""Represent a snapshot file."""
import asyncio
import json
import logging
from pathlib import Path
import tarfile
from tempfile import TemporaryDirectory

import voluptuous as vol
from voluptuous.humanize import humanize_error

from .validate import SCHEMA_SNAPSHOT, ALL_FOLDERS
from .utils import remove_folder
from ..const import (
    ATTR_SLUG, ATTR_NAME, ATTR_DATE, ATTR_ADDONS, ATTR_REPOSITORIES,
    ATTR_HOMEASSISTANT, ATTR_FOLDERS, ATTR_VERSION, ATTR_TYPE, ATTR_DEVICES,
    ATTR_IMAGE, ATTR_PORT, ATTR_SSL, ATTR_PASSWORD, ATTR_WATCHDOG, ATTR_BOOT)
from ..coresys import CoreSysAttributes
from ..utils.json import write_json_file

_LOGGER = logging.getLogger(__name__)


class Snapshot(CoreSysAttributes):
    """A signle hassio snapshot."""

    def __init__(self, coresys, tar_file):
        """Initialize a snapshot."""
        self.coresys = coresys
        self.tar_file = tar_file
        self._data = {}
        self._tmp = None

    @property
    def slug(self):
        """Return snapshot slug."""
        return self._data.get(ATTR_SLUG)

    @property
    def sys_type(self):
        """Return snapshot type."""
        return self._data.get(ATTR_TYPE)

    @property
    def name(self):
        """Return snapshot name."""
        return self._data[ATTR_NAME]

    @property
    def date(self):
        """Return snapshot date."""
        return self._data[ATTR_DATE]

    @property
    def addons(self):
        """Return snapshot date."""
        return self._data[ATTR_ADDONS]

    @property
    def folders(self):
        """Return list of saved folders."""
        return self._data[ATTR_FOLDERS]

    @property
    def repositories(self):
        """Return snapshot date."""
        return self._data[ATTR_REPOSITORIES]

    @repositories.setter
    def repositories(self, value):
        """Set snapshot date."""
        self._data[ATTR_REPOSITORIES] = value

    @property
    def homeassistant_version(self):
        """Return snapshot homeassistant version."""
        return self._data[ATTR_HOMEASSISTANT].get(ATTR_VERSION)

    @homeassistant_version.setter
    def homeassistant_version(self, value):
        """Set snapshot homeassistant version."""
        self._data[ATTR_HOMEASSISTANT][ATTR_VERSION] = value

    @property
    def homeassistant_devices(self):
        """Return snapshot homeassistant devices."""
        return self._data[ATTR_HOMEASSISTANT].get(ATTR_DEVICES)

    @homeassistant_devices.setter
    def homeassistant_devices(self, value):
        """Set snapshot homeassistant devices."""
        self._data[ATTR_HOMEASSISTANT][ATTR_DEVICES] = value

    @property
    def homeassistant_image(self):
        """Return snapshot homeassistant custom image."""
        return self._data[ATTR_HOMEASSISTANT].get(ATTR_IMAGE)

    @homeassistant_image.setter
    def homeassistant_image(self, value):
        """Set snapshot homeassistant custom image."""
        self._data[ATTR_HOMEASSISTANT][ATTR_IMAGE] = value

    @property
    def homeassistant_ssl(self):
        """Return snapshot homeassistant api ssl."""
        return self._data[ATTR_HOMEASSISTANT].get(ATTR_SSL)

    @homeassistant_ssl.setter
    def homeassistant_ssl(self, value):
        """Set snapshot homeassistant api ssl."""
        self._data[ATTR_HOMEASSISTANT][ATTR_SSL] = value

    @property
    def homeassistant_port(self):
        """Return snapshot homeassistant api port."""
        return self._data[ATTR_HOMEASSISTANT].get(ATTR_PORT)

    @homeassistant_port.setter
    def homeassistant_port(self, value):
        """Set snapshot homeassistant api port."""
        self._data[ATTR_HOMEASSISTANT][ATTR_PORT] = value

    @property
    def homeassistant_password(self):
        """Return snapshot homeassistant api password."""
        return self._data[ATTR_HOMEASSISTANT].get(ATTR_PASSWORD)

    @homeassistant_password.setter
    def homeassistant_password(self, value):
        """Set snapshot homeassistant api password."""
        self._data[ATTR_HOMEASSISTANT][ATTR_PASSWORD] = value

    @property
    def homeassistant_watchdog(self):
        """Return snapshot homeassistant watchdog options."""
        return self._data[ATTR_HOMEASSISTANT].get(ATTR_WATCHDOG)

    @homeassistant_watchdog.setter
    def homeassistant_watchdog(self, value):
        """Set snapshot homeassistant watchdog options."""
        self._data[ATTR_HOMEASSISTANT][ATTR_WATCHDOG] = value

    @property
    def homeassistant_boot(self):
        """Return snapshot homeassistant boot options."""
        return self._data[ATTR_HOMEASSISTANT].get(ATTR_BOOT)

    @homeassistant_boot.setter
    def homeassistant_boot(self, value):
        """Set snapshot homeassistant boot options."""
        self._data[ATTR_HOMEASSISTANT][ATTR_BOOT] = value

    @property
    def size(self):
        """Return snapshot size."""
        if not self.tar_file.is_file():
            return 0
        return self.tar_file.stat().st_size / 1048576  # calc mbyte

    def create(self, slug, name, date, sys_type):
        """Initialize a new snapshot."""
        # init metadata
        self._data[ATTR_SLUG] = slug
        self._data[ATTR_NAME] = name
        self._data[ATTR_DATE] = date
        self._data[ATTR_TYPE] = sys_type

        # Add defaults
        self._data = SCHEMA_SNAPSHOT(self._data)

    async def load(self):
        """Read snapshot.json from tar file."""
        if not self.tar_file.is_file():
            _LOGGER.error("No tarfile %s", self.tar_file)
            return False

        def _load_file():
            """Read snapshot.json."""
            with tarfile.open(self.tar_file, "r:") as snapshot:
                json_file = snapshot.extractfile("./snapshot.json")
                return json_file.read()

        # read snapshot.json
        try:
            raw = await self._loop.run_in_executor(None, _load_file)
        except (tarfile.TarError, KeyError) as err:
            _LOGGER.error(
                "Can't read snapshot tarfile %s: %s", self.tar_file, err)
            return False

        # parse data
        try:
            raw_dict = json.loads(raw)
        except json.JSONDecodeError as err:
            _LOGGER.error("Can't read data for %s: %s", self.tar_file, err)
            return False

        # validate
        try:
            self._data = SCHEMA_SNAPSHOT(raw_dict)
        except vol.Invalid as err:
            _LOGGER.error("Can't validate data for %s: %s", self.tar_file,
                          humanize_error(raw_dict, err))
            return False

        return True

    async def __aenter__(self):
        """Async context to open a snapshot."""
        self._tmp = TemporaryDirectory(dir=str(self._config.path_tmp))

        # create a snapshot
        if not self.tar_file.is_file():
            return self

        # extract a exists snapshot
        def _extract_snapshot():
            """Extract a snapshot."""
            with tarfile.open(self.tar_file, "r:") as tar:
                tar.extractall(path=self._tmp.name)

        await self._loop.run_in_executor(None, _extract_snapshot)

    async def __aexit__(self, exception_type, exception_value, traceback):
        """Async context to close a snapshot."""
        # exists snapshot or exception on build
        if self.tar_file.is_file() or exception_type is not None:
            self._tmp.cleanup()
            return

        # validate data
        try:
            self._data = SCHEMA_SNAPSHOT(self._data)
        except vol.Invalid as err:
            _LOGGER.error("Invalid data for %s: %s", self.tar_file,
                          humanize_error(self._data, err))
            raise ValueError("Invalid config") from None

        # new snapshot, build it
        def _create_snapshot():
            """Create a new snapshot."""
            with tarfile.open(self.tar_file, "w:") as tar:
                tar.add(self._tmp.name, arcname=".")

        if write_json_file(Path(self._tmp.name, "snapshot.json"), self._data):
            await self._loop.run_in_executor(None, _create_snapshot)
        else:
            _LOGGER.error("Can't write snapshot.json")

        self._tmp.cleanup()

    async def import_addon(self, addon):
        """Add a addon into snapshot."""
        snapshot_file = Path(self._tmp.name, "{}.tar.gz".format(addon.slug))

        if not await addon.snapshot(snapshot_file):
            _LOGGER.error("Can't make snapshot from %s", addon.slug)
            return False

        # store to config
        self._data[ATTR_ADDONS].append({
            ATTR_SLUG: addon.slug,
            ATTR_NAME: addon.name,
            ATTR_VERSION: addon.version_installed,
        })

        return True

    async def export_addon(self, addon):
        """Restore a addon from snapshot."""
        snapshot_file = Path(self._tmp.name, "{}.tar.gz".format(addon.slug))

        if not await addon.restore(snapshot_file):
            _LOGGER.error("Can't restore snapshot for %s", addon.slug)
            return False

        return True

    async def store_folders(self, folder_list=None):
        """Backup hassio data into snapshot."""
        folder_list = folder_list or ALL_FOLDERS

        def _folder_save(name):
            """Intenal function to snapshot a folder."""
            slug_name = name.replace("/", "_")
            snapshot_tar = Path(self._tmp.name, "{}.tar.gz".format(slug_name))
            origin_dir = Path(self._config.path_hassio, name)

            try:
                _LOGGER.info("Snapshot folder %s", name)
                with tarfile.open(snapshot_tar, "w:gz",
                                  compresslevel=1) as tar_file:
                    tar_file.add(origin_dir, arcname=".")
                    _LOGGER.info("Snapshot folder %s done", name)

                self._data[ATTR_FOLDERS].append(name)
            except tarfile.TarError as err:
                _LOGGER.warning("Can't snapshot folder %s: %s", name, err)

        # run tasks
        tasks = [self._loop.run_in_executor(None, _folder_save, folder)
                 for folder in folder_list]
        if tasks:
            await asyncio.wait(tasks, loop=self._loop)

    async def restore_folders(self, folder_list=None):
        """Backup hassio data into snapshot."""
        folder_list = folder_list or ALL_FOLDERS

        def _folder_restore(name):
            """Intenal function to restore a folder."""
            slug_name = name.replace("/", "_")
            snapshot_tar = Path(self._tmp.name, "{}.tar.gz".format(slug_name))
            origin_dir = Path(self._config.path_hassio, name)

            # clean old stuff
            if origin_dir.is_dir():
                remove_folder(origin_dir)

            try:
                _LOGGER.info("Restore folder %s", name)
                with tarfile.open(snapshot_tar, "r:gz") as tar_file:
                    tar_file.extractall(path=origin_dir)
                    _LOGGER.info("Restore folder %s done", name)
            except tarfile.TarError as err:
                _LOGGER.warning("Can't restore folder %s: %s", name, err)

        # run tasks
        tasks = [self._loop.run_in_executor(None, _folder_restore, folder)
                 for folder in folder_list]
        if tasks:
            await asyncio.wait(tasks, loop=self._loop)

    def store_homeassistant(self):
        """Read all data from homeassistant object."""
        self.homeassistant_version = self._homeassistant.version
        self.homeassistant_devices = self._homeassistant.devices
        self.homeassistant_watchdog = self._homeassistant.watchdog
        self.homeassistant_boot = self._homeassistant.boot

        # custom image
        if self._homeassistant.is_custom_image:
            self.homeassistant_image = self._homeassistant.image

        # api
        self.homeassistant_port = self._homeassistant.api_port
        self.homeassistant_ssl = self._homeassistant.api_ssl
        self.homeassistant_password = self._homeassistant.api_password

    def restore_homeassistant(self):
        """Write all data to homeassistant object."""
        self._homeassistant.devices = self.homeassistant_devices
        self._homeassistant.watchdog = self.homeassistant_watchdog
        self._homeassistant.boot = self.homeassistant_boot

        # custom image
        if self.homeassistant_image:
            self._homeassistant.set_custom(
                self.homeassistant_image, self.homeassistant_version)

        # api
        self._homeassistant.api_port = self.homeassistant_port
        self._homeassistant.api_ssl = self.homeassistant_ssl
        self._homeassistant.api_password = self.homeassistant_password

    def store_repositories(self):
        """Store repository list into snapshot."""
        self.repositories = self._config.addons_repositories

    async def restore_repositories(self):
        """Restore repositories from snapshot."""
        await self._addons.load_repositories(self.repositories)
