"""Handle core shared data."""
import asyncio

import aiohttp

from .config import CoreConfig
from .const import CHANNEL_DEV
from .docker import DockerAPI
from .misc.dns import DNSForward
from .misc.hardware import Hardware
from .misc.scheduler import Scheduler


class CoreSys:
    """Class that handle all shared data."""

    def __init__(self):
        """Initialize coresys."""
        # Static attributes
        self.exit_code = 0
        self.machine_id = None

        # External objects
        self._loop = asyncio.get_running_loop()
        self._websession = aiohttp.ClientSession()
        self._websession_ssl = aiohttp.ClientSession(
            connector=aiohttp.TCPConnector(ssl=False))

        # Global objects
        self._config = CoreConfig()
        self._hardware = Hardware()
        self._docker = DockerAPI()
        self._scheduler = Scheduler()
        self._dns = DNSForward()

        # Internal objects pointers
        self._core = None
        self._arch = None
        self._auth = None
        self._homeassistant = None
        self._supervisor = None
        self._addons = None
        self._api = None
        self._updater = None
        self._snapshots = None
        self._tasks = None
        self._host = None
        self._dbus = None
        self._hassos = None
        self._services = None
        self._discovery = None

    @property
    def machine(self):
        """Return running machine type of the Hass.io system."""
        if self._homeassistant:
            return self._homeassistant.machine
        return None

    @property
    def dev(self):
        """Return True if we run dev mode."""
        return self._updater.channel == CHANNEL_DEV

    @property
    def timezone(self):
        """Return timezone."""
        return self._config.timezone

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
    def core(self):
        """Return HassIO object."""
        return self._core

    @core.setter
    def core(self, value):
        """Set a Hass.io object."""
        if self._core:
            raise RuntimeError("Hass.io already set!")
        self._core = value

    @property
    def arch(self):
        """Return CpuArch object."""
        return self._arch

    @arch.setter
    def arch(self, value):
        """Set a CpuArch object."""
        if self._arch:
            raise RuntimeError("CpuArch already set!")
        self._arch = value

    @property
    def auth(self):
        """Return Auth object."""
        return self._auth

    @auth.setter
    def auth(self, value):
        """Set a Auth object."""
        if self._auth:
            raise RuntimeError("Auth already set!")
        self._auth = value

    @property
    def homeassistant(self):
        """Return Home Assistant object."""
        return self._homeassistant

    @homeassistant.setter
    def homeassistant(self, value):
        """Set a HomeAssistant object."""
        if self._homeassistant:
            raise RuntimeError("Home Assistant already set!")
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
        """Set an API object."""
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

    @services.setter
    def services(self, value):
        """Set a ServiceManager object."""
        if self._services:
            raise RuntimeError("Services already set!")
        self._services = value

    @property
    def discovery(self):
        """Return ServiceManager object."""
        return self._discovery

    @discovery.setter
    def discovery(self, value):
        """Set a Discovery object."""
        if self._discovery:
            raise RuntimeError("Discovery already set!")
        self._discovery = value

    @property
    def dbus(self):
        """Return DBusManager object."""
        return self._dbus

    @dbus.setter
    def dbus(self, value):
        """Set a DBusManager object."""
        if self._dbus:
            raise RuntimeError("DBusManager already set!")
        self._dbus = value

    @property
    def host(self):
        """Return HostManager object."""
        return self._host

    @host.setter
    def host(self, value):
        """Set a HostManager object."""
        if self._host:
            raise RuntimeError("HostManager already set!")
        self._host = value

    @property
    def hassos(self):
        """Return HassOS object."""
        return self._hassos

    @hassos.setter
    def hassos(self, value):
        """Set a HassOS object."""
        if self._hassos:
            raise RuntimeError("HassOS already set!")
        self._hassos = value


class CoreSysAttributes:
    """Inheret basic CoreSysAttributes."""

    coresys = None

    @property
    def sys_machine(self):
        """Return running machine type of the Hass.io system."""
        return self.coresys.machine

    @property
    def sys_dev(self):
        """Return True if we run dev mode."""
        return self.coresys.dev

    @property
    def sys_timezone(self):
        """Return timezone."""
        return self.coresys.timezone

    @property
    def sys_machine_id(self):
        """Return timezone."""
        return self.coresys.machine_id

    @property
    def sys_loop(self):
        """Return loop object."""
        return self.coresys.loop

    @property
    def sys_websession(self):
        """Return websession object."""
        return self.coresys.websession

    @property
    def sys_websession_ssl(self):
        """Return websession object with disabled SSL."""
        return self.coresys.websession_ssl

    @property
    def sys_config(self):
        """Return CoreConfig object."""
        return self.coresys.config

    @property
    def sys_hardware(self):
        """Return Hardware object."""
        return self.coresys.hardware

    @property
    def sys_docker(self):
        """Return DockerAPI object."""
        return self.coresys.docker

    @property
    def sys_scheduler(self):
        """Return Scheduler object."""
        return self.coresys.scheduler

    @property
    def sys_dns(self):
        """Return DNSForward object."""
        return self.coresys.dns

    @property
    def sys_core(self):
        """Return HassIO object."""
        return self.coresys.core

    @property
    def sys_arch(self):
        """Return CpuArch object."""
        return self.coresys.arch

    @property
    def sys_auth(self):
        """Return Auth object."""
        return self.coresys.auth

    @property
    def sys_homeassistant(self):
        """Return Home Assistant object."""
        return self.coresys.homeassistant

    @property
    def sys_supervisor(self):
        """Return Supervisor object."""
        return self.coresys.supervisor

    @property
    def sys_api(self):
        """Return API object."""
        return self.coresys.api

    @property
    def sys_updater(self):
        """Return Updater object."""
        return self.coresys.updater

    @property
    def sys_addons(self):
        """Return AddonManager object."""
        return self.coresys.addons

    @property
    def sys_snapshots(self):
        """Return SnapshotManager object."""
        return self.coresys.snapshots

    @property
    def sys_tasks(self):
        """Return Tasks object."""
        return self.coresys.tasks

    @property
    def sys_services(self):
        """Return ServiceManager object."""
        return self.coresys.services

    @property
    def sys_discovery(self):
        """Return ServiceManager object."""
        return self.coresys.discovery

    @property
    def sys_dbus(self):
        """Return DBusManager object."""
        return self.coresys.dbus

    @property
    def sys_host(self):
        """Return HostManager object."""
        return self.coresys.host

    @property
    def sys_hassos(self):
        """Return HassOS object."""
        return self.coresys.hassos

    def sys_run_in_executor(self, funct, *args):
        """Wrapper for executor pool."""
        return self.sys_loop.run_in_executor(None, funct, *args)

    def sys_create_task(self, coroutine):
        """Wrapper for async task."""
        return self.sys_loop.create_task(coroutine)
