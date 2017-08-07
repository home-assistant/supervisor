"""Fetch last versions from webserver."""
import asyncio
from datetime import timedelta
import json
import logging

import aiohttp
import async_timeout

from .const import (
    URL_HASSIO_VERSION, FILE_HASSIO_UPDATER, ATTR_HOMEASSISTANT, ATTR_HASSIO,
    ATTR_BETA_CHANNEL)
from .tools import AsyncThrottle, JsonConfig
from .validate import SCHEMA_UPDATER_CONFIG

_LOGGER = logging.getLogger(__name__)


class Updater(JsonConfig):
    """Fetch last versions from version.json."""

    def __ini__(self, config, loop, websession):
        """Initialize updater."""
        super().__init__(FILE_HASSIO_UPDATER, SCHEMA_UPDATER_CONFIG)
        self.config = config
        self.loop = loop
        self.websession = websession

    @property
    def version_homeassistant(self):
        """Return last version of homeassistant."""
        return self._data.get(ATTR_HOMEASSISTANT)

    @property
    def version_hassio(self):
        """Return last version of hassio."""
        return self._data.get(ATTR_HASSIO)

    @property
    def upsream(self):
        """Return Upstream branch for version."""
        if self.beta_channel:
            return 'dev'
        return 'master'

    @property
    def beta_channel(self):
        """Return True if we run in beta upstream."""
        return self._data[ATTR_BETA_CHANNEL]

    @beta_channel.setter
    def beta_channel(self, value):
        """Set beta upstream mode."""
        self._data[ATTR_BETA_CHANNEL] = bool(value)
        self.save()

    @AsyncThrottle(timedelta(min=1))
    async def fetch_data(self):
        """Fetch current versions from github.

        Is a coroutine.
        """
        url = URL_HASSIO_VERSION.format(self.upstream)
        try:
            with async_timeout.timeout(10, loop=self.loop):
                async with websession.get(url) as request:
                    data = await request.json(content_type=None)

        except (aiohttp.ClientError, asyncio.TimeoutError, KeyError) as err:
            _LOGGER.warning("Can't fetch versions from %s -> %s", url, err)
            return

        except json.JSONDecodeError as err:
            _LOGGER.warning("Can't parse versions from %s -> %s", url, err)
            return

        # data valid?
        if not data:
            _LOGGER.warning("Invalid data from %s", url)
            return

        # update versions
        self._data[ATTR_HOMEASSISTANT] = data.get('homeassistant')
        self._data[ATTR_HASSIO] = data.get('hassio')
        self.save()
