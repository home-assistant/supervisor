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
                config.drop_security_session(session)

    return _api_sessions_cleanup


def addons_update(loop, addons):
    """Create scheduler task for auto update addons."""
    async def _addons_update():
        """Check if a update is available of a addon and update it."""
        tasks = []
        for addon in addons.list_addons:
            if not addon.is_installed or not addon.auto_update:
                continue

            if addon.version_installed == addon.last_version:
                continue

            if addon.test_udpate_schema():
                tasks.append(addon.update())
            else:
                _LOGGER.warning(
                    "Addon %s will be ignore, schema tests fails", addon.slug)

        if tasks:
            _LOGGER.info("Addon auto update process %d tasks", len(tasks))
            await asyncio.wait(tasks, loop=loop)

    return _addons_update


def hassio_update(supervisor, updater):
    """Create scheduler task for update of supervisor hassio."""
    async def _hassio_update():
        """Check and run update of supervisor hassio."""
        await updater.fetch_data()
        if updater.version_hassio == supervisor.version:
            return

        # don't perform a update on beta/dev channel
        if updater.beta_channel:
            _LOGGER.warning("Ignore Hass.IO update on beta upstream!")
            return

        _LOGGER.info("Found new HassIO version %s.", updater.version_hassio)
        await supervisor.update(updater.version_hassio)

    return _hassio_update


def homeassistant_watchdog(loop, homeassistant):
    """Create scheduler task for montoring running state."""
    async def _homeassistant_watchdog():
        """Check running state and start if they is close."""
        # if Home-Assistant is active
        if not await homeassistant.is_initialize():
            return

        # If Home-Assistant is running
        if homeassistant.in_progress or await homeassistant.is_running():
            return

        loop.create_task(homeassistant.run())

    return _homeassistant_watchdog
