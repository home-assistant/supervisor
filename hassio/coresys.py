"""Handle core shared data."""
from __future__ import annotations
import asyncio
from typing import TYPE_CHECKING, Optional

import aiohttp

from .config import CoreConfig
from .const import CHANNEL_DEV
from .docker import DockerAPI
from .misc.hardware import Hardware
from .misc.scheduler import Scheduler

if TYPE_CHECKING:
    from .addons import AddonManager
    from .api import RestAPI
    from .arch import CpuArch
    from .auth import Auth
    from .core import HassIO
    from .dbus import DBusManager
    from .discovery import Discovery
    from .dns import CoreDNS
    from .hassos import HassOS
    from .homeassistant import HomeAssistant
    from .host import HostManager
    from .ingress import Ingress
    from .services import ServiceManager
    from .snapshots import SnapshotManager
    from .supervisor import Supervisor
    from .store import StoreManager
    from .tasks import Tasks
    from .updater import Updater


class CoreSys:
    """Class that handle all shared data."""

    def __init__(self):
        """Initialize coresys."""
        # Static attributes
        self.machine_id: str = None

        # External objects
        self._loop: asyncio.BaseEventLoop = asyncio.get_running_loop()
        self._websession: aiohttp.ClientSession = aiohttp.ClientSession()
        self._websession_ssl: aiohttp.ClientSession = aiohttp.ClientSession(
            connector=aiohttp.TCPConnector(ssl=False)
        )

        # Global objects
        self._config: CoreConfig = CoreConfig()
        self._hardware: Hardware = Hardware()
        self._docker: DockerAPI = DockerAPI()
        self._scheduler: Scheduler = Scheduler()

        # Internal objects pointers
        self._core: Optional[HassIO] = None
        self._arch: Optional[CpuArch] = None
        self._auth: Optional[Auth] = None
        self._dns: Optional[CoreDNS] = None
        self._homeassistant: Optional[HomeAssistant] = None
        self._supervisor: Optional[Supervisor] = None
        self._addons: Optional[AddonManager] = None
        self._api: Optional[RestAPI] = None
        self._updater: Optional[Updater] = None
        self._snapshots: Optional[SnapshotManager] = None
        self._tasks: Optional[Tasks] = None
        self._host: Optional[HostManager] = None
        self._ingress: Optional[Ingress] = None
        self._dbus: Optional[DBusManager] = None
        self._hassos: Optional[HassOS] = None
        self._services: Optional[ServiceManager] = None
        self._store: Optional[StoreManager] = None
        self._discovery: Optional[Discovery] = None

    @property
    def machine(self) -> str:
        """Return running machine type of the Hass.io system."""
        if self._homeassistant:
            return self._homeassistant.machine
        return None

    @property
    def dev(self) -> bool:
        """Return True if we run dev mode."""
        return self._updater.channel == CHANNEL_DEV

    @property
    def timezone(self) -> str:
        """Return timezone."""
        return self._config.timezone

    @property
    def loop(self) -> asyncio.BaseEventLoop:
        """Return loop object."""
        return self._loop

    @property
    def websession(self) -> aiohttp.ClientSession:
        """Return websession object."""
        return self._websession

    @property
    def websession_ssl(self) -> aiohttp.ClientSession:
        """Return websession object with disabled SSL."""
        return self._websession_ssl

    @property
    def config(self) -> CoreConfig:
        """Return CoreConfig object."""
        return self._config

    @property
    def hardware(self) -> Hardware:
        """Return Hardware object."""
        return self._hardware

    @property
    def docker(self) -> DockerAPI:
        """Return DockerAPI object."""
        return self._docker

    @property
    def scheduler(self) -> Scheduler:
        """Return Scheduler object."""
        return self._scheduler

    @property
    def core(self) -> HassIO:
        """Return HassIO object."""
        return self._core

    @core.setter
    def core(self, value: HassIO):
        """Set a Hass.io object."""
        if self._core:
            raise RuntimeError("Hass.io already set!")
        self._core = value

    @property
    def arch(self) -> CpuArch:
        """Return CpuArch object."""
        return self._arch

    @arch.setter
    def arch(self, value: CpuArch):
        """Set a CpuArch object."""
        if self._arch:
            raise RuntimeError("CpuArch already set!")
        self._arch = value

    @property
    def auth(self) -> Auth:
        """Return Auth object."""
        return self._auth

    @auth.setter
    def auth(self, value: Auth):
        """Set a Auth object."""
        if self._auth:
            raise RuntimeError("Auth already set!")
        self._auth = value

    @property
    def homeassistant(self) -> HomeAssistant:
        """Return Home Assistant object."""
        return self._homeassistant

    @homeassistant.setter
    def homeassistant(self, value: HomeAssistant):
        """Set a HomeAssistant object."""
        if self._homeassistant:
            raise RuntimeError("Home Assistant already set!")
        self._homeassistant = value

    @property
    def supervisor(self) -> Supervisor:
        """Return Supervisor object."""
        return self._supervisor

    @supervisor.setter
    def supervisor(self, value: Supervisor):
        """Set a Supervisor object."""
        if self._supervisor:
            raise RuntimeError("Supervisor already set!")
        self._supervisor = value

    @property
    def api(self) -> RestAPI:
        """Return API object."""
        return self._api

    @api.setter
    def api(self, value: RestAPI):
        """Set an API object."""
        if self._api:
            raise RuntimeError("API already set!")
        self._api = value

    @property
    def updater(self) -> Updater:
        """Return Updater object."""
        return self._updater

    @updater.setter
    def updater(self, value: Updater):
        """Set a Updater object."""
        if self._updater:
            raise RuntimeError("Updater already set!")
        self._updater = value

    @property
    def addons(self) -> AddonManager:
        """Return AddonManager object."""
        return self._addons

    @addons.setter
    def addons(self, value: AddonManager):
        """Set a AddonManager object."""
        if self._addons:
            raise RuntimeError("AddonManager already set!")
        self._addons = value

    @property
    def store(self) -> StoreManager:
        """Return StoreManager object."""
        return self._store

    @store.setter
    def store(self, value: StoreManager):
        """Set a StoreManager object."""
        if self._store:
            raise RuntimeError("StoreManager already set!")
        self._store = value

    @property
    def snapshots(self) -> SnapshotManager:
        """Return SnapshotManager object."""
        return self._snapshots

    @snapshots.setter
    def snapshots(self, value: SnapshotManager):
        """Set a SnapshotManager object."""
        if self._snapshots:
            raise RuntimeError("SnapshotsManager already set!")
        self._snapshots = value

    @property
    def tasks(self) -> Tasks:
        """Return Tasks object."""
        return self._tasks

    @tasks.setter
    def tasks(self, value: Tasks):
        """Set a Tasks object."""
        if self._tasks:
            raise RuntimeError("Tasks already set!")
        self._tasks = value

    @property
    def services(self) -> ServiceManager:
        """Return ServiceManager object."""
        return self._services

    @services.setter
    def services(self, value: ServiceManager):
        """Set a ServiceManager object."""
        if self._services:
            raise RuntimeError("Services already set!")
        self._services = value

    @property
    def discovery(self) -> Discovery:
        """Return ServiceManager object."""
        return self._discovery

    @discovery.setter
    def discovery(self, value: Discovery):
        """Set a Discovery object."""
        if self._discovery:
            raise RuntimeError("Discovery already set!")
        self._discovery = value

    @property
    def dbus(self) -> DBusManager:
        """Return DBusManager object."""
        return self._dbus

    @dbus.setter
    def dbus(self, value: DBusManager):
        """Set a DBusManager object."""
        if self._dbus:
            raise RuntimeError("DBusManager already set!")
        self._dbus = value

    @property
    def dns(self) -> CoreDNS:
        """Return CoreDNS object."""
        return self._dns

    @dns.setter
    def dns(self, value: CoreDNS):
        """Set a CoreDNS object."""
        if self._dns:
            raise RuntimeError("CoreDNS already set!")
        self._dns = value

    @property
    def host(self) -> HostManager:
        """Return HostManager object."""
        return self._host

    @host.setter
    def host(self, value: HostManager):
        """Set a HostManager object."""
        if self._host:
            raise RuntimeError("HostManager already set!")
        self._host = value

    @property
    def ingress(self) -> Ingress:
        """Return Ingress object."""
        return self._ingress

    @ingress.setter
    def ingress(self, value: Ingress):
        """Set a Ingress object."""
        if self._ingress:
            raise RuntimeError("Ingress already set!")
        self._ingress = value

    @property
    def hassos(self) -> HassOS:
        """Return HassOS object."""
        return self._hassos

    @hassos.setter
    def hassos(self, value: HassOS):
        """Set a HassOS object."""
        if self._hassos:
            raise RuntimeError("HassOS already set!")
        self._hassos = value


