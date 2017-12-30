"""Multible tasks."""
import asyncio
from datetime import datetime
import logging

from .coresys import CoreSysAttributes

_LOGGER = logging.getLogger(__name__)


class Tasks(CoreSysAttributes):
    """Handle Tasks inside HassIO."""

    def __ini__(self, coresys):
        """Initialize Tasks."""
        self.coresys = coresys


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


def homeassistant_watchdog_docker(loop, homeassistant):
    """Create scheduler task for montoring running state of docker."""
    async def _homeassistant_watchdog_docker():
        """Check running state of docker and start if they is close."""
        # if Home-Assistant is active
        if not await homeassistant.is_initialize() or \
                not homeassistant.watchdog:
            return

        # if Home-Assistant is running
        if homeassistant.in_progress or await homeassistant.is_running():
            return

        loop.create_task(homeassistant.run())
        _LOGGER.error("Watchdog found a problem with Home-Assistant docker!")

    return _homeassistant_watchdog_docker


def homeassistant_watchdog_api(loop, homeassistant):
    """Create scheduler task for montoring running state of API.

    Try 2 times to call API before we restart Home-Assistant. Maybe we had a
    delay in our system.
    """
    retry_scan = 0

    async def _homeassistant_watchdog_api():
        """Check running state of API and start if they is close."""
        nonlocal retry_scan

        # if Home-Assistant is active
        if not await homeassistant.is_initialize() or \
                not homeassistant.watchdog:
            return

        # if Home-Assistant API is up
        if homeassistant.in_progress or await homeassistant.check_api_state():
            return
        retry_scan += 1

        # Retry active
        if retry_scan == 1:
            _LOGGER.warning("Watchdog miss API response from Home-Assistant")
            return

        loop.create_task(homeassistant.restart())
        _LOGGER.error("Watchdog found a problem with Home-Assistant API!")
        retry_scan = 0

    return _homeassistant_watchdog_api
