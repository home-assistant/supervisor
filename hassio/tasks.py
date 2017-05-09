"""Multibe task for scheduler."""
import logging

_LOGGER = logging.getLogger(__name__)


def hassio_update(config, supervisor):
    """Create task for update of supervisor hassio."""
    async def _hassio_update():
        """Check and run update of supervisor hassio."""
        if config.last_hassio == supervisor.version:
            return

        _LOGGER.info("Found new HassIO version %s.", config.last_hassio)
        await supervisor.update(config.last_hassio)

    return _hassio_update


def homeassistant_watchdog(loop, homeassistant):
    """Create task for montoring running state."""
    async def _homeassistant_watchdog():
        """Check running state and start if they is close."""
        if homeassistant.in_progress or await homeassistant.is_running():
            return

        loop.create_task(homeassistant.run())

    return _homeassistant_watchdog
