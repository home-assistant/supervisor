"""Fetch last versions from webserver."""
import asyncio
from contextlib import suppress
from datetime import timedelta
import logging

import aiohttp

from .const import (
    URL_HASSIO_VERSION, URL_HASSOS_VERSION, FILE_HASSIO_UPDATER,
    ATTR_HOMEASSISTANT, ATTR_HASSIO, ATTR_CHANNEL, ATTR_HASSOS)
from .coresys import CoreSysAttributes
from .utils import AsyncThrottle
from .utils.json import JsonConfig
from .validate import SCHEMA_UPDATER_CONFIG
from .exceptions import UpdaterError

_LOGGER = logging.getLogger(__name__)


class Updater(JsonConfig, CoreSysAttributes):
    """Fetch last versions from version.json."""

    def __init__(self, coresys):
        """Initialize updater."""
        super().__init__(FILE_HASSIO_UPDATER, SCHEMA_UPDATER_CONFIG)
        self.coresys = coresys

    def load(self):
        """Update internal data.

        Return a coroutine.
        """
        return self.reload()

    @property
    def version_homeassistant(self):
        """Return last version of homeassistant."""
        return self._data.get(ATTR_HOMEASSISTANT)

    @property
    def version_hassio(self):
        """Return last version of hassio."""
        return self._data.get(ATTR_HASSIO)

    @property
    def version_hassos(self):
        """Return last version of hassos."""
        return self._data.get(ATTR_HASSOS)

    @property
    def channel(self):
        """Return upstream channel of hassio instance."""
        return self._data[ATTR_CHANNEL]

    @channel.setter
    def channel(self, value):
        """Set upstream mode."""
        self._data[ATTR_CHANNEL] = value

    async def _fetch_data(self, url_raw):
        """Fetch current versions from github.

        Is a coroutine.
        """
        url = url_raw.format(channel=self.channel)
        try:
            _LOGGER.info("Fetch update data from %s", url)
            async with self.sys_websession.get(url, timeout=10) as request:
                data = await request.json(content_type=None)

        except (aiohttp.ClientError, KeyError) as err:
            _LOGGER.warning("Can't fetch versions from %s: %s", url, err)
            raise UpdaterError() from None

        except ValueError as err:
            _LOGGER.warning("Can't parse versions from %s: %s", url, err)
            raise UpdaterError() from None

        # data valid?
        if not data or data.get(ATTR_CHANNEL) != self.channel:
            _LOGGER.warning("Invalid data from %s", url)
            raise UpdaterError() from None

        return data

    async def _hassio_data(self):
        """Read Hass.io data."""
        data = await self._fetch_data(URL_HASSIO_VERSION)
        machine = self.sys_machine or 'default'

        try:
            # update supervisor versions
            self._data[ATTR_HASSIO] = data['supervisor']

            # update Home Assistant version
            self._data[ATTR_HOMEASSISTANT] = data['homeassistant'][machine]
        except KeyError:
            _LOGGER.error("Wrong input for Hass.io data")

    async def _hassos_data(self):
        """Read HassOS data."""
        data = await self._fetch_data(URL_HASSOS_VERSION)

        try:
            # update HassOS version
            self._data[ATTR_HASSOS] = data['version'][self.sys_hassos.board]
        except KeyError:
            _LOGGER.error("Wrong input for HassOS data")

    @AsyncThrottle(timedelta(seconds=60))
    async def reload(self):
        """Fetch current versions from github.

        Is a coroutine.
        """
        with suppress(UpdaterError):
            await self._hassio_data()

        # If HassOS, read also this data
        if not self.sys_hassos.available:
            return

        with suppress(UpdaterError):
            await self._hassos_data()
