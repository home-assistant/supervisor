"""Fetch last versions from webserver."""
import asyncio
from contextlib import suppress
from datetime import timedelta
import json
import logging
from typing import Optional

import aiohttp
from awesomeversion import AwesomeVersion

from supervisor.jobs.const import JobExecutionLimit

from .const import (
    ATTR_AUDIO,
    ATTR_CHANNEL,
    ATTR_CLI,
    ATTR_DNS,
    ATTR_HASSOS,
    ATTR_HOMEASSISTANT,
    ATTR_IMAGE,
    ATTR_MULTICAST,
    ATTR_OBSERVER,
    ATTR_OTA,
    ATTR_SUPERVISOR,
    FILE_HASSIO_UPDATER,
    URL_HASSIO_VERSION,
    UpdateChannel,
)
from .coresys import CoreSysAttributes
from .exceptions import (
    CodeNotaryError,
    CodeNotaryUntrusted,
    UpdaterError,
    UpdaterJobError,
)
from .jobs.decorator import Job, JobCondition
from .utils.codenotary import calc_checksum
from .utils.common import FileConfiguration
from .validate import SCHEMA_UPDATER_CONFIG

_LOGGER: logging.Logger = logging.getLogger(__name__)


class Updater(FileConfiguration, CoreSysAttributes):
    """Fetch last versions from version.json."""

    def __init__(self, coresys):
        """Initialize updater."""
        super().__init__(FILE_HASSIO_UPDATER, SCHEMA_UPDATER_CONFIG)
        self.coresys = coresys

    async def load(self) -> None:
        """Update internal data."""
        with suppress(UpdaterError):
            await self.fetch_data()

    async def reload(self) -> None:
        """Update internal data."""
        with suppress(UpdaterError):
            await self.fetch_data()

    @property
    def version_homeassistant(self) -> Optional[AwesomeVersion]:
        """Return latest version of Home Assistant."""
        return self._data.get(ATTR_HOMEASSISTANT)

    @property
    def version_supervisor(self) -> Optional[AwesomeVersion]:
        """Return latest version of Supervisor."""
        return self._data.get(ATTR_SUPERVISOR)

    @property
    def version_hassos(self) -> Optional[AwesomeVersion]:
        """Return latest version of HassOS."""
        return self._data.get(ATTR_HASSOS)

    @property
    def version_cli(self) -> Optional[AwesomeVersion]:
        """Return latest version of CLI."""
        return self._data.get(ATTR_CLI)

    @property
    def version_dns(self) -> Optional[AwesomeVersion]:
        """Return latest version of DNS."""
        return self._data.get(ATTR_DNS)

    @property
    def version_audio(self) -> Optional[AwesomeVersion]:
        """Return latest version of Audio."""
        return self._data.get(ATTR_AUDIO)

    @property
    def version_observer(self) -> Optional[AwesomeVersion]:
        """Return latest version of Observer."""
        return self._data.get(ATTR_OBSERVER)

    @property
    def version_multicast(self) -> Optional[AwesomeVersion]:
        """Return latest version of Multicast."""
        return self._data.get(ATTR_MULTICAST)

    @property
    def image_homeassistant(self) -> Optional[str]:
        """Return image of Home Assistant docker."""
        if ATTR_HOMEASSISTANT not in self._data[ATTR_IMAGE]:
            return None
        return self._data[ATTR_IMAGE][ATTR_HOMEASSISTANT].format(
            machine=self.sys_machine
        )

    @property
    def image_supervisor(self) -> Optional[str]:
        """Return image of Supervisor docker."""
        if ATTR_SUPERVISOR not in self._data[ATTR_IMAGE]:
            return None
        return self._data[ATTR_IMAGE][ATTR_SUPERVISOR].format(
            arch=self.sys_arch.supervisor
        )

    @property
    def image_cli(self) -> Optional[str]:
        """Return image of CLI docker."""
        if ATTR_CLI not in self._data[ATTR_IMAGE]:
            return None
        return self._data[ATTR_IMAGE][ATTR_CLI].format(arch=self.sys_arch.supervisor)

    @property
    def image_dns(self) -> Optional[str]:
        """Return image of DNS docker."""
        if ATTR_DNS not in self._data[ATTR_IMAGE]:
            return None
        return self._data[ATTR_IMAGE][ATTR_DNS].format(arch=self.sys_arch.supervisor)

    @property
    def image_audio(self) -> Optional[str]:
        """Return image of Audio docker."""
        if ATTR_AUDIO not in self._data[ATTR_IMAGE]:
            return None
        return self._data[ATTR_IMAGE][ATTR_AUDIO].format(arch=self.sys_arch.supervisor)

    @property
    def image_observer(self) -> Optional[str]:
        """Return image of Observer docker."""
        if ATTR_OBSERVER not in self._data[ATTR_IMAGE]:
            return None
        return self._data[ATTR_IMAGE][ATTR_OBSERVER].format(
            arch=self.sys_arch.supervisor
        )

    @property
    def image_multicast(self) -> Optional[str]:
        """Return image of Multicast docker."""
        if ATTR_MULTICAST not in self._data[ATTR_IMAGE]:
            return None
        return self._data[ATTR_IMAGE][ATTR_MULTICAST].format(
            arch=self.sys_arch.supervisor
        )

    @property
    def ota_url(self) -> Optional[str]:
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

    @Job(
        conditions=[JobCondition.INTERNET_SYSTEM],
        on_condition=UpdaterJobError,
        limit=JobExecutionLimit.THROTTLE_WAIT,
        throttle_period=timedelta(seconds=30),
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
            async with self.sys_websession.get(url, timeout=10) as request:
                data = await request.read()

        except (aiohttp.ClientError, asyncio.TimeoutError) as err:
            self.sys_supervisor.connectivity = False
            raise UpdaterError(
                f"Can't fetch versions from {url}: {err}", _LOGGER.warning
            ) from err

        # Validate
        try:
            await self.sys_verify_content(checksum=calc_checksum(data))
        except CodeNotaryUntrusted as err:
            _LOGGER.critical(
                "Content-Trust is broaken for the version file fetch! - %s", err
            )
        except CodeNotaryError as err:
            _LOGGER.error("CodeNotary error while processing version checks: %s", err)

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

        try:
            # Update supervisor version
            self._data[ATTR_SUPERVISOR] = AwesomeVersion(data["supervisor"])

            # Update Home Assistant core version
            self._data[ATTR_HOMEASSISTANT] = AwesomeVersion(
                data["homeassistant"][machine]
            )

            # Update HassOS version
            if self.sys_hassos.board:
                self._data[ATTR_HASSOS] = AwesomeVersion(
                    data["hassos"][self.sys_hassos.board]
                )
                self._data[ATTR_OTA] = data["ota"]

            # Update Home Assistant plugins
            self._data[ATTR_CLI] = AwesomeVersion(data["cli"])
            self._data[ATTR_DNS] = AwesomeVersion(data["dns"])
            self._data[ATTR_AUDIO] = AwesomeVersion(data["audio"])
            self._data[ATTR_OBSERVER] = AwesomeVersion(data["observer"])
            self._data[ATTR_MULTICAST] = AwesomeVersion(data["multicast"])

            # Update images for that versions
            self._data[ATTR_IMAGE][ATTR_HOMEASSISTANT] = data["image"]["core"]
            self._data[ATTR_IMAGE][ATTR_SUPERVISOR] = data["image"]["supervisor"]
            self._data[ATTR_IMAGE][ATTR_AUDIO] = data["image"]["audio"]
            self._data[ATTR_IMAGE][ATTR_CLI] = data["image"]["cli"]
            self._data[ATTR_IMAGE][ATTR_DNS] = data["image"]["dns"]
            self._data[ATTR_IMAGE][ATTR_OBSERVER] = data["image"]["observer"]
            self._data[ATTR_IMAGE][ATTR_MULTICAST] = data["image"]["multicast"]

        except KeyError as err:
            raise UpdaterError(
                f"Can't process version data: {err}", _LOGGER.warning
            ) from err

        else:
            self.save_data()
