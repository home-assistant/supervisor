"""Fetch last versions from webserver."""
import asyncio
from contextlib import suppress
from datetime import timedelta
import json
import logging
from typing import Optional

import aiohttp

from .const import (
    ATTR_CHANNEL,
    ATTR_DNS,
    ATTR_HASSIO,
    ATTR_HASSOS,
    ATTR_HASSOS_CLI,
    ATTR_HOMEASSISTANT,
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
    def version_hassio(self) -> Optional[str]:
        """Return latest version of Supervisor."""
        return self._data.get(ATTR_HASSIO)

    @property
    def version_hassos(self) -> Optional[str]:
        """Return latest version of HassOS."""
        return self._data.get(ATTR_HASSOS)

    @property
    def version_hassos_cli(self) -> Optional[str]:
        """Return latest version of HassOS cli."""
        return self._data.get(ATTR_HASSOS_CLI)

    @property
    def version_dns(self) -> Optional[str]:
        """Return latest version of Supervisor DNS."""
        return self._data.get(ATTR_DNS)

    @property
    def channel(self) -> UpdateChannels:
        """Return upstream channel of Supervisor instance."""
        return self._data[ATTR_CHANNEL]

    @channel.setter
    def channel(self, value: UpdateChannels):
        """Set upstream mode."""
        self._data[ATTR_CHANNEL] = value

    @AsyncThrottle(timedelta(seconds=60))
    async def fetch_data(self):
        """Fetch current versions from Github.

        Is a coroutine.
        """
        url = URL_HASSIO_VERSION.format(channel=self.channel)
        machine = self.sys_machine or "default"
        board = self.sys_hassos.board

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
            # update supervisor version
            self._data[ATTR_HASSIO] = data["supervisor"]
            self._data[ATTR_DNS] = data["dns"]

            # update Home Assistant version
            self._data[ATTR_HOMEASSISTANT] = data["homeassistant"][machine]

            # update hassos version
            if self.sys_hassos.available and board:
                self._data[ATTR_HASSOS] = data["hassos"][board]
                self._data[ATTR_HASSOS_CLI] = data["hassos-cli"]

        except KeyError as err:
            _LOGGER.warning("Can't process version data: %s", err)
            raise HassioUpdaterError() from None

        else:
            self.save_data()
