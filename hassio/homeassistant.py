"""HomeAssistant control object."""
import asyncio
import logging
import os
import re

import aiohttp
from aiohttp.hdrs import CONTENT_TYPE
import async_timeout

from .const import (
    FILE_HASSIO_HOMEASSISTANT, ATTR_DEVICES, ATTR_IMAGE, ATTR_LAST_VERSION,
    ATTR_VERSION, ATTR_BOOT, ATTR_PASSWORD, ATTR_PORT, ATTR_SSL, ATTR_WATCHDOG,
    HEADER_HA_ACCESS, CONTENT_TYPE_JSON)
from .coresys import CoreSysAttributes
from .docker.homeassistant import DockerHomeAssistant
from .utils import convert_to_ascii
from .utils.json import JsonConfig
from .validate import SCHEMA_HASS_CONFIG

_LOGGER = logging.getLogger(__name__)

RE_YAML_ERROR = re.compile(r"homeassistant\.util\.yaml")


class HomeAssistant(JsonConfig, CoreSysAttributes):
    """Hass core object for handle it."""

    def __init__(self, coresys):
        """Initialize hass object."""
        super().__init__(FILE_HASSIO_HOMEASSISTANT, SCHEMA_HASS_CONFIG)
        self.coresys = coresys
        self.instance = DockerHomeAssistant(coresys)

    async def prepare(self):
        """Prepare HomeAssistant object."""
        if not await self.instance.exists():
            _LOGGER.info("No HomeAssistant docker %s found.", self.image)
            if self.is_custom_image:
                await self.install()
            else:
                await self.install_landingpage()
        else:
            await self.instance.attach()

    @property
    def api_ip(self):
        """Return IP of HomeAssistant instance."""
        return self._docker.network.gateway

    @property
    def api_port(self):
        """Return network port to home-assistant instance."""
        return self._data[ATTR_PORT]

    @api_port.setter
    def api_port(self, value):
        """Set network port for home-assistant instance."""
        self._data[ATTR_PORT] = value
        self.save()

    @property
    def api_password(self):
        """Return password for home-assistant instance."""
        return self._data.get(ATTR_PASSWORD)

    @api_password.setter
    def api_password(self, value):
        """Set password for home-assistant instance."""
        self._data[ATTR_PASSWORD] = value
        self.save()

    @property
    def api_ssl(self):
        """Return if we need ssl to home-assistant instance."""
        return self._data[ATTR_SSL]

    @api_ssl.setter
    def api_ssl(self, value):
        """Set SSL for home-assistant instance."""
        self._data[ATTR_SSL] = value
        self.save()

    @property
    def api_url(self):
        """Return API url to Home-Assistant."""
        return "{}://{}:{}".format(
            'https' if self.api_ssl else 'http', self.api_ip, self.api_port
        )

    @property
    def watchdog(self):
        """Return True if the watchdog should protect Home-Assistant."""
        return self._data[ATTR_WATCHDOG]

    @watchdog.setter
    def watchdog(self, value):
        """Return True if the watchdog should protect Home-Assistant."""
        self._data[ATTR_WATCHDOG] = value
        self.save()

    @property
    def version(self):
        """Return version of running homeassistant."""
        return self.instance.version

    @property
    def last_version(self):
        """Return last available version of homeassistant."""
        if self.is_custom_image:
            return self._data.get(ATTR_LAST_VERSION)
        return self._updater.version_homeassistant

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

    @boot.setter
    def boot(self, value):
        """Set home-assistant boot options."""
        self._data[ATTR_BOOT] = value
        self.save()

    def set_custom(self, image, version):
        """Set a custom image for homeassistant."""
        # reset
        if image is None and version is None:
            self._data.pop(ATTR_IMAGE, None)
            self._data.pop(ATTR_VERSION, None)

            self.instance.image = self.image
        else:
            if image:
                self._data[ATTR_IMAGE] = image
                self.instance.image = image
            if version:
                self._data[ATTR_VERSION] = version
        self.save()

    async def install_landingpage(self):
        """Install a landingpage."""
        _LOGGER.info("Setup HomeAssistant landingpage")
        while True:
            if await self.instance.install('landingpage'):
                break
            _LOGGER.warning("Fails install landingpage, retry after 60sec")
            await asyncio.sleep(60, loop=self._loop)

        # run landingpage after installation
        await self.instance.run()

    async def install(self):
        """Install a landingpage."""
        _LOGGER.info("Setup HomeAssistant")
        while True:
            # read homeassistant tag and install it
            if not self.last_version:
                await self._updater.fetch_data()

            tag = self.last_version
            if tag and await self.instance.install(tag):
                break
            _LOGGER.warning("Error on install HomeAssistant. Retry in 60sec")
            await asyncio.sleep(60, loop=self._loop)

        # finishing
        _LOGGER.info("HomeAssistant docker now installed")
        if self.boot:
            await self.instance.run()
        await self.instance.cleanup()

    async def update(self, version=None):
        """Update HomeAssistant version."""
        version = version or self.last_version
        running = await self.instance.is_running()

        if version == self.instance.version:
            _LOGGER.warning("Version %s is already installed", version)
            return False

        try:
            return await self.instance.update(version)
        finally:
            if running:
                await self.instance.run()

    def run(self):
        """Run HomeAssistant docker.

        Return a coroutine.
        """
        return self.instance.run()

    def stop(self):
        """Stop HomeAssistant docker.

        Return a coroutine.
        """
        return self.instance.stop()

    def restart(self):
        """Restart HomeAssistant docker.

        Return a coroutine.
        """
        return self.instance.restart()

    def logs(self):
        """Get HomeAssistant docker logs.

        Return a coroutine.
        """
        return self.instance.logs()

    def is_running(self):
        """Return True if docker container is running.

        Return a coroutine.
        """
        return self.instance.is_running()

    def is_initialize(self):
        """Return True if a docker container is exists.

        Return a coroutine.
        """
        return self.instance.is_initialize()

    @property
    def in_progress(self):
        """Return True if a task is in progress."""
        return self.instance.in_progress

    async def check_config(self):
        """Run homeassistant config check."""
        exit_code, log = await self.instance.execute_command(
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

    async def check_api_state(self):
        """Check if Home-Assistant up and running."""
        url = f"{self.api_url}/api/"
        header = {CONTENT_TYPE: CONTENT_TYPE_JSON}

        if self.api_password:
            header.update({HEADER_HA_ACCESS: self.api_password})

        try:
            async with async_timeout.timeout(30, loop=self._loop):
                async with self._websession_ssl.get(
                        url, headers=header) as request:
                    status = request.status

        except (asyncio.TimeoutError, aiohttp.ClientError):
            return False

        if status not in (200, 201):
            _LOGGER.warning("Home-Assistant API config missmatch")
        return True
