"""Fetch last versions from webserver."""
import asyncio
from datetime import timedelta
import json
import logging

import aiohttp
import async_timeout

from .const import (
    URL_HASSIO_VERSION, FILE_HASSIO_UPDATER, ATTR_HOMEASSISTANT, ATTR_HASSIO,
    ATTR_MODE, MODE_STABLE, MODE_BETA, MODE_DEV)
from .coresys import CoreSysAttributes
from .utils import AsyncThrottle
from .utils.json import JsonConfig
from .validate import SCHEMA_UPDATER_CONFIG

_LOGGER = logging.getLogger(__name__)

MODE_TO_BRANCH = {
    MODE_STABLE: 'master',
    MODE_BETA: 'rc',
    MODE_DEV: 'dev',
}


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
    def mode(self):
        """Return upstream mode of hassio instance."""
        return self._data[ATTR_MODE]

    @mode.setter
    def mode(self, value):
        """Set upstream mode."""
        self._data[ATTR_MODE] = value

    @AsyncThrottle(timedelta(seconds=60))
    async def reload(self):
        """Fetch current versions from github.

        Is a coroutine.
        """
        url = URL_HASSIO_VERSION.format(MODE_TO_BRANCH[self.mode])
        try:
            _LOGGER.info("Fetch update data from %s", url)
            with async_timeout.timeout(10, loop=self._loop):
                async with self._websession.get(url) as request:
                    data = await request.json(content_type=None)

        except (aiohttp.ClientError, asyncio.TimeoutError, KeyError) as err:
            _LOGGER.warning("Can't fetch versions from %s: %s", url, err)
            return

        except json.JSONDecodeError as err:
            _LOGGER.warning("Can't parse versions from %s: %s", url, err)
            return

        # data valid?
        if not data:
            _LOGGER.warning("Invalid data from %s", url)
            return

        # update versions
        self._data[ATTR_HOMEASSISTANT] = data.get('homeassistant')
        self._data[ATTR_HASSIO] = data.get('hassio')
        self.save_data()
