"""Handle core shared data."""
from __future__ import annotations

import asyncio
from collections.abc import Callable, Coroutine
from datetime import datetime
from functools import partial
import logging
import os
from types import MappingProxyType
from typing import TYPE_CHECKING, Any, TypeVar

import aiohttp

from .config import CoreConfig
from .const import ENV_SUPERVISOR_DEV, SERVER_SOFTWARE
from .utils.dt import UTC, get_time_zone

if TYPE_CHECKING:
    from .addons import AddonManager
    from .api import RestAPI
    from .arch import CpuArch
    from .auth import Auth
    from .backups.manager import BackupManager
    from .bus import Bus
    from .core import Core
    from .dbus.manager import DBusManager
    from .discovery import Discovery
    from .docker.manager import DockerAPI
    from .hardware.manager import HardwareManager
    from .homeassistant.module import HomeAssistant
    from .host.manager import HostManager
    from .ingress import Ingress
    from .jobs import JobManager
    from .misc.scheduler import Scheduler
    from .misc.tasks import Tasks
    from .mounts.manager import MountManager
    from .os.manager import OSManager
    from .plugins.manager import PluginManager
    from .resolution.module import ResolutionManager
    from .security.module import Security
    from .services import ServiceManager
    from .store import StoreManager
    from .supervisor import Supervisor
    from .updater import Updater


T = TypeVar("T")

_LOGGER: logging.Logger = logging.getLogger(__name__)


