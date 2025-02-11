"""Fetch last versions from webserver."""

from contextlib import suppress
from datetime import timedelta
import json
import logging

import aiohttp
from awesomeversion import AwesomeVersion

from supervisor.jobs.const import JobConcurrency, JobThrottle

from .bus import EventListener
from .const import (
    ATTR_AUDIO,
    ATTR_AUTO_UPDATE,
    ATTR_CHANNEL,
    ATTR_CLI,
    ATTR_DNS,
    ATTR_HASSOS_UNRESTRICTED,
    ATTR_HASSOS_UPGRADE,
    ATTR_HOMEASSISTANT,
    ATTR_IMAGE,
    ATTR_MULTICAST,
    ATTR_OBSERVER,
    ATTR_OTA,
    ATTR_SUPERVISOR,
    FILE_HASSIO_UPDATER,
    URL_HASSIO_VERSION,
    BusEvent,
    UpdateChannel,
)
from .coresys import CoreSys, CoreSysAttributes
from .exceptions import UpdaterError, UpdaterJobError
from .jobs.decorator import Job, JobCondition
from .utils.common import FileConfiguration
from .validate import SCHEMA_UPDATER_CONFIG

_LOGGER: logging.Logger = logging.getLogger(__name__)


class Updater(FileConfiguration, CoreSysAttributes):
    """Fetch last versions from version.json."""

    def __init__(self, coresys: CoreSys) -> None:
        """Initialize updater."""
        super().__init__(FILE_HASSIO_UPDATER, SCHEMA_UPDATER_CONFIG)
        self.coresys = coresys
        self._connectivity_listener: EventListener | None = None

    async def load(self) -> None:
        """Update internal data."""
        # Delay loading data by default so JobCondition.OS_SUPPORTED works.
        # Use HAOS unrestricted as indicator as this is what we need to evaluate
        # if the operating system version is supported.
        if self.sys_os.board and self.version_hassos_unrestricted is None:
            _LOGGER.info(
                "No OS update information found, force refreshing updater information"
            )
            await self.reload()

    async def reload(self) -> None:
        """Update internal data."""
        # If there's no connectivity, delay initial version fetch
        if not self.sys_supervisor.connectivity:
            _LOGGER.debug("No Supervisor connectivity, delaying version fetch")
            if not self._connectivity_listener:
                self._connectivity_listener = self.sys_bus.register_event(
                    BusEvent.SUPERVISOR_CONNECTIVITY_CHANGE, self._check_connectivity
                )
            _LOGGER.info("No Supervisor connectivity, delaying version fetch")
            return

        with suppress(UpdaterError):
            await self.fetch_data()

    @property
    def version_homeassistant(self) -> AwesomeVersion | None:
        """Return latest version of Home Assistant."""
        return self._data.get(ATTR_HOMEASSISTANT)

    @property
    def version_supervisor(self) -> AwesomeVersion | None:
        """Return latest version of Supervisor."""
        return self._data.get(ATTR_SUPERVISOR)

    @property
    def version_hassos(self) -> AwesomeVersion | None:
        """Return latest version of HassOS."""
        upgrade_map = self.upgrade_map_hassos
        unrestricted = self.version_hassos_unrestricted

        # If no upgrade map exists, fall back to unrestricted version
        if not upgrade_map:
            return unrestricted

        # If we have no unrestricted version or no current OS version, return unrestricted
        if (
            not unrestricted
            or not self.sys_os.version
            or self.sys_os.version.major is None
        ):
            return unrestricted

        current_major = str(self.sys_os.version.major)
        # Check if there's an upgrade path for current major version
        if current_major in upgrade_map:
            last_in_major = AwesomeVersion(upgrade_map[current_major])
            # If we're not at the last version in our major, upgrade to that first
            if self.sys_os.version != last_in_major:
                return last_in_major
            # If we are at the last version in our major, check for next major
            next_major = str(int(self.sys_os.version.major) + 1)
            if next_major in upgrade_map:
                return AwesomeVersion(upgrade_map[next_major])

        # Fall back to unrestricted version
        return unrestricted

    @property
    def version_hassos_unrestricted(self) -> AwesomeVersion | None:
        """Return latest version of HassOS ignoring upgrade restrictions."""
        return self._data.get(ATTR_HASSOS_UNRESTRICTED)

    @property
    def upgrade_map_hassos(self) -> dict[str, str] | None:
        """Return HassOS upgrade map."""
        return self._data.get(ATTR_HASSOS_UPGRADE)

    @property
    def version_cli(self) -> AwesomeVersion | None:
        """Return latest version of CLI."""
        return self._data.get(ATTR_CLI)

    @property
    def version_dns(self) -> AwesomeVersion | None:
        """Return latest version of DNS."""
        return self._data.get(ATTR_DNS)

    @property
    def version_audio(self) -> AwesomeVersion | None:
        """Return latest version of Audio."""
        return self._data.get(ATTR_AUDIO)

    @property
    def version_observer(self) -> AwesomeVersion | None:
        """Return latest version of Observer."""
        return self._data.get(ATTR_OBSERVER)

    @property
    def version_multicast(self) -> AwesomeVersion | None:
        """Return latest version of Multicast."""
        return self._data.get(ATTR_MULTICAST)

    @property
    def image_homeassistant(self) -> str | None:
        """Return image of Home Assistant docker."""
        if ATTR_HOMEASSISTANT not in self._data[ATTR_IMAGE]:
            return None
        return self._data[ATTR_IMAGE][ATTR_HOMEASSISTANT].format(
            machine=self.sys_machine
        )

    @property
    def image_supervisor(self) -> str | None:
        """Return image of Supervisor docker."""
        if ATTR_SUPERVISOR not in self._data[ATTR_IMAGE]:
            return None
        return self._data[ATTR_IMAGE][ATTR_SUPERVISOR].format(
            arch=self.sys_arch.supervisor
        )

    @property
    def image_cli(self) -> str | None:
        """Return image of CLI docker."""
        if ATTR_CLI not in self._data[ATTR_IMAGE]:
            return None
        return self._data[ATTR_IMAGE][ATTR_CLI].format(arch=self.sys_arch.supervisor)

    @property
    def image_dns(self) -> str | None:
        """Return image of DNS docker."""
        if ATTR_DNS not in self._data[ATTR_IMAGE]:
            return None
        return self._data[ATTR_IMAGE][ATTR_DNS].format(arch=self.sys_arch.supervisor)

    @property
    def image_audio(self) -> str | None:
        """Return image of Audio docker."""
        if ATTR_AUDIO not in self._data[ATTR_IMAGE]:
            return None
        return self._data[ATTR_IMAGE][ATTR_AUDIO].format(arch=self.sys_arch.supervisor)

    @property
    def image_observer(self) -> str | None:
        """Return image of Observer docker."""
        if ATTR_OBSERVER not in self._data[ATTR_IMAGE]:
            return None
        return self._data[ATTR_IMAGE][ATTR_OBSERVER].format(
            arch=self.sys_arch.supervisor
        )

    @property
    def image_multicast(self) -> str | None:
        """Return image of Multicast docker."""
        if ATTR_MULTICAST not in self._data[ATTR_IMAGE]:
            return None
        return self._data[ATTR_IMAGE][ATTR_MULTICAST].format(
            arch=self.sys_arch.supervisor
        )

    @property
    def ota_url(self) -> str | None:
        """Return OTA url for OS."""
        return self._data.get(ATTR_OTA)

    @property
    def channel(self) -> UpdateChannel:
        """Return upstream channel of Supervisor instance."""
        return self._data[ATTR_CHANNEL]

    @channel.setter
    def channel(self, value: UpdateChannel):
        """Set upstream mode."""
        self._data[ATTR_CHANNEL] = value

    @property
    def auto_update(self) -> bool:
        """Return if Supervisor auto updates enabled."""
        return self._data[ATTR_AUTO_UPDATE]

    @auto_update.setter
    def auto_update(self, value: bool) -> None:
        """Set Supervisor auto updates enabled."""
        self._data[ATTR_AUTO_UPDATE] = value

    async def _check_connectivity(self, connectivity: bool):
        """Fetch data once connectivity is true."""
        if connectivity:
            await self.reload()

    @Job(
        name="updater_fetch_data",
        conditions=[
            JobCondition.ARCHITECTURE_SUPPORTED,
            JobCondition.INTERNET_SYSTEM,
            JobCondition.HOME_ASSISTANT_CORE_SUPPORTED,
            JobCondition.OS_SUPPORTED,
        ],
        on_condition=UpdaterJobError,
        throttle_period=timedelta(seconds=30),
        concurrency=JobConcurrency.QUEUE,
        throttle=JobThrottle.THROTTLE,
    )
    async def fetch_data(self):
        """Fetch current versions from Github.

        Is a coroutine.
        """
        url = URL_HASSIO_VERSION.format(channel=self.channel)
        machine = self.sys_machine or "default"

        # Get data
        try:
            _LOGGER.info("Fetching update data from %s", url)
            timeout = aiohttp.ClientTimeout(total=10)
            async with self.sys_websession.get(url, timeout=timeout) as request:
                if request.status != 200:
                    raise UpdaterError(
                        f"Fetching version from {url} response with {request.status}",
                        _LOGGER.warning,
                    )
                data = await request.read()

        except (aiohttp.ClientError, TimeoutError) as err:
            self.sys_supervisor.connectivity = False
            raise UpdaterError(
                f"Can't fetch versions from {url}: {str(err) or 'Timeout'}",
                _LOGGER.warning,
            ) from err

        # Fetch was successful. If there's a connectivity listener, time to remove it
        if self._connectivity_listener:
            self.sys_bus.remove_listener(self._connectivity_listener)
            self._connectivity_listener = None

        # Parse data
        try:
            data = json.loads(data)
        except json.JSONDecodeError as err:
            raise UpdaterError(
                f"Can't parse versions from {url}: {err}", _LOGGER.warning
            ) from err

        # data valid?
        if not data or data.get(ATTR_CHANNEL) != self.channel:
            raise UpdaterError(f"Invalid data from {url}", _LOGGER.warning)

        events = ["supervisor", "core"]
        try:
            # Update supervisor version
            self._data[ATTR_SUPERVISOR] = AwesomeVersion(data["supervisor"])

            # Update Home Assistant core version
            self._data[ATTR_HOMEASSISTANT] = AwesomeVersion(
                data["homeassistant"][machine]
            )

            # Update HassOS version
            if self.sys_os.board:
                self._data[ATTR_OTA] = data["ota"]
                if version := data["hassos"].get(self.sys_os.board):
                    self._data[ATTR_HASSOS_UNRESTRICTED] = AwesomeVersion(version)
                    # Store the upgrade map for persistent access
                    self._data[ATTR_HASSOS_UPGRADE] = data.get("hassos-upgrade", {})
                    events.append("os")
                else:
                    _LOGGER.warning(
                        "Board '%s' not found in version file. No OS updates.",
                        self.sys_os.board,
                    )

            # Update Home Assistant plugins
            self._data[ATTR_CLI] = AwesomeVersion(data["cli"])
            self._data[ATTR_DNS] = AwesomeVersion(data["dns"])
            self._data[ATTR_AUDIO] = AwesomeVersion(data["audio"])
            self._data[ATTR_OBSERVER] = AwesomeVersion(data["observer"])
            self._data[ATTR_MULTICAST] = AwesomeVersion(data["multicast"])

            # Update images for that versions
            self._data[ATTR_IMAGE][ATTR_HOMEASSISTANT] = data["images"]["core"]
            self._data[ATTR_IMAGE][ATTR_SUPERVISOR] = data["images"]["supervisor"]
            self._data[ATTR_IMAGE][ATTR_AUDIO] = data["images"]["audio"]
            self._data[ATTR_IMAGE][ATTR_CLI] = data["images"]["cli"]
            self._data[ATTR_IMAGE][ATTR_DNS] = data["images"]["dns"]
            self._data[ATTR_IMAGE][ATTR_OBSERVER] = data["images"]["observer"]
            self._data[ATTR_IMAGE][ATTR_MULTICAST] = data["images"]["multicast"]

        except KeyError as err:
            raise UpdaterError(
                f"Can't process version data: {err}", _LOGGER.warning
            ) from err

        await self.save_data()

        # Send status update to core
        for event in events:
            self.sys_homeassistant.websocket.supervisor_update_event(event)
