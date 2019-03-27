"""Main file for Hass.io."""
from contextlib import suppress
import asyncio
import logging

import async_timeout

from .coresys import CoreSysAttributes
from .const import (
    STARTUP_SYSTEM,
    STARTUP_SERVICES,
    STARTUP_APPLICATION,
    STARTUP_INITIALIZE,
)
from .exceptions import HassioError, HomeAssistantError

_LOGGER = logging.getLogger(__name__)


class HassIO(CoreSysAttributes):
    """Main object of Hass.io."""

    def __init__(self, coresys):
        """Initialize Hass.io object."""
        self.coresys = coresys

    async def setup(self):
        """Setup HassIO orchestration."""
        # Load Supervisor
        await self.sys_supervisor.load()

        # Load DBus
        await self.sys_dbus.load()

        # Load Host
        await self.sys_host.load()

        # Load Home Assistant
        await self.sys_homeassistant.load()

        # Load CPU/Arch
        await self.sys_arch.load()

        # Load HassOS
        await self.sys_hassos.load()

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

        # start dns forwarding
        self.sys_create_task(self.sys_dns.start())

    async def start(self):
        """Start Hass.io orchestration."""
        # on release channel, try update itself
        if self.sys_supervisor.need_update:
            if self.sys_dev:
                _LOGGER.warning("Ignore Hass.io updates on dev!")
            elif await self.sys_supervisor.update():
                return

        # start api
        await self.sys_api.start()

        # start addon mark as initialize
        await self.sys_addons.boot(STARTUP_INITIALIZE)

        try:
            # HomeAssistant is already running / supervisor have only reboot
            if self.sys_hardware.last_boot == self.sys_config.last_boot:
                _LOGGER.info("Hass.io reboot detected")
                return

            # reset register services / discovery
            self.sys_services.reset()

            # start addon mark as system
            await self.sys_addons.boot(STARTUP_SYSTEM)

            # start addon mark as services
            await self.sys_addons.boot(STARTUP_SERVICES)

            # run HomeAssistant
            if self.sys_homeassistant.boot:
                with suppress(HomeAssistantError):
                    await self.sys_homeassistant.start()

            # start addon mark as application
            await self.sys_addons.boot(STARTUP_APPLICATION)

            # store new last boot
            self.sys_config.last_boot = self.sys_hardware.last_boot
            self.sys_config.save_data()

        finally:
            # Add core tasks into scheduler
            await self.sys_tasks.load()

            # If landingpage / run upgrade in background
            if self.sys_homeassistant.version == "landingpage":
                self.sys_create_task(self.sys_homeassistant.install())

            _LOGGER.info("Hass.io is up and running")

    async def stop(self):
        """Stop a running orchestration."""
        # don't process scheduler anymore
        self.sys_scheduler.suspend = True

        # process async stop tasks
        try:
            with async_timeout.timeout(10):
                await asyncio.wait(
                    [
                        self.sys_api.stop(),
                        self.sys_dns.stop(),
                        self.sys_websession.close(),
                        self.sys_websession_ssl.close(),
                    ]
                )
        except asyncio.TimeoutError:
            _LOGGER.warning("Force Shutdown!")

        _LOGGER.info("Hass.io is down")

    async def shutdown(self):
        """Shutdown all running containers in correct order."""
        await self.sys_addons.shutdown(STARTUP_APPLICATION)

        # Close Home Assistant
        with suppress(HassioError):
            await self.sys_homeassistant.stop()

        await self.sys_addons.shutdown(STARTUP_SERVICES)
        await self.sys_addons.shutdown(STARTUP_SYSTEM)
        await self.sys_addons.shutdown(STARTUP_INITIALIZE)