class CoreSys:
    """Class that handle all shared data."""

    def __init__(self):
        """Initialize coresys."""
        # Static attributes protected
        self._machine_id: str | None = None
        self._machine: str | None = None

        # External objects
        self._loop: asyncio.BaseEventLoop = asyncio.get_running_loop()
        self._websession: aiohttp.ClientSession = aiohttp.ClientSession()

        # Global objects
        self._config: CoreConfig = CoreConfig()

        # Internal objects pointers
        self._docker: DockerAPI | None = None
        self._core: Core | None = None
        self._arch: CpuArch | None = None
        self._auth: Auth | None = None
        self._homeassistant: HomeAssistant | None = None
        self._supervisor: Supervisor | None = None
        self._addons: AddonManager | None = None
        self._api: RestAPI | None = None
        self._updater: Updater | None = None
        self._backups: BackupManager | None = None
        self._tasks: Tasks | None = None
        self._host: HostManager | None = None
        self._ingress: Ingress | None = None
        self._dbus: DBusManager | None = None
        self._os: OSManager | None = None
        self._services: ServiceManager | None = None
        self._scheduler: Scheduler | None = None
        self._store: StoreManager | None = None
        self._discovery: Discovery | None = None
        self._hardware: HardwareManager | None = None
        self._plugins: PluginManager | None = None
        self._resolution: ResolutionManager | None = None
        self._jobs: JobManager | None = None
        self._security: Security | None = None
        self._bus: Bus | None = None
        self._mounts: MountManager | None = None

        # Set default header for aiohttp
        self._websession._default_headers = MappingProxyType(
            {aiohttp.hdrs.USER_AGENT: SERVER_SOFTWARE}
        )

    @property
    def dev(self) -> bool:
        """Return True if we run dev mode."""
        return bool(os.environ.get(ENV_SUPERVISOR_DEV, 0))

    @property
    def timezone(self) -> str:
        """Return system timezone."""
        if self.config.timezone:
            return self.config.timezone
        if self.host.info.timezone:
            return self.host.info.timezone
        return "UTC"

    @property
    def loop(self) -> asyncio.BaseEventLoop:
        """Return loop object."""
        return self._loop

    @property
    def websession(self) -> aiohttp.ClientSession:
        """Return websession object."""
        return self._websession

    @property
    def config(self) -> CoreConfig:
        """Return CoreConfig object."""
        return self._config

    @property
    def docker(self) -> DockerAPI:
        """Return DockerAPI object."""
        if self._docker is None:
            raise RuntimeError("Docker not set!")
        return self._docker

    @docker.setter
    def docker(self, value: DockerAPI) -> None:
        """Set docker object."""
        if self._docker:
            raise RuntimeError("Docker already set!")
        self._docker = value

    @property
    def scheduler(self) -> Scheduler:
        """Return Scheduler object."""
        if self._scheduler is None:
            raise RuntimeError("Scheduler not set!")
        return self._scheduler

    @scheduler.setter
    def scheduler(self, value: Scheduler) -> None:
        """Set a Scheduler object."""
        if self._scheduler:
            raise RuntimeError("Scheduler already set!")
        self._scheduler = value

    @property
    def core(self) -> Core:
        """Return core object."""
        if self._core is None:
            raise RuntimeError("Core not set!")
        return self._core

    @core.setter
    def core(self, value: Core) -> None:
        """Set a Core object."""
        if self._core:
            raise RuntimeError("Core already set!")
        self._core = value

    @property
    def plugins(self) -> PluginManager:
        """Return PluginManager object."""
        if self._plugins is None:
            raise RuntimeError("PluginManager not set!")
        return self._plugins

    @plugins.setter
    def plugins(self, value: PluginManager) -> None:
        """Set a PluginManager object."""
        if self._plugins:
            raise RuntimeError("PluginManager already set!")
        self._plugins = value

    @property
    def arch(self) -> CpuArch:
        """Return CpuArch object."""
        if self._arch is None:
            raise RuntimeError("CpuArch not set!")
        return self._arch

    @arch.setter
    def arch(self, value: CpuArch) -> None:
        """Set a CpuArch object."""
        if self._arch:
            raise RuntimeError("CpuArch already set!")
        self._arch = value

    @property
    def auth(self) -> Auth:
        """Return Auth object."""
        if self._auth is None:
            raise RuntimeError("Auth not set!")
        return self._auth

    @auth.setter
    def auth(self, value: Auth) -> None:
        """Set a Auth object."""
        if self._auth:
            raise RuntimeError("Auth already set!")
        self._auth = value

    @property
    def homeassistant(self) -> HomeAssistant:
        """Return Home Assistant object."""
        if self._homeassistant is None:
            raise RuntimeError("Home Assistant not set!")
        return self._homeassistant

    @homeassistant.setter
    def homeassistant(self, value: HomeAssistant) -> None:
        """Set a HomeAssistant object."""
        if self._homeassistant:
            raise RuntimeError("Home Assistant already set!")
        self._homeassistant = value

    @property
    def supervisor(self) -> Supervisor:
        """Return Supervisor object."""
        if self._supervisor is None:
            raise RuntimeError("Supervisor not set!")
        return self._supervisor

    @supervisor.setter
    def supervisor(self, value: Supervisor) -> None:
        """Set a Supervisor object."""
        if self._supervisor:
            raise RuntimeError("Supervisor already set!")
        self._supervisor = value

    @property
    def api(self) -> RestAPI:
        """Return API object."""
        if self._api is None:
            raise RuntimeError("API not set!")
        return self._api

    @api.setter
    def api(self, value: RestAPI) -> None:
        """Set an API object."""
        if self._api:
            raise RuntimeError("API already set!")
        self._api = value

    @property
    def updater(self) -> Updater:
        """Return Updater object."""
        if self._updater is None:
            raise RuntimeError("Updater not set!")
        return self._updater

    @updater.setter
    def updater(self, value: Updater) -> None:
        """Set a Updater object."""
        if self._updater:
            raise RuntimeError("Updater already set!")
        self._updater = value

    @property
    def addons(self) -> AddonManager:
        """Return AddonManager object."""
        if self._addons is None:
            raise RuntimeError("AddonManager not set!")
        return self._addons

    @addons.setter
    def addons(self, value: AddonManager) -> None:
        """Set a AddonManager object."""
        if self._addons:
            raise RuntimeError("AddonManager already set!")
        self._addons = value

    @property
    def store(self) -> StoreManager:
        """Return StoreManager object."""
        if self._store is None:
            raise RuntimeError("StoreManager not set!")
        return self._store

    @store.setter
    def store(self, value: StoreManager) -> None:
        """Set a StoreManager object."""
        if self._store:
            raise RuntimeError("StoreManager already set!")
        self._store = value

    @property
    def backups(self) -> BackupManager:
        """Return BackupManager object."""
        if self._backups is None:
            raise RuntimeError("BackupManager not set!")
        return self._backups

    @backups.setter
    def backups(self, value: BackupManager) -> None:
        """Set a BackupManager object."""
        if self._backups:
            raise RuntimeError("BackupsManager already set!")
        self._backups = value

    @property
    def tasks(self) -> Tasks:
        """Return Tasks object."""
        if self._tasks is None:
            raise RuntimeError("Tasks not set!")
        return self._tasks

    @tasks.setter
    def tasks(self, value: Tasks) -> None:
        """Set a Tasks object."""
        if self._tasks:
            raise RuntimeError("Tasks already set!")
        self._tasks = value

    @property
    def services(self) -> ServiceManager:
        """Return ServiceManager object."""
        if self._services is None:
            raise RuntimeError("Services not set!")
        return self._services

    @services.setter
    def services(self, value: ServiceManager) -> None:
        """Set a ServiceManager object."""
        if self._services:
            raise RuntimeError("Services already set!")
        self._services = value

    @property
    def discovery(self) -> Discovery:
        """Return ServiceManager object."""
        if self._discovery is None:
            raise RuntimeError("Discovery not set!")
        return self._discovery

    @discovery.setter
    def discovery(self, value: Discovery) -> None:
        """Set a Discovery object."""
        if self._discovery:
            raise RuntimeError("Discovery already set!")
        self._discovery = value

    @property
    def dbus(self) -> DBusManager:
        """Return DBusManager object."""
        if self._dbus is None:
            raise RuntimeError("DBusManager not set!")
        return self._dbus

    @dbus.setter
    def dbus(self, value: DBusManager) -> None:
        """Set a DBusManager object."""
        if self._dbus:
            raise RuntimeError("DBusManager already set!")
        self._dbus = value

    @property
    def bus(self) -> Bus:
        """Return Bus object."""
        if self._bus is None:
            raise RuntimeError("Bus not set!")
        return self._bus

    @bus.setter
    def bus(self, value: Bus) -> None:
        """Set a Bus object."""
        if self._bus:
            raise RuntimeError("Bus already set!")
        self._bus = value

    @property
    def host(self) -> HostManager:
        """Return HostManager object."""
        if self._host is None:
            raise RuntimeError("HostManager not set!")
        return self._host

    @host.setter
    def host(self, value: HostManager) -> None:
        """Set a HostManager object."""
        if self._host:
            raise RuntimeError("HostManager already set!")
        self._host = value

    @property
    def hardware(self) -> HardwareManager:
        """Return HardwareManager object."""
        if self._hardware is None:
            raise RuntimeError("HardwareManager not set!")
        return self._hardware

    @hardware.setter
    def hardware(self, value: HardwareManager) -> None:
        """Set a HardwareManager object."""
        if self._hardware:
            raise RuntimeError("HardwareManager already set!")
        self._hardware = value

    @property
    def ingress(self) -> Ingress:
        """Return Ingress object."""
        if self._ingress is None:
            raise RuntimeError("Ingress not set!")
        return self._ingress

    @ingress.setter
    def ingress(self, value: Ingress) -> None:
        """Set a Ingress object."""
        if self._ingress:
            raise RuntimeError("Ingress already set!")
        self._ingress = value

    @property
    def os(self) -> OSManager:
        """Return OSManager object."""
        if self._os is None:
            raise RuntimeError("OSManager not set!")
        return self._os

    @os.setter
    def os(self, value: OSManager) -> None:
        """Set a OSManager object."""
        if self._os:
            raise RuntimeError("OSManager already set!")
        self._os = value

    @property
    def resolution(self) -> ResolutionManager:
        """Return resolution manager object."""
        if self._resolution is None:
            raise RuntimeError("resolution manager not set!")
        return self._resolution

    @resolution.setter
    def resolution(self, value: ResolutionManager) -> None:
        """Set a resolution manager object."""
        if self._resolution:
            raise RuntimeError("resolution manager already set!")
        self._resolution = value

    @property
    def security(self) -> Security:
        """Return security object."""
        if self._security is None:
            raise RuntimeError("security not set!")
        return self._security

    @security.setter
    def security(self, value: Security) -> None:
        """Set a security object."""
        if self._security:
            raise RuntimeError("security already set!")
        self._security = value

    @property
    def jobs(self) -> JobManager:
        """Return resolution manager object."""
        if self._jobs is None:
            raise RuntimeError("job manager not set!")
        return self._jobs

    @jobs.setter
    def jobs(self, value: JobManager) -> None:
        """Set a resolution manager object."""
        if self._jobs:
            raise RuntimeError("job manager already set!")
        self._jobs = value

    @property
    def mounts(self) -> MountManager:
        """Return mount manager object."""
        if self._mounts is None:
            raise RuntimeError("mount manager not set!")
        return self._mounts

    @mounts.setter
    def mounts(self, value: MountManager) -> None:
        """Set a mount manager object."""
        if self._mounts:
            raise RuntimeError("mount manager already set!")
        self._mounts = value

    @property
    def machine(self) -> str | None:
        """Return machine type string."""
        return self._machine

    @machine.setter
    def machine(self, value: str) -> None:
        """Set a machine type string."""
        if self._machine:
            raise RuntimeError("Machine type already set!")
        self._machine = value

    @property
    def machine_id(self) -> str | None:
        """Return machine-id type string."""
        return self._machine_id

    @machine_id.setter
    def machine_id(self, value: str) -> None:
        """Set a machine-id type string."""
        if self._machine_id:
            raise RuntimeError("Machine-ID type already set!")
        self._machine_id = value

    def now(self) -> datetime:
        """Return now in local timezone."""
        return datetime.now(get_time_zone(self.timezone) or UTC)

    def run_in_executor(
        self, funct: Callable[..., T], *args: tuple[Any], **kwargs: dict[str, Any]
    ) -> Coroutine[Any, Any, T]:
        """Add an job to the executor pool."""
        if kwargs:
            funct = partial(funct, **kwargs)

        return self.loop.run_in_executor(None, funct, *args)

    def create_task(self, coroutine: Coroutine) -> asyncio.Task:
        """Create an async task."""
        return self.loop.create_task(coroutine)


