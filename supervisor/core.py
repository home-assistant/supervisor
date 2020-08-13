"""Main file for Supervisor."""
import asyncio
from contextlib import suppress
import logging

import async_timeout

from .const import SOCKET_DBUS, AddonStartup, CoreStates
from .coresys import CoreSys, CoreSysAttributes
from .exceptions import HassioError, HomeAssistantError, SupervisorUpdateError

_LOGGER: logging.Logger = logging.getLogger(__name__)


class Core(CoreSysAttributes):
    """Main object of Supervisor."""

    def __init__(self, coresys: CoreSys):
        """Initialize Supervisor object."""
        self.coresys: CoreSys = coresys
        self.state: CoreStates = CoreStates.INITIALIZE
        self._healthy: bool = True

    @property
    def healthy(self) -> bool:
        """Return True if system is healthy."""
        return self._healthy and self.sys_supported

    async def connect(self):
        """Connect Supervisor container."""
        await self.sys_supervisor.load()

        # If host docker is supported?
        if not self.sys_docker.info.supported_version:
            self.coresys.supported = False
            _LOGGER.error(
                "Docker version %s is not supported by Supervisor!",
                self.sys_docker.info.version,
            )
        elif self.sys_docker.info.inside_lxc:
            self.coresys.supported = False
            _LOGGER.error(
                "Detected Docker running inside LXC. Running Home Assistant with the Supervisor on LXC is not supported!"
            )

        if self.sys_docker.info.check_requirements():
            self.coresys.supported = False

        # Dbus available
        if not SOCKET_DBUS.exists():
            self.coresys.supported = False
            _LOGGER.error(
                "DBus is required for Home Assistant. This system is not supported!"
            )

        # Check supervisor version/update
        if self.sys_dev:
            self.sys_config.version = self.sys_supervisor.version
        elif (
            self.sys_config.version == "dev"
            or self.sys_supervisor.instance.version == "dev"
        ):
            self.coresys.supported = False
            _LOGGER.warning(
                "Found a development supervisor outside dev channel (%s)",
                self.sys_updater.channel,
            )
        elif self.sys_config.version != self.sys_supervisor.version:
            self._healthy = False
            _LOGGER.error(
                "Update %s of Supervisor %s fails!",
                self.sys_config.version,
                self.sys_supervisor.version,
            )

    async def setup(self):
        """Start setting up supervisor orchestration."""
        self.state = CoreStates.SETUP

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

        # rest api views
        await self.sys_api.load()

        # load last available data
        await self.sys_snapshots.load()

        # load services
        await self.sys_services.load()

        # Load discovery
        await self.sys_discovery.load()

        # Load ingress
        await self.sys_ingress.load()

        # Load secrets
        await self.sys_secrets.load()

    async def start(self):
        """Start Supervisor orchestration."""
        self.state = CoreStates.STARTUP
        await self.sys_api.start()

        # Check if system is healthy
        if not self.sys_supported:
            _LOGGER.critical("System running in a unsupported environment!")
        elif not self.healthy:
            _LOGGER.critical(
                "System running in a unhealthy state and need manual intervention!"
            )

        # Mark booted partition as healthy
        if self.sys_hassos.available:
            await self.sys_hassos.mark_healthy()

        # On release channel, try update itself
        if self.sys_supervisor.need_update:
            try:
                if self.sys_dev or not self.healthy:
                    _LOGGER.warning("Ignore Supervisor updates!")
                else:
                    await self.sys_supervisor.update()
            except SupervisorUpdateError:
                _LOGGER.critical(
                    "Can't update supervisor! This will break some Add-ons or affect "
                    "future version of Home Assistant!"
                )

        # Start addon mark as initialize
        await self.sys_addons.boot(AddonStartup.INITIALIZE)

        try:
            # HomeAssistant is already running / supervisor have only reboot
            if self.sys_hardware.last_boot == self.sys_config.last_boot:
                _LOGGER.info("Supervisor reboot detected")
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
                and not await self.sys_homeassistant.is_running()
            ):
                with suppress(HomeAssistantError):
                    await self.sys_homeassistant.start()
            else:
                _LOGGER.info("Skip start of Home Assistant")

            # start addon mark as application
            await self.sys_addons.boot(AddonStartup.APPLICATION)

            # store new last boot
            self._update_last_boot()

        finally:
            # Add core tasks into scheduler
            await self.sys_tasks.load()

            # If landingpage / run upgrade in background
            if self.sys_homeassistant.version == "landingpage":
                self.sys_create_task(self.sys_homeassistant.install())

            # Start observe the host Hardware
            await self.sys_hwmonitor.load()

            # Upate Host/Deivce information
            self.sys_create_task(self.sys_host.reload())
            self.sys_create_task(self.sys_updater.reload())

            _LOGGER.info("Supervisor is up and running")
            self.state = CoreStates.RUNNING

    async def stop(self):
        """Stop a running orchestration."""
        # don't process scheduler anymore
        self.state = CoreStates.STOPPING

        # store new last boot / prevent time adjustments
        if self.state == CoreStates.RUNNING:
            self._update_last_boot()

        # process async stop tasks
        try:
            with async_timeout.timeout(10):
                await asyncio.wait(
                    [
                        self.sys_api.stop(),
                        self.sys_websession.close(),
                        self.sys_websession_ssl.close(),
                        self.sys_ingress.unload(),
                        self.sys_plugins.unload(),
                        self.sys_hwmonitor.unload(),
                    ]
                )
        except asyncio.TimeoutError:
            _LOGGER.warning("Force Shutdown!")

        _LOGGER.info("Supervisor is down")

    async def shutdown(self):
        """Shutdown all running containers in correct order."""
        # don't process scheduler anymore
        if self.state == CoreStates.RUNNING:
            self.state = CoreStates.STOPPING

        # Shutdown Application Add-ons, using Home Assistant API
        await self.sys_addons.shutdown(AddonStartup.APPLICATION)

        # Close Home Assistant
        with suppress(HassioError):
            await self.sys_homeassistant.stop()

        # Shutdown System Add-ons
        await self.sys_addons.shutdown(AddonStartup.SERVICES)
        await self.sys_addons.shutdown(AddonStartup.SYSTEM)
        await self.sys_addons.shutdown(AddonStartup.INITIALIZE)

        # Shutdown all Plugins
        if self.state == CoreStates.STOPPING:
            await self.sys_plugins.shutdown()

    def _update_last_boot(self):
        """Update last boot time."""
        self.sys_config.last_boot = self.sys_hardware.last_boot
        self.sys_config.save_data()

    async def repair(self):
        """Repair system integrity."""
        _LOGGER.info("Start repairing of Supervisor Environment")
        await self.sys_run_in_executor(self.sys_docker.repair)

        # Fix plugins
        await self.sys_plugins.repair()

        # Restore core functionality
        await self.sys_addons.repair()
        await self.sys_homeassistant.repair()

        # Tag version for latest
        await self.sys_supervisor.repair()
        _LOGGER.info("Finished repairing of Supervisor Environment")
