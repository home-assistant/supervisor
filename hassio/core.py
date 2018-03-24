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

        # load last available data
        await self._updater.load()

        # load last available data
        await self._snapshots.load()

        # load services
        await self._services.load()

        # start dns forwarding
        self._loop.create_task(self._dns.start())

        # start addon mark as initialize
        await self._addons.auto_boot(STARTUP_INITIALIZE)

    async def start(self):
        """Start HassIO orchestration."""
        # on release channel, try update itself
        # on dev mode, only read new versions
        if not self._dev and self._supervisor.need_update:
            if await self._supervisor.update():
                return
        else:
            _LOGGER.info("Ignore Hass.io auto updates on dev channel")

        # start api
        await self._api.start()
        _LOGGER.info("Start API on %s", self._docker.network.supervisor)

        try:
            # HomeAssistant is already running / supervisor have only reboot
            if self._hardware.last_boot == self._config.last_boot:
                _LOGGER.info("Hass.io reboot detected")
                return

            # reset register services / discovery
            self._services.reset()

            # start addon mark as system
            await self._addons.auto_boot(STARTUP_SYSTEM)

            # start addon mark as services
            await self._addons.auto_boot(STARTUP_SERVICES)

            # run HomeAssistant
            if self._homeassistant.boot:
                await self._homeassistant.start()

            # start addon mark as application
            await self._addons.auto_boot(STARTUP_APPLICATION)

            # store new last boot
            self._config.last_boot = self._hardware.last_boot
            self._config.save_data()

        finally:
            # Add core tasks into scheduler
            await self._tasks.load()

            # If landingpage / run upgrade in background
            if self._homeassistant.version == 'landingpage':
                self._loop.create_task(self._homeassistant.install())

            _LOGGER.info("Hass.io is up and running")

    async def stop(self):
        """Stop a running orchestration."""
        # don't process scheduler anymore
        self._scheduler.suspend = True

        # process async stop tasks
        await asyncio.wait([
            self._api.stop(),
            self._dns.stop(),
            self._websession.close(),
            self._websession_ssl.close()
        ], loop=self._loop)
