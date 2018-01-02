"""Main file for HassIO."""
import asyncio
import logging

from .coresys import CoreSysAttributes
from .const import (
    STARTUP_SYSTEM, STARTUP_SERVICES, STARTUP_APPLICATION, STARTUP_INITIALIZE)
from .utils.dt import fetch_timezone

_LOGGER = logging.getLogger(__name__)


class HassIO(CoreSysAttributes):
    """Main object of hassio."""

    def __init__(self, coresys):
        """Initialize hassio object."""
        self.coresys = coresys

    async def setup(self):
        """Setup HassIO orchestration."""
        # update timezone
        if self._config.timezone == 'UTC':
            self._config.timezone = await fetch_timezone(self._websession)

        # supervisor
        await self._supervisor.load()

        # hostcontrol
        await self._host_control.load()

        # Load homeassistant
        await self._homeassistant.load()

        # Load addons
        await self._addons.load()

        # rest api views
        await self._api.load()

        # start dns forwarding
        self._loop.create_task(self._dns.start())

        # start addon mark as initialize
        await self._addons.auto_boot(STARTUP_INITIALIZE)

    async def start(self):
        """Start HassIO orchestration."""
        # on release channel, try update itself
        # on beta channel, only read new versions
        if not self._updater.beta_channel:
            await self._supervisor.update()
        else:
            _LOGGER.info("Ignore Hass.io auto updates on beta mode")

        # start api
        await self._api.start()
        _LOGGER.info("Start API on %s", self._docker.network.supervisor)

        try:
            # HomeAssistant is already running / supervisor have only reboot
            if self._hardware.last_boot == self._config.last_boot:
                _LOGGER.info("Hass.io reboot detected")
                return

            # start addon mark as system
            await self._addons.auto_boot(STARTUP_SYSTEM)

            # start addon mark as services
            await self._addons.auto_boot(STARTUP_SERVICES)

            # run HomeAssistant
            if self._homeassistant.boot:
                await self._homeassistant.run()

            # start addon mark as application
            await self._addons.auto_boot(STARTUP_APPLICATION)

            # store new last boot
            self._config.last_boot = self._hardware.last_boot

        finally:
            # Add core tasks into scheduler
            await self._tasks.load()

            # If landingpage / run upgrade in background
            if self._homeassistant.version == 'landingpage':
                self._loop.create_task(self._homeassistant.install())

    async def stop(self):
        """Stop a running orchestration."""
        # don't process scheduler anymore
        self._scheduler.suspend = True

        # process stop tasks
        self._websession.close()
        self._websession_ssl.close()

        # process async stop tasks
        await asyncio.wait(
            [self._api.stop(), self._dns.stop()], loop=self._loop)
