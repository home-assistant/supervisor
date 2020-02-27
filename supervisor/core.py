"""Main file for Supervisor."""
import asyncio
from contextlib import suppress
import logging

import async_timeout

from .const import (
    STARTUP_APPLICATION,
    STARTUP_INITIALIZE,
    STARTUP_SERVICES,
    STARTUP_SYSTEM,
    CoreStates,
)
from .coresys import CoreSys, CoreSysAttributes
from .exceptions import HassioError, HomeAssistantError, SupervisorUpdateError

_LOGGER: logging.Logger = logging.getLogger(__name__)


class Core(CoreSysAttributes):
    """Main object of Supervisor."""

    def __init__(self, coresys: CoreSys):
        """Initialize Supervisor object."""
        self.coresys: CoreSys = coresys
        self.state: CoreStates = CoreStates.INITIALIZE

    async def connect(self):
        """Connect Supervisor container."""
        await self.sys_supervisor.load()

    async def setup(self):
        """Setup supervisor orchestration."""
        self.state = CoreStates.STARTUP

        # Load DBus
        await self.sys_dbus.load()

        # Load Host
        await self.sys_host.load()

        # Load Plugins container
        await asyncio.wait([self.sys_dns.load(), self.sys_audio.load()])

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
        await self.sys_updater.load()

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
        await self.sys_api.start()

        # Mark booted partition as healthy
        if self.sys_hassos.available:
            await self.sys_hassos.mark_healthy()

        # On release channel, try update itself
        if self.sys_supervisor.need_update:
            try:
                if self.sys_dev:
                    _LOGGER.warning("Ignore Supervisor updates on dev!")
                else:
                    await self.sys_supervisor.update()
            except SupervisorUpdateError:
                _LOGGER.fatal(
                    "Can't update supervisor! This will break some Add-ons or affect "
                    "future version of Home Assistant!"
                )

        # Start addon mark as initialize
        await self.sys_addons.boot(STARTUP_INITIALIZE)

        try:
            # HomeAssistant is already running / supervisor have only reboot
            if self.sys_hardware.last_boot == self.sys_config.last_boot:
                _LOGGER.info("Supervisor reboot detected")
                return

            # reset register services / discovery
            self.sys_services.reset()

            # start addon mark as system
            await self.sys_addons.boot(STARTUP_SYSTEM)

            # start addon mark as services
            await self.sys_addons.boot(STARTUP_SERVICES)

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
            await self.sys_addons.boot(STARTUP_APPLICATION)

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

            _LOGGER.info("Supervisor is up and running")
            self.state = CoreStates.RUNNING

        # On full host boot, relaod information
        self.sys_create_task(self.sys_host.reload())
        self.sys_create_task(self.sys_updater.reload())

    async def stop(self):
        """Stop a running orchestration."""
        # don't process scheduler anymore
        self.sys_scheduler.suspend = True

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
                        self.sys_dns.unload(),
                        self.sys_hwmonitor.unload(),
                    ]
                )
        except asyncio.TimeoutError:
            _LOGGER.warning("Force Shutdown!")

        _LOGGER.info("Supervisor is down")

    async def shutdown(self):
        """Shutdown all running containers in correct order."""
        await self.sys_addons.shutdown(STARTUP_APPLICATION)

        # Close Home Assistant
        with suppress(HassioError):
            await self.sys_homeassistant.stop()

        await self.sys_addons.shutdown(STARTUP_SERVICES)
        await self.sys_addons.shutdown(STARTUP_SYSTEM)
        await self.sys_addons.shutdown(STARTUP_INITIALIZE)

    def _update_last_boot(self):
        """Update last boot time."""
        self.sys_config.last_boot = self.sys_hardware.last_boot
        self.sys_config.save_data()

    async def repair(self):
        """Repair system integrity."""
        _LOGGER.info("Start repairing of Supervisor Environment")
        await self.sys_run_in_executor(self.sys_docker.repair)

        # Restore core functionality
        await self.sys_dns.repair()
        await self.sys_addons.repair()
        await self.sys_homeassistant.repair()

        # Fix HassOS specific
        if self.sys_hassos.available:
            await self.sys_hassos.repair_cli()

        # Tag version for latest
        await self.sys_supervisor.repair()
        _LOGGER.info("Finished repairing of Supervisor Environment")
