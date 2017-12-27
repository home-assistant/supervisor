"""Handle core shared data."""

import aiohttp

from .config import CoreConfig
from .dock import DockerAPI
from .dns import DNSForward
from .hardware import Hardware
from .host_control import HostControl
from .scheduler import Scheduler


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
        self._scheduler = Scheduler(loop=loop)
        self._dns = DNSForward(loop=loop)
        self._host_control = HostControl(loop=loop)

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
        """Return CoreConfig object."""
        return self._config

    @property
    def hardware(self):
        """Return Hardware object."""
        return self._hardware

    @property
    def docker(self):
        """Return DockerAPI object."""
        return self._docker

    @property
    def scheduler(self):
        """Return Scheduler object."""
        return self._scheduler

    @property
    def dns(self):
        """Return DNSForward object."""
        return self._dns

    @property
    def host_control(self):
        """Return HostControl object."""
        return self._host_control
