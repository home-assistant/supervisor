"""A collection of tasks."""
import asyncio
import logging

from .coresys import CoreSysAttributes
from .exceptions import HomeAssistantError, CoreDNSError

_LOGGER = logging.getLogger(__name__)

HASS_WATCHDOG_API = "HASS_WATCHDOG_API"

RUN_UPDATE_SUPERVISOR = 29100
RUN_UPDATE_ADDONS = 57600
RUN_UPDATE_HASSOSCLI = 28100
RUN_UPDATE_DNS = 30100

RUN_RELOAD_ADDONS = 10800
RUN_RELOAD_SNAPSHOTS = 72000
RUN_RELOAD_HOST = 72000
RUN_RELOAD_UPDATER = 7200
RUN_RELOAD_INGRESS = 930

RUN_WATCHDOG_HOMEASSISTANT_DOCKER = 15
RUN_WATCHDOG_HOMEASSISTANT_API = 300

RUN_WATCHDOG_DNS_DOCKER = 20


class Tasks(CoreSysAttributes):
    """Handle Tasks inside Hass.io."""

    def __init__(self, coresys):
        """Initialize Tasks."""
        self.coresys = coresys
        self.jobs = set()
        self._cache = {}

    async def load(self):
        """Add Tasks to scheduler."""
        # Update
        self.jobs.add(
            self.sys_scheduler.register_task(self._update_addons, RUN_UPDATE_ADDONS)
        )
        self.jobs.add(
            self.sys_scheduler.register_task(
                self._update_supervisor, RUN_UPDATE_SUPERVISOR
            )
        )
        self.jobs.add(
            self.sys_scheduler.register_task(
                self._update_hassos_cli, RUN_UPDATE_HASSOSCLI
            )
        )
        self.jobs.add(
            self.sys_scheduler.register_task(self._update_dns, RUN_UPDATE_DNS)
        )

        # Reload
        self.jobs.add(
            self.sys_scheduler.register_task(self.sys_store.reload, RUN_RELOAD_ADDONS)
        )
        self.jobs.add(
            self.sys_scheduler.register_task(
                self.sys_updater.reload, RUN_RELOAD_UPDATER
            )
        )
        self.jobs.add(
            self.sys_scheduler.register_task(
                self.sys_snapshots.reload, RUN_RELOAD_SNAPSHOTS
            )
        )
        self.jobs.add(
            self.sys_scheduler.register_task(self.sys_host.reload, RUN_RELOAD_HOST)
        )
        self.jobs.add(
            self.sys_scheduler.register_task(
                self.sys_ingress.reload, RUN_RELOAD_INGRESS
            )
        )

        # Watchdog
        self.jobs.add(
            self.sys_scheduler.register_task(
                self._watchdog_homeassistant_docker, RUN_WATCHDOG_HOMEASSISTANT_DOCKER
            )
        )
        self.jobs.add(
            self.sys_scheduler.register_task(
                self._watchdog_homeassistant_api, RUN_WATCHDOG_HOMEASSISTANT_API
            )
        )
        self.jobs.add(
            self.sys_scheduler.register_task(
                self._watchdog_dns_docker, RUN_WATCHDOG_DNS_DOCKER
            )
        )

        _LOGGER.info("All core tasks are scheduled")

    async def _update_addons(self):
        """Check if an update is available for an Add-on and update it."""
        tasks = []
        for addon in self.sys_addons.all:
            if not addon.is_installed or not addon.auto_update:
                continue

            if addon.version == addon.latest_version:
                continue

            if addon.test_update_schema():
                tasks.append(addon.update())
            else:
                _LOGGER.warning(
                    "Add-on %s will be ignored, schema tests fails", addon.slug
                )

        if tasks:
            _LOGGER.info("Add-on auto update process %d tasks", len(tasks))
            await asyncio.wait(tasks)

    async def _update_supervisor(self):
        """Check and run update of Supervisor Hass.io."""
        if not self.sys_supervisor.need_update:
            return

        # don't perform an update on dev channel
        if self.sys_dev:
            _LOGGER.warning("Ignore Hass.io update on dev channel!")
            return

        _LOGGER.info("Found new Hass.io version")
        await self.sys_supervisor.update()

    async def _watchdog_homeassistant_docker(self):
        """Check running state of Docker and start if they is close."""
        # if Home Assistant is active
        if (
            not await self.sys_homeassistant.is_fails()
            or not self.sys_homeassistant.watchdog
            or self.sys_homeassistant.error_state
        ):
            return

        # if Home Assistant is running
        if (
            self.sys_homeassistant.in_progress
            or await self.sys_homeassistant.is_running()
        ):
            return

        _LOGGER.warning("Watchdog found a problem with Home Assistant Docker!")
        try:
            await self.sys_homeassistant.start()
        except HomeAssistantError:
            _LOGGER.error("Watchdog Home Assistant reanimation fails!")

    async def _watchdog_homeassistant_api(self):
        """Create scheduler task for monitoring running state of API.

        Try 2 times to call API before we restart Home-Assistant. Maybe we had
        a delay in our system.
        """
        # If Home-Assistant is active
        if (
            not await self.sys_homeassistant.is_fails()
            or not self.sys_homeassistant.watchdog
            or self.sys_homeassistant.error_state
        ):
            return

        # Init cache data
        retry_scan = self._cache.get(HASS_WATCHDOG_API, 0)

        # If Home-Assistant API is up
        if (
            self.sys_homeassistant.in_progress
            or await self.sys_homeassistant.check_api_state()
        ):
            return

        # Look like we run into a problem
        retry_scan += 1
        if retry_scan == 1:
            self._cache[HASS_WATCHDOG_API] = retry_scan
            _LOGGER.warning("Watchdog miss API response from Home Assistant")
            return

        _LOGGER.error("Watchdog found a problem with Home Assistant API!")
        try:
            await self.sys_homeassistant.restart()
        except HomeAssistantError:
            _LOGGER.error("Watchdog Home Assistant reanimation fails!")
        finally:
            self._cache[HASS_WATCHDOG_API] = 0

    async def _update_hassos_cli(self):
        """Check and run update of HassOS CLI."""
        if not self.sys_hassos.need_cli_update:
            return

        # don't perform an update on dev channel
        if self.sys_dev:
            _LOGGER.warning("Ignore HassOS CLI update on dev channel!")
            return

        _LOGGER.info("Found new HassOS CLI version")
        await self.sys_hassos.update_cli()

    async def _update_dns(self):
        """Check and run update of CoreDNS plugin."""
        if not self.sys_dns.need_update:
            return

        # don't perform an update on dev channel
        if self.sys_dev:
            _LOGGER.warning("Ignore CoreDNS update on dev channel!")
            return

        _LOGGER.info("Found new CoreDNS plugin version")
        await self.sys_dns.update()

    async def _watchdog_dns_docker(self):
        """Check running state of Docker and start if they is close."""
        # if Home Assistant is active
        if await self.sys_dns.is_running():
            return
        _LOGGER.warning("Watchdog found a problem with CoreDNS plugin!")

        if await self.sys_dns.is_fails():
            _LOGGER.warning("CoreDNS plugin is in fails state / Reset config")
            await self.sys_dns.reset()

        try:
            await self.sys_dns.start()
        except CoreDNSError:
            _LOGGER.error("Watchdog CoreDNS reanimation fails!")
