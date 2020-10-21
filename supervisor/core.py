"""Main file for Supervisor."""
import asyncio
from contextlib import suppress
import logging
from typing import Optional

import async_timeout

from .const import (
    RUN_SUPERVISOR_STATE,
    SOCKET_DBUS,
    SUPERVISED_SUPPORTED_OS,
    AddonStartup,
    CoreState,
    HostFeature,
)
from .coresys import CoreSys, CoreSysAttributes
from .exceptions import (
    DockerError,
    HassioError,
    HomeAssistantCrashError,
    HomeAssistantError,
    SupervisorUpdateError,
)
from .resolution.const import ContextType, IssueType, UnsupportedReason

_LOGGER: logging.Logger = logging.getLogger(__name__)


class Core(CoreSysAttributes):
    """Main object of Supervisor."""

    def __init__(self, coresys: CoreSys):
        """Initialize Supervisor object."""
        self.coresys: CoreSys = coresys
        self.healthy: bool = True
        self._state: Optional[CoreState] = None

    @property
    def state(self) -> CoreState:
        """Return state of the core."""
        return self._state

    @property
    def supported(self) -> CoreState:
        """Return true if the installation is supported."""
        return len(self.sys_resolution.unsupported) == 0

    @state.setter
    def state(self, new_state: CoreState) -> None:
        """Set core into new state."""
        try:
            RUN_SUPERVISOR_STATE.write_text(new_state.value)
        except OSError as err:
            _LOGGER.warning(
                "Can't update the Supervisor state to %s: %s", new_state, err
            )
        finally:
            self._state = new_state

    async def connect(self):
        """Connect Supervisor container."""
        self.state = CoreState.INITIALIZE

        # Load information from container
        await self.sys_supervisor.load()

        # If host docker is supported?
        if not self.sys_docker.info.supported_version:
            self.sys_resolution.unsupported = UnsupportedReason.DOCKER_VERSION
            self.healthy = False
            _LOGGER.error(
                "Docker version '%s' is not supported by Supervisor!",
                self.sys_docker.info.version,
            )
        elif self.sys_docker.info.inside_lxc:
            self.sys_resolution.unsupported = UnsupportedReason.LXC
            self.healthy = False
            _LOGGER.error(
                "Detected Docker running inside LXC. Running Home Assistant with the Supervisor on LXC is not supported!"
            )
        elif not self.sys_supervisor.instance.privileged:
            self.sys_resolution.unsupported = UnsupportedReason.PRIVILEGED
            self.healthy = False
            _LOGGER.error("Supervisor does not run in Privileged mode.")

        if self.sys_docker.info.check_requirements():
            self.sys_resolution.unsupported = UnsupportedReason.DOCKER_CONFIGURATION

        # Dbus available
        if not SOCKET_DBUS.exists():
            self.sys_resolution.unsupported = UnsupportedReason.DBUS
            _LOGGER.error(
                "D-Bus is required for Home Assistant. This system is not supported!"
            )

        # Check supervisor version/update
        if self.sys_dev:
            self.sys_config.version = self.sys_supervisor.version
        elif self.sys_config.version != self.sys_supervisor.version:
            self.sys_resolution.create_issue(
                IssueType.UPDATE_ROLLBACK, ContextType.SUPERVISOR
            )
            self.healthy = False
            _LOGGER.error(
                "Update '%s' of Supervisor '%s' failed!",
                self.sys_config.version,
                self.sys_supervisor.version,
            )

    async def setup(self):
        """Start setting up supervisor orchestration."""
        self.state = CoreState.SETUP

        # rest api views
        await self.sys_api.load()
        await self.sys_api.start()

        # Load DBus
        await self.sys_dbus.load()

        # Load Host
        await self.sys_host.load()

        # Load Plugins container
        await self.sys_plugins.load()

        # load last available data
        await self.sys_updater.load()

        # Load Home Assistant
        await self.sys_homeassistant.load()

        # Load CPU/Arch
        await self.sys_arch.load()

        # Load HassOS
        await self.sys_hassos.load()

        # Load Stores
        await self.sys_store.load()

        # Load Add-ons
        await self.sys_addons.load()

        # load last available data
        await self.sys_snapshots.load()

        # load services
        await self.sys_services.load()

        # Load discovery
        await self.sys_discovery.load()

        # Load ingress
        await self.sys_ingress.load()

        # Load Resoulution
        await self.sys_resolution.load()

        # Check supported OS
        if not self.sys_hassos.available:
            if self.sys_host.info.operating_system not in SUPERVISED_SUPPORTED_OS:
                self.sys_resolution.unsupported = UnsupportedReason.OS
                _LOGGER.error(
                    "Detected unsupported OS: %s",
                    self.sys_host.info.operating_system,
                )

        # Check Host features
        if HostFeature.NETWORK not in self.sys_host.supported_features:
            self.sys_resolution.unsupported = UnsupportedReason.NETWORK_MANAGER
            _LOGGER.error("NetworkManager is not correctly configured")
        if any(
            feature not in self.sys_host.supported_features
            for feature in (
                HostFeature.HOSTNAME,
                HostFeature.SERVICES,
                HostFeature.SHUTDOWN,
                HostFeature.REBOOT,
            )
        ):
            self.sys_resolution.unsupported = UnsupportedReason.SYSTEMD
            _LOGGER.error("Systemd is not correctly working")

        # Check if image names from denylist exist
        try:
            if await self.sys_run_in_executor(self.sys_docker.check_denylist_images):
                self.sys_resolution.unsupported = UnsupportedReason.CONTAINER
                self.healthy = False
        except DockerError:
            self.healthy = False

    async def start(self):
        """Start Supervisor orchestration."""
        self.state = CoreState.STARTUP

        # Check if system is healthy
        if not self.supported:
            _LOGGER.warning("System running in a unsupported environment!")
        if not self.healthy:
            _LOGGER.critical(
                "System running in a unhealthy state and need manual intervention!"
            )

        # Mark booted partition as healthy
        if self.sys_hassos.available:
            await self.sys_hassos.mark_healthy()

        # On release channel, try update itself
        if self.sys_supervisor.need_update:
            try:
                if not self.healthy:
                    _LOGGER.warning("Ignoring Supervisor updates!")
                else:
                    await self.sys_supervisor.update()
                    return
            except SupervisorUpdateError as err:
                _LOGGER.critical(
                    "Can't update Supervisor! This will break some Add-ons or affect "
                    "future version of Home Assistant!"
                )
                self.sys_capture_exception(err)

        # Start addon mark as initialize
        await self.sys_addons.boot(AddonStartup.INITIALIZE)

        try:
            # HomeAssistant is already running / supervisor have only reboot
            if self.sys_hardware.last_boot == self.sys_config.last_boot:
                _LOGGER.debug("Supervisor reboot detected")
                return

            # reset register services / discovery
            self.sys_services.reset()

            # start addon mark as system
            await self.sys_addons.boot(AddonStartup.SYSTEM)

            # start addon mark as services
            await self.sys_addons.boot(AddonStartup.SERVICES)

            # run HomeAssistant
            if (
                self.sys_homeassistant.boot
                and not await self.sys_homeassistant.core.is_running()
            ):
                try:
                    await self.sys_homeassistant.core.start()
                except HomeAssistantCrashError as err:
                    _LOGGER.error("Can't start Home Assistant Core - rebuiling")
                    self.sys_capture_exception(err)

                    with suppress(HomeAssistantError):
                        await self.sys_homeassistant.core.rebuild()
                except HomeAssistantError as err:
                    self.sys_capture_exception(err)
            else:
                _LOGGER.debug("Skiping start of Home Assistant")

            # start addon mark as application
            await self.sys_addons.boot(AddonStartup.APPLICATION)

            # store new last boot
            self._update_last_boot()

        finally:
            # Add core tasks into scheduler
            await self.sys_tasks.load()

            # If landingpage / run upgrade in background
            if self.sys_homeassistant.version == "landingpage":
                self.sys_create_task(self.sys_homeassistant.core.install())

            # Start observe the host Hardware
            await self.sys_hwmonitor.load()

            # Upate Host/Deivce information
            self.sys_create_task(self.sys_host.reload())
            self.sys_create_task(self.sys_updater.reload())

            self.state = CoreState.RUNNING
            _LOGGER.info("Supervisor is up and running")

    async def stop(self):
        """Stop a running orchestration."""
        # store new last boot / prevent time adjustments
        if self.state in (CoreState.RUNNING, CoreState.SHUTDOWN):
            self._update_last_boot()
        if self.state in (CoreState.STOPPING, CoreState.CLOSE):
            return

        # don't process scheduler anymore
        self.state = CoreState.STOPPING

        # Stage 1
        try:
            async with async_timeout.timeout(10):
                await asyncio.wait([self.sys_api.stop(), self.sys_scheduler.shutdown()])
        except asyncio.TimeoutError:
            _LOGGER.warning("Stage 1: Force Shutdown!")

        # Stage 2
        try:
            async with async_timeout.timeout(10):
                await asyncio.wait(
                    [
                        self.sys_websession.close(),
                        self.sys_websession_ssl.close(),
                        self.sys_ingress.unload(),
                        self.sys_hwmonitor.unload(),
                    ]
                )
        except asyncio.TimeoutError:
            _LOGGER.warning("Stage 2: Force Shutdown!")

        self.state = CoreState.CLOSE
        _LOGGER.info("Supervisor is down")
        self.sys_loop.stop()

    async def shutdown(self):
        """Shutdown all running containers in correct order."""
        # don't process scheduler anymore
        if self.state == CoreState.RUNNING:
            self.state = CoreState.SHUTDOWN

        # Shutdown Application Add-ons, using Home Assistant API
        await self.sys_addons.shutdown(AddonStartup.APPLICATION)

        # Close Home Assistant
        with suppress(HassioError):
            await self.sys_homeassistant.core.stop()

        # Shutdown System Add-ons
        await self.sys_addons.shutdown(AddonStartup.SERVICES)
        await self.sys_addons.shutdown(AddonStartup.SYSTEM)
        await self.sys_addons.shutdown(AddonStartup.INITIALIZE)

        # Shutdown all Plugins
        if self.state in (CoreState.STOPPING, CoreState.SHUTDOWN):
            await self.sys_plugins.shutdown()

    def _update_last_boot(self):
        """Update last boot time."""
        self.sys_config.last_boot = self.sys_hardware.last_boot
        self.sys_config.save_data()

    async def repair(self):
        """Repair system integrity."""
        _LOGGER.info("Starting repair of Supervisor Environment")
        await self.sys_run_in_executor(self.sys_docker.repair)

        # Fix plugins
        await self.sys_plugins.repair()

        # Restore core functionality
        await self.sys_addons.repair()
        await self.sys_homeassistant.core.repair()

        # Tag version for latest
        await self.sys_supervisor.repair()
        _LOGGER.info("Finished repair of Supervisor Environment")
