"""HomeAssistant control object."""
import asyncio
import logging
import os
import re

from .const import (
    FILE_HASSIO_HOMEASSISTANT, ATTR_DEVICES, ATTR_IMAGE, ATTR_LAST_VERSION,
    ATTR_VERSION, ATTR_BOOT)
from .dock.homeassistant import DockerHomeAssistant
from .tools import JsonConfig, convert_to_ascii
from .validate import SCHEMA_HASS_CONFIG

_LOGGER = logging.getLogger(__name__)

RE_YAML_ERROR = re.compile(r"homeassistant\.util\.yaml")


class HomeAssistant(JsonConfig):
    """Hass core object for handle it."""

    def __init__(self, config, loop, docker, updater):
        """Initialize hass object."""
        super().__init__(FILE_HASSIO_HOMEASSISTANT, SCHEMA_HASS_CONFIG)
        self.config = config
        self.loop = loop
        self.updater = updater
        self.docker = DockerHomeAssistant(config, loop, docker, self)

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
        return self.updater.version_homeassistant

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

    @property
    def boot(self):
        """Return True if home-assistant boot is enabled."""
        return self._data[ATTR_BOOT]

    @enable.setter
    def boot(self):
        """Set home-assistant boot options."""
        return self._data[ATTR_BOOT]

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
                await self.updater.fetch_data()

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

        try:
            return await self.docker.update(version)
        finally:
            await self.docker.run()

    def run(self):
        """Run HomeAssistant docker.

        Return a coroutine.
        """
        return self.docker.run()

    def stop(self):
        """Stop HomeAssistant docker.

        Return a coroutine.
        """
        return self.docker.stop()

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

    def is_initialize(self):
        """Return True if a docker container is exists.

        Return a coroutine.
        """
        return self.docker.is_initialize()

    @property
    def in_progress(self):
        """Return True if a task is in progress."""
        return self.docker.in_progress

    async def check_config(self):
        """Run homeassistant config check."""
        exit_code, log = await self.docker.execute_command(
            "python3 -m homeassistant -c /config --script check_config"
        )

        # if not valid
        if exit_code is None:
            return (False, "")

        # parse output
        log = convert_to_ascii(log)
        if exit_code != 0 or RE_YAML_ERROR.search(log):
            return (False, log)
        return (True, log)
