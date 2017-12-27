"""Handle core shared data."""

import aiohttp

from .config import CoreConfig
from .hardware import Hardware
from .dock import DockerAPI


class CoreSys(object):
    """Class that handle all shared data."""

    def __init__(self, loop):
        """Initialize coresys."""
        # Static attributes
        self.exit_code = 0
        self.arch = None

        # External objects
        self._loop = loop
        self._websession = aiohttp.ClientSession(loop=loop)

        # Internal objects
        self._config = CoreConfig()
        self._hardware = Hardware()
        self._docker = DockerAPI()

    @property
    def loop(self):
        """Return loop object."""
        return self._loop

    @property
    def websession(self):
        """Return websession object."""
        return self._websession

    @property
    def config(self):
        """Return config object."""
        return self._config

    @property
    def hardware(self):
        """Return hardware object."""
        return self._hardware

    @property
    def docker(self):
        """Return docker object."""
        return self._docker
