"""A collection of tasks."""
import logging

from ..const import AddonState, HostFeature
from ..coresys import CoreSysAttributes
from ..exceptions import (
    AddonsError,
    AudioError,
    CliError,
    CoreDNSError,
    HomeAssistantError,
    MulticastError,
    ObserverError,
)
from ..jobs.decorator import Job, JobCondition

_LOGGER: logging.Logger = logging.getLogger(__name__)

HASS_WATCHDOG_API = "HASS_WATCHDOG_API"

RUN_UPDATE_SUPERVISOR = 29100
RUN_UPDATE_ADDONS = 57600
RUN_UPDATE_CLI = 28100
RUN_UPDATE_DNS = 30100
RUN_UPDATE_AUDIO = 30200
RUN_UPDATE_MULTICAST = 30300
RUN_UPDATE_OBSERVER = 30400

RUN_RELOAD_ADDONS = 10800
RUN_RELOAD_SNAPSHOTS = 72000
RUN_RELOAD_HOST = 7600
RUN_RELOAD_UPDATER = 7200
RUN_RELOAD_INGRESS = 930

RUN_WATCHDOG_HOMEASSISTANT_DOCKER = 15
RUN_WATCHDOG_HOMEASSISTANT_API = 120

RUN_WATCHDOG_DNS_DOCKER = 30
RUN_WATCHDOG_AUDIO_DOCKER = 60
RUN_WATCHDOG_CLI_DOCKER = 60
RUN_WATCHDOG_OBSERVER_DOCKER = 60
RUN_WATCHDOG_MULTICAST_DOCKER = 60

RUN_WATCHDOG_ADDON_DOCKER = 30
RUN_WATCHDOG_ADDON_APPLICATON = 120
RUN_WATCHDOG_OBSERVER_APPLICATION = 180

RUN_REFRESH_ADDON = 15

RUN_CHECK_CONNECTIVITY = 30


