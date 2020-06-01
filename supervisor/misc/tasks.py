"""A collection of tasks."""
import logging

from ..coresys import CoreSysAttributes
from ..exceptions import (
    AddonsError,
    AudioError,
    CliError,
    CoreDNSError,
    HomeAssistantError,
    MulticastError,
)

_LOGGER: logging.Logger = logging.getLogger(__name__)

HASS_WATCHDOG_API = "HASS_WATCHDOG_API"

RUN_UPDATE_SUPERVISOR = 29100
RUN_UPDATE_ADDONS = 57600
RUN_UPDATE_CLI = 28100
RUN_UPDATE_DNS = 30100
RUN_UPDATE_AUDIO = 30200
RUN_UPDATE_MULTICAST = 30300

RUN_RELOAD_ADDONS = 10800
RUN_RELOAD_SNAPSHOTS = 72000
RUN_RELOAD_HOST = 7600
RUN_RELOAD_UPDATER = 7200
RUN_RELOAD_INGRESS = 930

RUN_WATCHDOG_HOMEASSISTANT_DOCKER = 15
RUN_WATCHDOG_HOMEASSISTANT_API = 300

RUN_WATCHDOG_DNS_DOCKER = 20
RUN_WATCHDOG_AUDIO_DOCKER = 30
RUN_WATCHDOG_CLI_DOCKER = 40
RUN_WATCHDOG_MULTICAST_DOCKER = 50


class Tasks(CoreSysAttributes):
    """Handle Tasks inside Supervisor."""

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
            self.sys_scheduler.register_task(self._update_cli, RUN_UPDATE_CLI)
        )
        self.jobs.add(
            self.sys_scheduler.register_task(self._update_dns, RUN_UPDATE_DNS)
        )
        self.jobs.add(
            self.sys_scheduler.register_task(self._update_audio, RUN_UPDATE_AUDIO)
        )
        self.jobs.add(
            self.sys_scheduler.register_task(
                self._update_multicast, RUN_UPDATE_MULTICAST
            )
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
        self.jobs.add(
            self.sys_scheduler.register_task(
                self._watchdog_audio_docker, RUN_WATCHDOG_AUDIO_DOCKER
            )
        )
        self.jobs.add(
            self.sys_scheduler.register_task(
                self._watchdog_cli_docker, RUN_WATCHDOG_CLI_DOCKER
            )
        )
        self.jobs.add(
            self.sys_scheduler.register_task(
                self._watchdog_multicast_docker, RUN_WATCHDOG_MULTICAST_DOCKER
            )
        )

        _LOGGER.info("All core tasks are scheduled")

    async def _update_addons(self):
        """Check if an update is available for an Add-on and update it."""
        for addon in self.sys_addons.all:
            if not addon.is_installed or not addon.auto_update:
                continue

            if addon.version == addon.latest_version:
                continue

            if addon.test_update_schema():
                _LOGGER.info("Add-on auto update process %s", addon.slug)
                try:
                    await addon.update()
                except AddonsError:
                    _LOGGER.error("Can't auto update Add-on %s", addon.slug)
            else:
                _LOGGER.warning(
                    "Add-on %s will be ignored, schema tests fails", addon.slug
                )

    async def _update_supervisor(self):
        """Check and run update of Supervisor Supervisor."""
        if not self.sys_supervisor.need_update:
            return

        # don't perform an update on dev channel
        if self.sys_dev:
            _LOGGER.warning("Ignore Supervisor update on dev channel!")
            return

        _LOGGER.info("Found new Supervisor version")
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

    async def _update_cli(self):
        """Check and run update of cli."""
        if not self.sys_plugins.cli.need_update:
            return

        _LOGGER.info("Found new cli version")
        await self.sys_plugins.cli.update()

    async def _update_dns(self):
        """Check and run update of CoreDNS plugin."""
        if not self.sys_plugins.dns.need_update:
            return

        _LOGGER.info("Found new CoreDNS plugin version")
        await self.sys_plugins.dns.update()

    async def _update_audio(self):
        """Check and run update of PulseAudio plugin."""
        if not self.sys_plugins.audio.need_update:
            return

        _LOGGER.info("Found new PulseAudio plugin version")
        await self.sys_plugins.audio.update()

    async def _update_multicast(self):
        """Check and run update of multicast."""
        if not self.sys_plugins.multicast.need_update:
            return

        _LOGGER.info("Found new Multicast version")
        await self.sys_plugins.multicast.update()

    async def _watchdog_dns_docker(self):
        """Check running state of Docker and start if they is close."""
        # if CoreDNS is active
        if await self.sys_plugins.dns.is_running() or self.sys_plugins.dns.in_progress:
            return
        _LOGGER.warning("Watchdog found a problem with CoreDNS plugin!")

        # Reset of fails
        if await self.sys_plugins.dns.is_fails():
            _LOGGER.error("CoreDNS plugin is in fails state / Reset config")
            await self.sys_plugins.dns.reset()
            await self.sys_plugins.dns.loop_detection()

        try:
            await self.sys_plugins.dns.start()
        except CoreDNSError:
            _LOGGER.error("Watchdog CoreDNS reanimation fails!")

    async def _watchdog_audio_docker(self):
        """Check running state of Docker and start if they is close."""
        # if PulseAudio plugin is active
        if (
            await self.sys_plugins.audio.is_running()
            or self.sys_plugins.audio.in_progress
        ):
            return
        _LOGGER.warning("Watchdog found a problem with PulseAudio plugin!")

        try:
            await self.sys_plugins.audio.start()
        except AudioError:
            _LOGGER.error("Watchdog PulseAudio reanimation fails!")

    async def _watchdog_cli_docker(self):
        """Check running state of Docker and start if they is close."""
        # if cli plugin is active
        if await self.sys_plugins.cli.is_running() or self.sys_plugins.cli.in_progress:
            return
        _LOGGER.warning("Watchdog found a problem with cli plugin!")

        try:
            await self.sys_plugins.cli.start()
        except CliError:
            _LOGGER.error("Watchdog cli reanimation fails!")

    async def _watchdog_multicast_docker(self):
        """Check running state of Docker and start if they is close."""
        # if multicast plugin is active
        if (
            await self.sys_plugins.multicast.is_running()
            or self.sys_plugins.multicast.in_progress
        ):
            return
        _LOGGER.warning("Watchdog found a problem with Multicast plugin!")

        try:
            await self.sys_plugins.multicast.start()
        except MulticastError:
            _LOGGER.error("Watchdog Multicast reanimation fails!")