class CoreSysAttributes:
    """Inheret basic CoreSysAttributes."""

    coresys = None

    @property
    def sys_machine(self) -> str:
        """Return running machine type of the Hass.io system."""
        return self.coresys.machine

    @property
    def sys_dev(self) -> str:
        """Return True if we run dev mode."""
        return self.coresys.dev

    @property
    def sys_timezone(self) -> str:
        """Return timezone."""
        return self.coresys.timezone

    @property
    def sys_machine_id(self) -> str:
        """Return timezone."""
        return self.coresys.machine_id

    @property
    def sys_loop(self) -> asyncio.BaseEventLoop:
        """Return loop object."""
        return self.coresys.loop

    @property
    def sys_websession(self) -> aiohttp.ClientSession:
        """Return websession object."""
        return self.coresys.websession

    @property
    def sys_websession_ssl(self) -> aiohttp.ClientSession:
        """Return websession object with disabled SSL."""
        return self.coresys.websession_ssl

    @property
    def sys_config(self) -> CoreConfig:
        """Return CoreConfig object."""
        return self.coresys.config

    @property
    def sys_hardware(self) -> Hardware:
        """Return Hardware object."""
        return self.coresys.hardware

    @property
    def sys_docker(self) -> DockerAPI:
        """Return DockerAPI object."""
        return self.coresys.docker

    @property
    def sys_scheduler(self) -> Scheduler:
        """Return Scheduler object."""
        return self.coresys.scheduler

    @property
    def sys_core(self) -> HassIO:
        """Return HassIO object."""
        return self.coresys.core

    @property
    def sys_arch(self) -> CpuArch:
        """Return CpuArch object."""
        return self.coresys.arch

    @property
    def sys_auth(self) -> Auth:
        """Return Auth object."""
        return self.coresys.auth

    @property
    def sys_homeassistant(self) -> HomeAssistant:
        """Return Home Assistant object."""
        return self.coresys.homeassistant

    @property
    def sys_supervisor(self) -> Supervisor:
        """Return Supervisor object."""
        return self.coresys.supervisor

    @property
    def sys_api(self) -> RestAPI:
        """Return API object."""
        return self.coresys.api

    @property
    def sys_updater(self) -> Updater:
        """Return Updater object."""
        return self.coresys.updater

    @property
    def sys_addons(self) -> AddonManager:
        """Return AddonManager object."""
        return self.coresys.addons

    @property
    def sys_store(self) -> StoreManager:
        """Return StoreManager object."""
        return self.coresys.store

    @property
    def sys_snapshots(self) -> SnapshotManager:
        """Return SnapshotManager object."""
        return self.coresys.snapshots

    @property
    def sys_tasks(self) -> Tasks:
        """Return Tasks object."""
        return self.coresys.tasks

    @property
    def sys_services(self) -> ServiceManager:
        """Return ServiceManager object."""
        return self.coresys.services

    @property
    def sys_discovery(self) -> Discovery:
        """Return ServiceManager object."""
        return self.coresys.discovery

    @property
    def sys_dbus(self) -> DBusManager:
        """Return DBusManager object."""
        return self.coresys.dbus

    @property
    def sys_dns(self) -> CoreDNS:
        """Return CoreDNS object."""
        return self.coresys.dns

    @property
    def sys_host(self) -> HostManager:
        """Return HostManager object."""
        return self.coresys.host

    @property
    def sys_ingress(self) -> Ingress:
        """Return Ingress object."""
        return self.coresys.ingress

    @property
    def sys_hassos(self) -> HassOS:
        """Return HassOS object."""
        return self.coresys.hassos

    def sys_run_in_executor(self, funct, *args) -> asyncio.Future:
        """Wrapper for executor pool."""
        return self.sys_loop.run_in_executor(None, funct, *args)

    def sys_create_task(self, coroutine) -> asyncio.Task:
        """Wrapper for async task."""
        return self.sys_loop.create_task(coroutine)
