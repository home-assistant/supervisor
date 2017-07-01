"""Represent a snapshot file."""
import json
import logging
import tarfile
from tempfile import TemporaryDirectory

from .const import (
    ATTR_SLUG, ATTR_NAME, ATTR_DATE, ATTR_ADDONS, ATTR_REPOSITORIES)
from .tools import write_json_file

_LOGGER = logging.getLogger(__name__)


class Snapshot(object):
    """A signle hassio snapshot."""

    def __init__(self, loop, tar_file):
        """Initialize a snapshot."""
        self.loop = loop
        self.tar_file = tar_file
        self._data = {}

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

    @property
    def size(self):
        """Return snapshot size."""
        if not self.tar_file.is_file():
            return 0
        return self.tar_file.stat().st_size / 1048576  # calc mbyte

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

        # parse data
        try:
            self._data = json.loads(raw)
        except json.JSONDecodeError as err:
            _LOGGER.error("Can't read data for %s -> %s", self.tar_file, err)
            return False

        return True
