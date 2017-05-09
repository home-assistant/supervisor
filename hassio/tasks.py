"""Multible tasks."""
import asyncio
import logging

_LOGGER = logging.getLogger(__name__)


def hassio_update(config, supervisor):
    """Create scheduler task for update of supervisor hassio."""
    async def _hassio_update():
        """Check and run update of supervisor hassio."""
        if config.last_hassio == supervisor.version:
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


async def homeassistant_setup(config, loop, homeassistant):
    """Install a homeassistant docker container."""
    while True:
        # read homeassistant tag and install it
        if not config.last_homeassistant:
            await config.fetch_update_infos()

        tag = config.last_homeassistant
        if tag and await homeassistant.install(tag):
            break
        _LOGGER.warning("Error on setup HomeAssistant. Retry in 60.")
        await asyncio.sleep(60, loop=loop)

    # store version
    _LOGGER.info("HomeAssistant docker now installed.")
