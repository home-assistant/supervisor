"""Represent a snapshot file."""
import asyncio
import json
import logging
from pathlib import Path, PurePath
import shutil
import tarfile
from tempfile import TemporaryDirectory

import voluptuous as vol
from voluptuous.humanize import humanize_error

from .validate import SCHEMA_SNAPSHOT
from ..const import (
    ATTR_SLUG, ATTR_NAME, ATTR_DATE, ATTR_ADDONS, ATTR_REPOSITORIES,
    ATTR_HOMEASSISTANT)
from ..tools import write_json_file

_LOGGER = logging.getLogger(__name__)

HASSIO_PATH_LIST = (('config', 'share'))


class Snapshot(object):
    """A signle hassio snapshot."""

    def __init__(self, config, loop, tar_file):
        """Initialize a snapshot."""
        self.loop = loop
        self.config = config
        self.tar_file = tar_file
        self._data = {}
        self._tmp = None

    @property
    def slug(self):
        """Return snapshot slug."""
        return self._data.get(ATTR_SLUG)

    @property
    def name(self):
        """Return snapshot name."""
        return self._data.get(ATTR_NAME)

    @property
    def date(self):
        """Return snapshot date."""
        return self._data.get(ATTR_DATE)

    @property
    def addons(self):
        """Return snapshot date."""
        return self._data.get(ATTR_ADDONS)

    @property
    def repositories(self):
        """Return snapshot date."""
        return self._data.get(ATTR_REPOSITORIES)

    @repositories.setter
    def repositories(self, value):
        """Set snapshot date."""
        self._data[ATTR_REPOSITORIES] = value

    @property
    def homeassistant(self):
        """Return snapshot homeassistant version."""
        return self._data.get(ATTR_HOMEASSISTANT)

    @homeassistant.setter
    def homeassistant(self, value):
        """Set snapshot homeassistant version."""
        self._data[ATTR_HOMEASSISTANT] = value

    @property
    def size(self):
        """Return snapshot size."""
        if not self.tar_file.is_file():
            return 0
        return self.tar_file.stat().st_size / 1048576  # calc mbyte

    def create(self, slug, name, date):
        """Initialize a new snapshot."""
        # init metadata
        self._data[ATTR_SLUG] = slug
        self._data[ATTR_NAME] = name
        self._data[ATTR_DATE] = date

        # init other constructs
        self._data[ATTR_ADDONS] = []
        self._data[ATTR_REPOSITORIES] = []

    async def load(self):
        """Read snapshot.json from tar file."""
        if not self.tar_file.is_file():
            _LOGGER.error("No tarfile %s", self.tar_file)
            return False

        def _load_file():
            """Read snapshot.json."""
            with tarfile.open(self.tar_file, "r:xz") as snapshot:
                json_file = snapshot.extractfile("snapshot.json")
            if json_file:
                return json_file.read()

        # read snapshot.json
        try:
            raw = await self.loop.run_in_executor(None, _load_file)
        except tarfile.TarError as err:
            _LOGGER.error(
                "Can't read snapshot tarfile %s -> %s", self.tar_file, err)
            return False

        # parse data
        try:
            raw_dict = json.loads(raw)
        except json.JSONDecodeError as err:
            _LOGGER.error("Can't read data for %s -> %s", self.tar_file, err)
            return False

        # validate
        try:
            raw_dict = SCHEMA_SNAPSHOT(raw_dict)
        except vol.Invalid as err:
            _LOGGER.error("Can't validate data for %s -> %s", self.tar_file,
                          humanize_error(raw_dict, err))
            return False

        return True

    async def __aenter__(self):
        """Async context to open a snapshot."""
        self._tmp = TemporaryDirectory(dir=str(self.config.path_tmp))

        # create a snapshot
        if not self.tar_file.is_file():
            return self

        # extract a exists snapshot
        def _extract_snapshot():
            """Extract a snapshot."""
            with tarfile.open(self.tar_file, "r:xz") as tar:
                tar.extractall(path=self._tmp.name)

        await self.loop.run_in_executor(None, _extract_snapshot)

    async def __aexit__(self):
        """Async context to close a snapshot."""
        # exists snapshot, close
        if self.tar_file.is_file():
            return self._tmp.cleanup()

        # new snapshot, build it
        def _create_snapshot():
            """Create a new snapshot."""
            with tarfile.open(self.tar_file, "w:xz") as tar:
                tar.add(self._tmp.name, arcname=".")

        await self.loop.run_in_executor(None, _create_snapshot)

    async def import_addon(self, addon):
        """Add a addon into snapshot."""
        snapshot_file = Path(self._tmp, "{}.tar.xz".format(addon.slug))

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
        snapshot_file = Path(self._tmp, "{}.tar.xz".format(addon.slug))

        if not await addon.restore(snapshot_file):
            _LOGGER.error("Can't restore snapshot for %s", addon.slug)
            return False

        return True

    async def store_folders(self):
        """Backup hassio data into snapshot."""
        def _folder_save(name):
            """Intenal function to snapshot a folder."""
            snapshot_dir = Path(self._tmp, name)
            origin_dir = Path(self.config.path_hassio, name)

            try:
                shutil.copytree(str(origin_dir), str(snapshot_dir))
            except shutil.Error as err:
                _LOGGER.warning("Can't snapshot folder %s -> %s", name, err)

        # run tasks
        tasks = [self.loop.run_in_executor(None, _folder_save, folder)
                 for folder in HASSIO_PATH_LIST]
        if tasks:
            await asyncio.wait(tasks, loop=self.loop)

    async def restore_folders(self):
        """Backup hassio data into snapshot."""
        def _folder_restore(name):
            """Intenal function to restore a folder."""
            snapshot_dir = Path(self._tmp, name)
            origin_dir = Path(self.config.path_hassio, name)

            # clean old stuff
            if origin_dir.is_dir():
                shutil.rmtree(str(origin_dir), ignore_errors=True)

            try:
                shutil.copytree(str(snapshot_dir), str(origin_dir))
            except shutil.Error as err:
                _LOGGER.warning("Can't restore folder %s -> %s", name, err)

        # run tasks
        tasks = [self.loop.run_in_executor(None, _folder_restore, folder)
                 for folder in HASSIO_PATH_LIST]
        if tasks:
            await asyncio.wait(tasks, loop=self.loop)