class Tasks(CoreSysAttributes):
    """Handle Tasks inside Supervisor."""

    def __init__(self, coresys):
        """Initialize Tasks."""
        self.coresys = coresys
        self._cache = {}

    async def load(self):
        """Add Tasks to scheduler."""
        # Update
        self.sys_scheduler.register_task(self._update_addons, RUN_UPDATE_ADDONS)
        self.sys_scheduler.register_task(self._update_supervisor, RUN_UPDATE_SUPERVISOR)
        self.sys_scheduler.register_task(self._update_cli, RUN_UPDATE_CLI)
        self.sys_scheduler.register_task(self._update_dns, RUN_UPDATE_DNS)
        self.sys_scheduler.register_task(self._update_audio, RUN_UPDATE_AUDIO)
        self.sys_scheduler.register_task(self._update_multicast, RUN_UPDATE_MULTICAST)
        self.sys_scheduler.register_task(self._update_observer, RUN_UPDATE_OBSERVER)

        # Reload
        self.sys_scheduler.register_task(self.sys_store.reload, RUN_RELOAD_ADDONS)
        self.sys_scheduler.register_task(self.sys_updater.reload, RUN_RELOAD_UPDATER)
        self.sys_scheduler.register_task(
            self.sys_snapshots.reload, RUN_RELOAD_SNAPSHOTS
        )
        self.sys_scheduler.register_task(self.sys_host.reload, RUN_RELOAD_HOST)
        self.sys_scheduler.register_task(self.sys_ingress.reload, RUN_RELOAD_INGRESS)

        # Watchdog
        self.sys_scheduler.register_task(
            self._watchdog_homeassistant_docker, RUN_WATCHDOG_HOMEASSISTANT_DOCKER
        )
        self.sys_scheduler.register_task(
            self._watchdog_homeassistant_api, RUN_WATCHDOG_HOMEASSISTANT_API
        )
        self.sys_scheduler.register_task(
            self._watchdog_dns_docker, RUN_WATCHDOG_DNS_DOCKER
        )
        self.sys_scheduler.register_task(
            self._watchdog_audio_docker, RUN_WATCHDOG_AUDIO_DOCKER
        )
        self.sys_scheduler.register_task(
            self._watchdog_cli_docker, RUN_WATCHDOG_CLI_DOCKER
        )
        self.sys_scheduler.register_task(
            self._watchdog_observer_docker, RUN_WATCHDOG_OBSERVER_DOCKER
        )
        self.sys_scheduler.register_task(
            self._watchdog_observer_application, RUN_WATCHDOG_OBSERVER_APPLICATION
        )
        self.sys_scheduler.register_task(
            self._watchdog_multicast_docker, RUN_WATCHDOG_MULTICAST_DOCKER
        )
        self.sys_scheduler.register_task(
            self._watchdog_addon_docker, RUN_WATCHDOG_ADDON_DOCKER
        )
        self.sys_scheduler.register_task(
            self._watchdog_addon_application, RUN_WATCHDOG_ADDON_APPLICATON
        )

        # Refresh
        self.sys_scheduler.register_task(self._refresh_addon, RUN_REFRESH_ADDON)

        # Connectivity
        self.sys_scheduler.register_task(
            self._check_connectivity, RUN_CHECK_CONNECTIVITY
        )

        _LOGGER.info("All core tasks are scheduled")

    @Job(
        conditions=[
            JobCondition.HEALTHY,
            JobCondition.FREE_SPACE,
            JobCondition.INTERNET_HOST,
        ]
    )
    async def _update_addons(self):
        """Check if an update is available for an Add-on and update it."""
        for addon in self.sys_addons.all:
            if not addon.is_installed or not addon.auto_update:
                continue

            # Evaluate available updates
            if not addon.need_update:
                continue
            if not addon.test_update_schema():
                _LOGGER.warning(
                    "Add-on %s will be ignored, schema tests failed", addon.slug
                )
                continue

            # Run Add-on update sequential
            # avoid issue on slow IO
            _LOGGER.info("Add-on auto update process %s", addon.slug)
            try:
                await addon.update()
            except AddonsError:
                _LOGGER.error("Can't auto update Add-on %s", addon.slug)

    @Job(conditions=[JobCondition.FREE_SPACE, JobCondition.INTERNET_HOST])
    async def _update_supervisor(self):
        """Check and run update of Supervisor Supervisor."""
        if not self.sys_supervisor.need_update:
            return

        _LOGGER.info(
            "Found new Supervisor version %s, updating",
            self.sys_supervisor.latest_version,
        )
        await self.sys_supervisor.update()

    async def _watchdog_homeassistant_docker(self):
        """Check running state of Docker and start if they is close."""
        # if Home Assistant is active
        if (
            not await self.sys_homeassistant.core.is_failed()
            or not self.sys_homeassistant.watchdog
            or self.sys_homeassistant.error_state
        ):
            return

        # if Home Assistant is running
        if (
            self.sys_homeassistant.core.in_progress
            or await self.sys_homeassistant.core.is_running()
        ):
            return

        _LOGGER.warning("Watchdog found a problem with Home Assistant Docker!")
        try:
            await self.sys_homeassistant.core.start()
        except HomeAssistantError as err:
            _LOGGER.error("Home Assistant watchdog reanimation failed!")
            self.sys_capture_exception(err)
        else:
            return

        _LOGGER.info("Rebuilding the Home Assistant Container")
        await self.sys_homeassistant.core.rebuild()

    async def _watchdog_homeassistant_api(self):
        """Create scheduler task for monitoring running state of API.

        Try 2 times to call API before we restart Home-Assistant. Maybe we had
        a delay in our system.
        """
        # If Home-Assistant is active
        if (
            not await self.sys_homeassistant.core.is_failed()
            or not self.sys_homeassistant.watchdog
            or self.sys_homeassistant.error_state
        ):
            return

        # Init cache data
        retry_scan = self._cache.get(HASS_WATCHDOG_API, 0)

        # If Home-Assistant API is up
        if (
            self.sys_homeassistant.core.in_progress
            or await self.sys_homeassistant.api.check_api_state()
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
            await self.sys_homeassistant.core.restart()
        except HomeAssistantError as err:
            _LOGGER.error("Home Assistant watchdog reanimation failed!")
            self.sys_capture_exception(err)
        finally:
            self._cache[HASS_WATCHDOG_API] = 0

    async def _update_cli(self):
        """Check and run update of cli."""
        if not self.sys_plugins.cli.need_update:
            return

        _LOGGER.info(
            "Found new cli version %s, updating", self.sys_plugins.cli.latest_version
        )
        await self.sys_plugins.cli.update()

    async def _update_dns(self):
        """Check and run update of CoreDNS plugin."""
        if not self.sys_plugins.dns.need_update:
            return

        _LOGGER.info(
            "Found new CoreDNS plugin version %s, updating",
            self.sys_plugins.dns.latest_version,
        )
        await self.sys_plugins.dns.update()

    async def _update_audio(self):
        """Check and run update of PulseAudio plugin."""
        if not self.sys_plugins.audio.need_update:
            return

        _LOGGER.info(
            "Found new PulseAudio plugin version %s, updating",
            self.sys_plugins.audio.latest_version,
        )
        await self.sys_plugins.audio.update()

    async def _update_observer(self):
        """Check and run update of Observer plugin."""
        if not self.sys_plugins.observer.need_update:
            return

        _LOGGER.info(
            "Found new Observer plugin version %s, updating",
            self.sys_plugins.observer.latest_version,
        )
        await self.sys_plugins.observer.update()

    async def _update_multicast(self):
        """Check and run update of multicast."""
        if not self.sys_plugins.multicast.need_update:
            return

        _LOGGER.info(
            "Found new Multicast version %s, updating",
            self.sys_plugins.multicast.latest_version,
        )
        await self.sys_plugins.multicast.update()

    async def _watchdog_dns_docker(self):
        """Check running state of Docker and start if they is close."""
        # if CoreDNS is active
        if await self.sys_plugins.dns.is_running() or self.sys_plugins.dns.in_progress:
            return
        _LOGGER.warning("Watchdog found a problem with CoreDNS plugin!")

        # Detect loop
        await self.sys_plugins.dns.loop_detection()

        try:
            await self.sys_plugins.dns.start()
        except CoreDNSError:
            _LOGGER.error("CoreDNS watchdog reanimation failed!")

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
            _LOGGER.error("PulseAudio watchdog reanimation failed!")

    async def _watchdog_cli_docker(self):
        """Check running state of Docker and start if they is close."""
        # if cli plugin is active
        if await self.sys_plugins.cli.is_running() or self.sys_plugins.cli.in_progress:
            return
        _LOGGER.warning("Watchdog found a problem with cli plugin!")

        try:
            await self.sys_plugins.cli.start()
        except CliError:
            _LOGGER.error("CLI watchdog reanimation failed!")

    async def _watchdog_observer_docker(self):
        """Check running state of Docker and start if they is close."""
        # if observer plugin is active
        if (
            await self.sys_plugins.observer.is_running()
            or self.sys_plugins.observer.in_progress
        ):
            return
        _LOGGER.warning("Watchdog/Docker found a problem with observer plugin!")

        try:
            await self.sys_plugins.observer.start()
        except ObserverError:
            _LOGGER.error("Observer watchdog reanimation failed!")

    async def _watchdog_observer_application(self):
        """Check running state of application and rebuild if they is not response."""
        # if observer plugin is active
        if (
            self.sys_plugins.observer.in_progress
            or await self.sys_plugins.observer.check_system_runtime()
        ):
            return
        _LOGGER.warning("Watchdog/Application found a problem with observer plugin!")

        try:
            await self.sys_plugins.observer.rebuild()
        except ObserverError:
            _LOGGER.error("Observer watchdog reanimation failed!")

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
            _LOGGER.error("Multicast watchdog reanimation failed!")

    async def _watchdog_addon_docker(self):
        """Check running state  of Docker and start if they is close."""
        for addon in self.sys_addons.installed:
            # if watchdog need looking for
            if not addon.watchdog or await addon.is_running():
                continue

            # if Addon have running actions
            if addon.in_progress or addon.state != AddonState.STARTED:
                continue

            _LOGGER.warning("Watchdog found a problem with %s!", addon.slug)
            try:
                await addon.start()
            except AddonsError as err:
                _LOGGER.error("%s watchdog reanimation failed with %s", addon.slug, err)
                self.sys_capture_exception(err)

    async def _watchdog_addon_application(self):
        """Check running state of the application and start if they is hangs."""
        for addon in self.sys_addons.installed:
            # if watchdog need looking for
            if not addon.watchdog or addon.state != AddonState.STARTED:
                continue

            # Init cache data
            retry_scan = self._cache.get(addon.slug, 0)

            # if Addon have running actions / Application work
            if addon.in_progress or await addon.watchdog_application():
                continue

            # Look like we run into a problem
            retry_scan += 1
            if retry_scan == 1:
                self._cache[addon.slug] = retry_scan
                _LOGGER.warning(
                    "Watchdog missing application response from %s", addon.slug
                )
                return

            _LOGGER.warning("Watchdog found a problem with %s application!", addon.slug)
            try:
                await addon.restart()
            except AddonsError as err:
                _LOGGER.error("%s watchdog reanimation failed with %s", addon.slug, err)
                self.sys_capture_exception(err)
            finally:
                self._cache[addon.slug] = 0

    async def _refresh_addon(self) -> None:
        """Refresh addon state."""
        for addon in self.sys_addons.installed:
            # if watchdog need looking for
            if addon.watchdog or addon.state != AddonState.STARTED:
                continue

            # if Addon have running actions
            if addon.in_progress or await addon.is_running():
                continue

            # Adjust state
            addon.state = AddonState.STOPPED

    async def _check_connectivity(self) -> None:
        """Check system connectivity."""
        value = self._cache.get("connectivity", 0)

        # Need only full check if not connected or each 10min
        if value >= 600:
            pass
        elif (
            self.sys_supervisor.connectivity
            and self.sys_host.network.connectivity is None
        ) or (
            self.sys_supervisor.connectivity
            and self.sys_host.network.connectivity is not None
            and self.sys_host.network.connectivity
        ):
            self._cache["connectivity"] = value + RUN_CHECK_CONNECTIVITY
            return

        # Check connectivity
        try:
            await self.sys_supervisor.check_connectivity()
            if HostFeature.NETWORK in self.sys_host.supported_features:
                await self.sys_host.network.check_connectivity()
        finally:
            self._cache["connectivity"] = 0
