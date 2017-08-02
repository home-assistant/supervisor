"""HomeAssistant control object."""
import asyncio
import logging
import os

from .const import (
    FILE_HASSIO_HOMEASSISTANT, ATTR_DEVICES, ATTR_IMAGE, ATTR_LAST_VERSION,
    ATTR_VERSION)
from .dock.homeassistant import DockerHomeAssistant
from .tools import JsonConfig
from .validate import SCHEMA_HASS_CONFIG

_LOGGER = logging.getLogger(__name__)


class HomeAssistant(JsonConfig):
    """Hass core object for handle it."""

    def __init__(self, config, loop, dock, websession):
        """Initialize hass object."""
        super().__init__(FILE_HASSIO_HOMEASSISTANT, SCHEMA_HASS_CONFIG)
        self.config = config
        self.loop = loop
        self.websession = websession
        self.docker = DockerHomeAssistant(config, loop, dock, self)

    async def prepare(self):
        """Prepare HomeAssistant object."""
        if not await self.docker.exists():
            _LOGGER.info("No HomeAssistant docker %s found.", self.image)
            if self.is_custom_image:
                await self.install()
            else:
                await self.install_landingpage()
        else:
            await self.docker.attach()

    @property
    def version(self):
        """Return version of running homeassistant."""
        return self.docker.version

    @property
    def last_version(self):
        """Return last available version of homeassistant."""
        if self.is_custom_image:
            return self._data.get(ATTR_LAST_VERSION)
        return self.config.last_homeassistant

    @property
    def image(self):
        """Return image name of hass containter."""
        if ATTR_IMAGE in self._data:
            return self._data[ATTR_IMAGE]
        return os.environ['HOMEASSISTANT_REPOSITORY']

    @property
    def is_custom_image(self):
        """Return True if a custom image is used."""
        return ATTR_IMAGE in self._data

    @property
    def devices(self):
        """Return extend device mapping."""
        return self._data[ATTR_DEVICES]

    @devices.setter
    def devices(self, value):
        """Set extend device mapping."""
        self._data[ATTR_DEVICES] = value
        self.save()

    def set_custom(self, image, version):
        """Set a custom image for homeassistant."""
        # reset
        if image is None and version is None:
            self._data.pop(ATTR_IMAGE, None)
            self._data.pop(ATTR_VERSION, None)

            self.docker.image = self.image
        else:
            if image:
                self._data[ATTR_IMAGE] = image
                self.docker.image = image
            if version:
                self._data[ATTR_VERSION] = version
        self.save()

    async def install_landingpage(self):
        """Install a landingpage."""
        _LOGGER.info("Setup HomeAssistant landingpage")
        while True:
            if await self.docker.install('landingpage'):
                break
            _LOGGER.warning("Fails install landingpage, retry after 60sec")
            await asyncio.sleep(60, loop=self.loop)

    async def install(self):
        """Install a landingpage."""
        _LOGGER.info("Setup HomeAssistant")
        while True:
            # read homeassistant tag and install it
            if not self.last_version:
                await self.config.fetch_update_infos(self.websession)

            tag = self.last_version
            if tag and await self.docker.install(tag):
                break
            _LOGGER.warning("Error on install HomeAssistant. Retry in 60sec")
            await asyncio.sleep(60, loop=self.loop)

        # store version
        _LOGGER.info("HomeAssistant docker now installed")
        await self.docker.cleanup()

    async def update(self, version=None):
        """Update HomeAssistant version."""
        version = version or self.last_version

        if version == self.docker.version:
            _LOGGER.warning("Version %s is already installed", version)
            return False

        return self.docker.update(version)

    def run(self):
        """Run HomeAssistant docker.

        Return a coroutine.
        """
        return self.docker.run()

    def restart(self):
        """Restart HomeAssistant docker.

        Return a coroutine.
        """
        return self.docker.restart()

    def logs(self):
        """Get HomeAssistant docker logs.

        Return a coroutine.
        """
        return self.docker.logs()

    def is_running(self):
        """Return True if docker container is running.

        Return a coroutine.
        """
        return self.docker.is_running()

    @property
    def in_progress(self):
        """Return True if a task is in progress."""
        return self.docker.in_progress
