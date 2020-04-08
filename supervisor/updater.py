"""Fetch last versions from webserver."""
import asyncio
from contextlib import suppress
from datetime import timedelta
import json
import logging
from typing import Optional

import aiohttp

from .const import (
    ATTR_AUDIO,
    ATTR_CHANNEL,
    ATTR_CLI,
    ATTR_DNS,
    ATTR_HASSOS,
    ATTR_HOMEASSISTANT,
    ATTR_IMAGE,
    ATTR_MULTICAST,
    ATTR_SUPERVISOR,
    FILE_HASSIO_UPDATER,
    URL_HASSIO_VERSION,
    UpdateChannels,
)
from .coresys import CoreSysAttributes
from .exceptions import HassioUpdaterError
from .utils import AsyncThrottle
from .utils.json import JsonConfig
from .validate import SCHEMA_UPDATER_CONFIG

_LOGGER: logging.Logger = logging.getLogger(__name__)


class Updater(JsonConfig, CoreSysAttributes):
    """Fetch last versions from version.json."""

    def __init__(self, coresys):
        """Initialize updater."""
        super().__init__(FILE_HASSIO_UPDATER, SCHEMA_UPDATER_CONFIG)
        self.coresys = coresys

    async def load(self) -> None:
        """Update internal data."""
        with suppress(HassioUpdaterError):
            await self.fetch_data()

    async def reload(self) -> None:
        """Update internal data."""
        with suppress(HassioUpdaterError):
            await self.fetch_data()

    @property
    def version_homeassistant(self) -> Optional[str]:
        """Return latest version of Home Assistant."""
        return self._data.get(ATTR_HOMEASSISTANT)

    @property
    def version_supervisor(self) -> Optional[str]:
        """Return latest version of Supervisor."""
        return self._data.get(ATTR_SUPERVISOR)

    @property
    def version_hassos(self) -> Optional[str]:
        """Return latest version of HassOS."""
        return self._data.get(ATTR_HASSOS)

    @property
    def version_cli(self) -> Optional[str]:
        """Return latest version of CLI."""
        return self._data.get(ATTR_CLI)

    @property
    def version_dns(self) -> Optional[str]:
        """Return latest version of DNS."""
        return self._data.get(ATTR_DNS)

    @property
    def version_audio(self) -> Optional[str]:
        """Return latest version of Audio."""
        return self._data.get(ATTR_AUDIO)

    @property
    def version_multicast(self) -> Optional[str]:
        """Return latest version of Multicast."""
        return self._data.get(ATTR_MULTICAST)

    @property
    def image_homeassistant(self) -> Optional[str]:
        """Return latest version of Home Assistant."""
        return (
            self._data[ATTR_IMAGE]
            .get(ATTR_HOMEASSISTANT, "")
            .format(machine=self.sys_machine)
        )

    @property
    def image_supervisor(self) -> Optional[str]:
        """Return latest version of Supervisor."""
        return (
            self._data[ATTR_IMAGE]
            .get(ATTR_SUPERVISOR, "")
            .format(arch=self.sys_arch.supervisor)
        )

    @property
    def image_cli(self) -> Optional[str]:
        """Return latest version of CLI."""
        return (
            self._data[ATTR_IMAGE]
            .get(ATTR_CLI, "")
            .format(arch=self.sys_arch.supervisor)
        )

    @property
    def image_dns(self) -> Optional[str]:
        """Return latest version of DNS."""
        return (
            self._data[ATTR_IMAGE]
            .get(ATTR_DNS, "")
            .format(arch=self.sys_arch.supervisor)
        )

    @property
    def image_audio(self) -> Optional[str]:
        """Return latest version of Audio."""
        return (
            self._data[ATTR_IMAGE]
            .get(ATTR_AUDIO, "")
            .format(arch=self.sys_arch.supervisor)
        )

    @property
    def image_multicast(self) -> Optional[str]:
        """Return latest version of Multicast."""
        return (
            self._data[ATTR_IMAGE]
            .get(ATTR_MULTICAST, "")
            .format(arch=self.sys_arch.supervisor)
        )

    @property
    def channel(self) -> UpdateChannels:
        """Return upstream channel of Supervisor instance."""
        return self._data[ATTR_CHANNEL]

    @channel.setter
    def channel(self, value: UpdateChannels):
        """Set upstream mode."""
        self._data[ATTR_CHANNEL] = value

    @AsyncThrottle(timedelta(seconds=30))
    async def fetch_data(self):
        """Fetch current versions from Github.

        Is a coroutine.
        """
        url = URL_HASSIO_VERSION.format(channel=self.channel)
        machine = self.sys_machine or "default"

        try:
            _LOGGER.info("Fetch update data from %s", url)
            async with self.sys_websession.get(url, timeout=10) as request:
                data = await request.json(content_type=None)

        except (aiohttp.ClientError, asyncio.TimeoutError) as err:
            _LOGGER.warning("Can't fetch versions from %s: %s", url, err)
            raise HassioUpdaterError() from None

        except json.JSONDecodeError as err:
            _LOGGER.warning("Can't parse versions from %s: %s", url, err)
            raise HassioUpdaterError() from None

        # data valid?
        if not data or data.get(ATTR_CHANNEL) != self.channel:
            _LOGGER.warning("Invalid data from %s", url)
            raise HassioUpdaterError() from None

        try:
            # Update supervisor version
            self._data[ATTR_SUPERVISOR] = data["supervisor"]

            # Update Home Assistant core version
            self._data[ATTR_HOMEASSISTANT] = data["homeassistant"][machine]

            # Update HassOS version
            if self.sys_hassos.board:
                self._data[ATTR_HASSOS] = data["hassos"][self.sys_hassos.board]

            # Update Home Assistant plugins
            self._data[ATTR_CLI] = data["cli"]
            self._data[ATTR_DNS] = data["dns"]
            self._data[ATTR_AUDIO] = data["audio"]
            self._data[ATTR_MULTICAST] = data["multicast"]

            # Update images for that versions
            self._data[ATTR_IMAGE][ATTR_HOMEASSISTANT] = data["image"]["core"]
            self._data[ATTR_IMAGE][ATTR_SUPERVISOR] = data["image"]["supervisor"]
            self._data[ATTR_IMAGE][ATTR_AUDIO] = data["image"]["audio"]
            self._data[ATTR_IMAGE][ATTR_CLI] = data["image"]["cli"]
            self._data[ATTR_IMAGE][ATTR_DNS] = data["image"]["dns"]
            self._data[ATTR_IMAGE][ATTR_MULTICAST] = data["image"]["multicast"]

        except KeyError as err:
            _LOGGER.warning("Can't process version data: %s", err)
            raise HassioUpdaterError() from None

        else:
            self.save_data()
