"""HomeAssistant control object."""
import asyncio
import logging
import os
import re
import socket
import time

import aiohttp
from aiohttp.hdrs import CONTENT_TYPE
import attr

from .const import (
    FILE_HASSIO_HOMEASSISTANT, ATTR_IMAGE, ATTR_LAST_VERSION, ATTR_UUID,
    ATTR_BOOT, ATTR_PASSWORD, ATTR_PORT, ATTR_SSL, ATTR_WATCHDOG,
    ATTR_WAIT_BOOT, HEADER_HA_ACCESS, CONTENT_TYPE_JSON)
from .coresys import CoreSysAttributes
from .docker.homeassistant import DockerHomeAssistant
from .utils import convert_to_ascii, process_lock
from .utils.json import JsonConfig
from .validate import SCHEMA_HASS_CONFIG

_LOGGER = logging.getLogger(__name__)

RE_YAML_ERROR = re.compile(r"homeassistant\.util\.yaml")

# pylint: disable=invalid-name
ConfigResult = attr.make_class('ConfigResult', ['valid', 'log'])


class HomeAssistant(JsonConfig, CoreSysAttributes):
    """Hass core object for handle it."""

    def __init__(self, coresys):
        """Initialize hass object."""
        super().__init__(FILE_HASSIO_HOMEASSISTANT, SCHEMA_HASS_CONFIG)
        self.coresys = coresys
        self.instance = DockerHomeAssistant(coresys)
        self.lock = asyncio.Lock(loop=coresys.loop)
        self._error_state = False

    async def load(self):
        """Prepare HomeAssistant object."""
        if await self.instance.attach():
            return

        _LOGGER.info("No HomeAssistant docker %s found.", self.image)
        await self.install_landingpage()

    @property
    def machine(self):
        """Return System Machines."""
        return self.instance.machine

    @property
    def error_state(self):
        """Return True if system is in error."""
        return self._error_state

    @property
    def api_ip(self):
        """Return IP of HomeAssistant instance."""
        return self.sys_docker.network.gateway

    @property
    def api_port(self):
        """Return network port to home-assistant instance."""
        return self._data[ATTR_PORT]

    @api_port.setter
    def api_port(self, value):
        """Set network port for home-assistant instance."""
        self._data[ATTR_PORT] = value

    @property
    def api_password(self):
        """Return password for home-assistant instance."""
        return self._data.get(ATTR_PASSWORD)

    @api_password.setter
    def api_password(self, value):
        """Set password for home-assistant instance."""
        self._data[ATTR_PASSWORD] = value

    @property
    def api_ssl(self):
        """Return if we need ssl to home-assistant instance."""
        return self._data[ATTR_SSL]

    @api_ssl.setter
    def api_ssl(self, value):
        """Set SSL for home-assistant instance."""
        self._data[ATTR_SSL] = value

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

    @property
    def wait_boot(self):
        """Return time to wait for Home-Assistant startup."""
        return self._data[ATTR_WAIT_BOOT]

    @wait_boot.setter
    def wait_boot(self, value):
        """Set time to wait for Home-Assistant startup."""
        self._data[ATTR_WAIT_BOOT] = value

    @property
    def version(self):
        """Return version of running homeassistant."""
        return self.instance.version

    @property
    def last_version(self):
        """Return last available version of homeassistant."""
        if self.is_custom_image:
            return self._data.get(ATTR_LAST_VERSION)
        return self.sys_updater.version_homeassistant

    @last_version.setter
    def last_version(self, value):
        """Set last available version of homeassistant."""
        if value:
            self._data[ATTR_LAST_VERSION] = value
        else:
            self._data.pop(ATTR_LAST_VERSION, None)

    @property
    def image(self):
        """Return image name of hass containter."""
        if self._data.get(ATTR_IMAGE):
            return self._data[ATTR_IMAGE]
        return os.environ['HOMEASSISTANT_REPOSITORY']

    @image.setter
    def image(self, value):
        """Set image name of hass containter."""
        if value:
            self._data[ATTR_IMAGE] = value
        else:
            self._data.pop(ATTR_IMAGE, None)

    @property
    def is_custom_image(self):
        """Return True if a custom image is used."""
        return all(attr in self._data for attr in
                   (ATTR_IMAGE, ATTR_LAST_VERSION))

    @property
    def boot(self):
        """Return True if home-assistant boot is enabled."""
        return self._data[ATTR_BOOT]

    @boot.setter
    def boot(self, value):
        """Set home-assistant boot options."""
        self._data[ATTR_BOOT] = value

    @property
    def uuid(self):
        """Return a UUID of this HomeAssistant."""
        return self._data[ATTR_UUID]

    @process_lock
    async def install_landingpage(self):
        """Install a landingpage."""
        _LOGGER.info("Setup HomeAssistant landingpage")
        while True:
            if await self.instance.install('landingpage'):
                break
            _LOGGER.warning("Fails install landingpage, retry after 60sec")
            await asyncio.sleep(60)

        # Run landingpage after installation
        await self._start()

    @process_lock
    async def install(self):
        """Install a landingpage."""
        _LOGGER.info("Setup HomeAssistant")
        while True:
            # read homeassistant tag and install it
            if not self.last_version:
                await self.sys_updater.reload()

            tag = self.last_version
            if tag and await self.instance.install(tag):
                break
            _LOGGER.warning("Error on install HomeAssistant. Retry in 60sec")
            await asyncio.sleep(60)

        # finishing
        _LOGGER.info("HomeAssistant docker now installed")
        if self.boot:
            await self._start()
        await self.instance.cleanup()

    @process_lock
    async def update(self, version=None):
        """Update HomeAssistant version."""
        version = version or self.last_version
        rollback = self.version
        running = await self.instance.is_running()
        exists = await self.instance.exists()

        if exists and version == self.instance.version:
            _LOGGER.warning("Version %s is already installed", version)
            return False

        # process a update
        async def _update(to_version):
            """Run Home Assistant update."""
            try:
                return await self.instance.update(to_version)
            finally:
                if running:
                    await self._start()

        # Update Home Assistant
        ret = await _update(version)

        # Update going wrong, revert it
        if self.error_state and rollback:
            _LOGGER.fatal("Home Assistant update fails -> rollback!")
            ret = await _update(rollback)

        return ret

    async def _start(self):
        """Start HomeAssistant docker & wait."""
        if not await self.instance.run():
            return False
        return await self._block_till_run()

    @process_lock
    def start(self):
        """Run HomeAssistant docker.

        Return a coroutine.
        """
        return self._start()

    @process_lock
    def stop(self):
        """Stop HomeAssistant docker.

        Return a coroutine.
        """
        return self.instance.stop()

    @process_lock
    async def restart(self):
        """Restart HomeAssistant docker."""
        await self.instance.stop()
        return await self._start()

    def logs(self):
        """Get HomeAssistant docker logs.

        Return a coroutine.
        """
        return self.instance.logs()

    def stats(self):
        """Return stats of HomeAssistant.

        Return a coroutine.
        """
        return self.instance.stats()

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
        return self.instance.in_progress or self.lock.locked()

    async def check_config(self):
        """Run homeassistant config check."""
        result = await self.instance.execute_command(
            "python3 -m homeassistant -c /config --script check_config"
        )

        # if not valid
        if result.exit_code is None:
            return ConfigResult(False, "")

        # parse output
        log = convert_to_ascii(result.output)
        if result.exit_code != 0 or RE_YAML_ERROR.search(log):
            return ConfigResult(False, log)
        return ConfigResult(True, log)

    async def check_api_state(self):
        """Check if Home-Assistant up and running."""
        url = f"{self.api_url}/api/"
        header = {CONTENT_TYPE: CONTENT_TYPE_JSON}

        if self.api_password:
            header.update({HEADER_HA_ACCESS: self.api_password})

        try:
            # pylint: disable=bad-continuation
            async with self.sys_websession_ssl.get(
                    url, headers=header, timeout=30) as request:
                status = request.status

        except (asyncio.TimeoutError, aiohttp.ClientError):
            return False

        if status not in (200, 201):
            _LOGGER.warning("Home-Assistant API config missmatch")
        return True

    async def send_event(self, event_type, event_data=None):
        """Send event to Home-Assistant."""
        url = f"{self.api_url}/api/events/{event_type}"
        header = {CONTENT_TYPE: CONTENT_TYPE_JSON}

        if self.api_password:
            header.update({HEADER_HA_ACCESS: self.api_password})

        try:
            # pylint: disable=bad-continuation
            async with self.sys_websession_ssl.post(
                    url, headers=header, timeout=30,
                    json=event_data) as request:
                status = request.status

        except (asyncio.TimeoutError, aiohttp.ClientError) as err:
            _LOGGER.warning(
                "Home-Assistant event %s fails: %s", event_type, err)
            return False

        if status not in (200, 201):
            _LOGGER.warning("Home-Assistant event %s fails", event_type)
            return False
        return True

    async def _block_till_run(self):
        """Block until Home-Assistant is booting up or startup timeout."""
        start_time = time.monotonic()

        def check_port():
            """Check if port is mapped."""
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                result = sock.connect_ex((str(self.api_ip), self.api_port))
                sock.close()

                if result == 0:
                    return True
                return False
            except OSError:
                pass

        while time.monotonic() - start_time < self.wait_boot:
            if await self.sys_run_in_executor(check_port):
                _LOGGER.info("Detect a running Home-Assistant instance")
                self._error_state = False
                return True
            await asyncio.sleep(10)

        _LOGGER.warning("Don't wait anymore of Home-Assistant startup!")
        self._error_state = True
        return False
