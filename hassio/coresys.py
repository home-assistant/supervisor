"""Handle core shared data."""

import aiohttp

from .config import CoreConfig
from .docker import DockerAPI
from .misc.dns import DNSForward
from .misc.hardware import Hardware
from .misc.host_control import HostControl
from .misc.scheduler import Scheduler


class CoreSys(object):
    """Class that handle all shared data."""

    def __init__(self, loop):
        """Initialize coresys."""
        # Static attributes
        self.exit_code = 0

        # External objects
        self._loop = loop
        self._websession = aiohttp.ClientSession(loop=loop)
        self._websession_ssl = aiohttp.ClientSession(
            connector=aiohttp.TCPConnector(verify_ssl=False), loop=loop)

        # Global objects
        self._config = CoreConfig()
        self._hardware = Hardware()
        self._docker = DockerAPI()
        self._scheduler = Scheduler(loop=loop)
        self._dns = DNSForward(loop=loop)
        self._host_control = HostControl(loop=loop)

        # Internal objects pointers
        self._homeassistant = None
        self._supervisor = None
        self._addons = None
        self._api = None
        self._updater = None
        self._snapshots = None
        self._tasks = None
        self._services = None

    @property
    def arch(self):
        """Return running arch of hass.io system."""
        if self._supervisor:
            return self._supervisor.arch
        return None

    @property
    def loop(self):
        """Return loop object."""
        return self._loop

    @property
    def websession(self):
        """Return websession object."""
        return self._websession

    @property
    def websession_ssl(self):
        """Return websession object with disabled SSL."""
        return self._websession_ssl

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

    @property
    def homeassistant(self):
        """Return HomeAssistant object."""
        return self._homeassistant

    @homeassistant.setter
    def homeassistant(self, value):
        """Set a HomeAssistant object."""
        if self._homeassistant:
            raise RuntimeError("HomeAssistant already set!")
        self._homeassistant = value

    @property
    def supervisor(self):
        """Return Supervisor object."""
        return self._supervisor

    @supervisor.setter
    def supervisor(self, value):
        """Set a Supervisor object."""
        if self._supervisor:
            raise RuntimeError("Supervisor already set!")
        self._supervisor = value

    @property
    def api(self):
        """Return API object."""
        return self._api

    @api.setter
    def api(self, value):
        """Set a API object."""
        if self._api:
            raise RuntimeError("API already set!")
        self._api = value

    @property
    def updater(self):
        """Return Updater object."""
        return self._updater

    @updater.setter
    def updater(self, value):
        """Set a Updater object."""
        if self._updater:
            raise RuntimeError("Updater already set!")
        self._updater = value

    @property
    def addons(self):
        """Return AddonManager object."""
        return self._addons

    @addons.setter
    def addons(self, value):
        """Set a AddonManager object."""
        if self._addons:
            raise RuntimeError("AddonManager already set!")
        self._addons = value

    @property
    def snapshots(self):
        """Return SnapshotManager object."""
        return self._snapshots

    @snapshots.setter
    def snapshots(self, value):
        """Set a SnapshotManager object."""
        if self._snapshots:
            raise RuntimeError("SnapshotsManager already set!")
        self._snapshots = value

    @property
    def tasks(self):
        """Return Tasks object."""
        return self._tasks

    @tasks.setter
    def tasks(self, value):
        """Set a Tasks object."""
        if self._tasks:
            raise RuntimeError("Tasks already set!")
        self._tasks = value

    @property
    def services(self):
        """Return ServiceManager object."""
        return self._services

    @tasks.setter
    def services(self, value):
        """Set a ServiceManager object."""
        if self._services:
            raise RuntimeError("Services already set!")
        self._services = value


class CoreSysAttributes(object):
    """Inheret basic CoreSysAttributes."""

    coresys = None

    def __getattr__(self, name):
        """Mapping to coresys."""
        if hasattr(self.coresys, name[1:]):
            return getattr(self.coresys, name[1:])
        raise AttributeError(f"Can't find {name} on {self.__class__}")
