"""Fetch last versions from webserver."""
import asyncio
from contextlib import suppress
from datetime import timedelta
import json
import logging

import aiohttp

from .const import (
    URL_HASSIO_VERSION, FILE_HASSIO_UPDATER, ATTR_HOMEASSISTANT, ATTR_HASSIO,
    ATTR_CHANNEL, ATTR_HASSOS)
from .coresys import CoreSysAttributes
from .utils import AsyncThrottle
from .utils.json import JsonConfig
from .validate import SCHEMA_UPDATER_CONFIG

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

    @AsyncThrottle(timedelta(seconds=60))
    async def reload(self):
        """Fetch current versions from github.

        Is a coroutine.
        """
        url = URL_HASSIO_VERSION.format(channel=self.channel)
        machine = self.sys_machine or 'default'
        board = self.sys_hassos.board

        try:
            _LOGGER.info("Fetch update data from %s", url)
            async with self.sys_websession.get(url, timeout=10) as request:
                data = await request.json(content_type=None)

        except (aiohttp.ClientError, asyncio.TimeoutError, KeyError) as err:
            _LOGGER.warning("Can't fetch versions from %s: %s", url, err)
            return

        except json.JSONDecodeError as err:
            _LOGGER.warning("Can't parse versions from %s: %s", url, err)
            return

        # data valid?
        if not data or data.get(ATTR_CHANNEL) != self.channel:
            _LOGGER.warning("Invalid data from %s", url)
            return

        try:
            # update supervisor version
            self._data[ATTR_HASSIO] = data['supervisor']

            # update Home Assistant version
            self._data[ATTR_HOMEASSISTANT] = data['homeassistant'][machine]

            # update hassos version
            if self.sys_hassos.availabe and board:
                self._data[ATTR_HASSOS] = data['hassos'][board]

        except KeyError as err:
            _LOGGER.warning("Can't process version data: %s", err)

        else:
            self.save_data()