class CoreSysAttributes:
    """Inherit basic CoreSysAttributes."""

    coresys: CoreSys

    @property
    def sys_timezone(self) -> str:
        """Return system internal used timezone."""
        return self.coresys.timezone

    @property
    def sys_machine(self) -> str | None:
        """Return running machine type of the Supervisor system."""
        return self.coresys.machine

    @property
    def sys_dev(self) -> bool:
        """Return True if we run dev mode."""
        return self.coresys.dev

    @property
    def sys_loop(self) -> asyncio.BaseEventLoop:
        """Return loop object."""
        return self.coresys.loop

    @property
    def sys_websession(self) -> aiohttp.ClientSession:
        """Return websession object."""
        return self.coresys.websession

    @property
    def sys_config(self) -> CoreConfig:
        """Return CoreConfig object."""
        return self.coresys.config

    @property
    def sys_docker(self) -> DockerAPI:
        """Return DockerAPI object."""
        return self.coresys.docker

    @property
    def sys_scheduler(self) -> Scheduler:
        """Return Scheduler object."""
        return self.coresys.scheduler

    @property
    def sys_core(self) -> Core:
        """Return Core object."""
        return self.coresys.core

    @property
    def sys_bus(self) -> Bus:
        """Return Bus object."""
        return self.coresys.bus

    @property
    def sys_plugins(self) -> PluginManager:
        """Return PluginManager object."""
        return self.coresys.plugins

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
    def sys_backups(self) -> BackupManager:
        """Return BackupManager object."""
        return self.coresys.backups

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
    def sys_host(self) -> HostManager:
        """Return HostManager object."""
        return self.coresys.host

    @property
    def sys_hardware(self) -> HardwareManager:
        """Return HwMonitor object."""
        return self.coresys.hardware

    @property
    def sys_ingress(self) -> Ingress:
        """Return Ingress object."""
        return self.coresys.ingress

    @property
    def sys_os(self) -> OSManager:
        """Return OSManager object."""
        return self.coresys.os

    @property
    def sys_resolution(self) -> ResolutionManager:
        """Return Resolution manager object."""
        return self.coresys.resolution

    @property
    def sys_security(self) -> Security:
        """Return Security object."""
        return self.coresys.security

    @property
    def sys_jobs(self) -> JobManager:
        """Return Job manager object."""
        return self.coresys.jobs

    @property
    def sys_mounts(self) -> MountManager:
        """Return mount manager object."""
        return self.coresys.mounts

    def now(self) -> datetime:
        """Return now in local timezone."""
        return self.coresys.now()

    def sys_run_in_executor(
        self, funct: Callable[..., T], *args: tuple[Any], **kwargs: dict[str, Any]
    ) -> Coroutine[Any, Any, T]:
        """Add an job to the executor pool."""
        return self.coresys.run_in_executor(funct, *args, **kwargs)

    def sys_create_task(self, coroutine: Coroutine) -> asyncio.Task:
        """Create an async task."""
        return self.coresys.create_task(coroutine)
