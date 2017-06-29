"""Multible tasks."""
import asyncio
from datetime import datetime
import logging

_LOGGER = logging.getLogger(__name__)


def api_sessions_cleanup(config):
    """Create scheduler task for cleanup api sessions."""
    async def _api_sessions_cleanup():
        """Cleanup old api sessions."""
        now = datetime.now()
        for session, until_valid in config.security_sessions.items():
            if now >= until_valid:
                config.security_sessions = (session, None)

    return _api_sessions_cleanup


def hassio_update(config, supervisor, websession):
    """Create scheduler task for update of supervisor hassio."""
    async def _hassio_update():
        """Check and run update of supervisor hassio."""
        await config.fetch_update_infos(websession)
        if config.last_hassio == supervisor.version:
            return

        # don't perform a update on beta/dev channel
        if config.upstream_beta:
            _LOGGER.warning("Ignore Hass.IO update on beta upstream!")
            return

        _LOGGER.info("Found new HassIO version %s.", config.last_hassio)
        await supervisor.update(config.last_hassio)

    return _hassio_update


def homeassistant_watchdog(loop, homeassistant):
    """Create scheduler task for montoring running state."""
    async def _homeassistant_watchdog():
        """Check running state and start if they is close."""
        if homeassistant.in_progress or await homeassistant.is_running():
            return

        loop.create_task(homeassistant.run())

    return _homeassistant_watchdog


async def homeassistant_setup(config, loop, homeassistant, websession):
    """Install a homeassistant docker container."""
    while True:
        # read homeassistant tag and install it
        if not config.last_homeassistant:
            await config.fetch_update_infos(websession)

        tag = config.last_homeassistant
        if tag and await homeassistant.install(tag):
            break
        _LOGGER.warning("Error on setup HomeAssistant. Retry in 60.")
        await asyncio.sleep(60, loop=loop)

    # store version
    _LOGGER.info("HomeAssistant docker now installed.")
