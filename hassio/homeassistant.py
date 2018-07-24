"""HomeAssistant control object."""
import asyncio
from contextlib import asynccontextmanager, suppress
import logging
import os
import re
import socket
import time

import aiohttp
from aiohttp import hdrs
import attr

from .const import (
    FILE_HASSIO_HOMEASSISTANT, ATTR_IMAGE, ATTR_LAST_VERSION, ATTR_UUID,
    ATTR_BOOT, ATTR_PASSWORD, ATTR_PORT, ATTR_SSL, ATTR_WATCHDOG,
    ATTR_WAIT_BOOT, ATTR_REFRESH_TOKEN,
    HEADER_HA_ACCESS)
from .coresys import CoreSysAttributes
from .docker.homeassistant import DockerHomeAssistant
from .exceptions import (
    HomeAssistantUpdateError, HomeAssistantError, HomeAssistantAPIError,
    HomeAssistantAuthError)
from .utils import convert_to_ascii, process_lock
from .utils.json import JsonConfig
from .validate import SCHEMA_HASS_CONFIG

_LOGGER = logging.getLogger(__name__)

RE_YAML_ERROR = re.compile(r"homeassistant\.util\.yaml")

# pylint: disable=invalid-name
ConfigResult = attr.make_class('ConfigResult', ['valid', 'log'], frozen=True)


class HomeAssistant(JsonConfig, CoreSysAttributes):
    """Hass core object for handle it."""

    def __init__(self, coresys):
        """Initialize hass object."""
        super().__init__(FILE_HASSIO_HOMEASSISTANT, SCHEMA_HASS_CONFIG)
        self.coresys = coresys
        self.instance = DockerHomeAssistant(coresys)
        self.lock = asyncio.Lock(loop=coresys.loop)
        self._error_state = False
        # We don't persist access tokens. Instead we fetch new ones when needed
        self.access_token = None

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

    @property
    def refresh_token(self):
        """Return the refresh token to authenticate with HomeAssistant."""
        return self._data.get(ATTR_REFRESH_TOKEN)

    @refresh_token.setter
    def refresh_token(self, value):
        """Set Home Assistant refresh_token."""
        self._data[ATTR_REFRESH_TOKEN] = value

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
        _LOGGER.info("Start landingpage")
        try:
            await self._start()
        except HomeAssistantError:
            _LOGGER.warning("Can't start landingpage")

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
        try:
            if not self.boot:
                return
            _LOGGER.info("Start HomeAssistant")
            await self._start()
        except HomeAssistantError:
            _LOGGER.error("Can't start HomeAssistant!")
        finally:
            await self.instance.cleanup()

    @process_lock
    async def update(self, version=None):
        """Update HomeAssistant version."""
        version = version or self.last_version
        rollback = self.version if not self.error_state else None
        running = await self.instance.is_running()
        exists = await self.instance.exists()

        if exists and version == self.instance.version:
            _LOGGER.warning("Version %s is already installed", version)
            return HomeAssistantUpdateError()

        # process a update
        async def _update(to_version):
            """Run Home Assistant update."""
            try:
                _LOGGER.info("Update HomeAssistant to version %s", to_version)
                if not await self.instance.update(to_version):
                    raise HomeAssistantUpdateError()
            finally:
                if running:
                    await self._start()
                _LOGGER.info("Successfull run HomeAssistant %s", to_version)

        # Update Home Assistant
        with suppress(HomeAssistantError):
            await _update(version)
            return

        # Update going wrong, revert it
        if self.error_state and rollback:
            _LOGGER.fatal("HomeAssistant update fails -> rollback!")
            await _update(rollback)
        else:
            raise HomeAssistantUpdateError()

    async def _start(self):
        """Start HomeAssistant docker & wait."""
        if not await self.instance.run():
            raise HomeAssistantError()
        await self._block_till_run()

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
        await self._start()

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
            raise HomeAssistantError()

        # parse output
        log = convert_to_ascii(result.output)
        if result.exit_code != 0 or RE_YAML_ERROR.search(log):
            return ConfigResult(False, log)
        return ConfigResult(True, log)

    async def ensure_access_token(self):
        """Ensures there is an access token."""
        if self.access_token is not None:
            return

        with suppress(asyncio.TimeoutError, aiohttp.ClientError):
            async with self.sys_websession_ssl.get(
                    f"{self.api_url}/auth/token",
                    timeout=30,
                    data={
                        "grant_type": "refresh_token",
                        "refresh_token": self.refresh_token
                    }
            ) as resp:
                if resp.status != 200:
                    _LOGGER.error("Authenticate problem with HomeAssistant!")
                    raise HomeAssistantAuthError()
                tokens = await resp.json()
                self.access_token = tokens['access_token']
                return

        _LOGGER.error("Can't update HomeAssistant access token!")
        raise HomeAssistantAPIError()

    @asynccontextmanager
    async def make_request(self, method, path, json=None, content_type=None,
                           data=None, timeout=30):
        """Async context manager to make a request with right auth."""
        url = f"{self.api_url}/{path}"
        headers = {}

        # Passthrough content type
        if content_type is not None:
            headers[hdrs.CONTENT_TYPE] = content_type

        # Set old API Password
        if self.api_password:
            headers[HEADER_HA_ACCESS] = self.api_password

        for _ in (1, 2):
            # Prepare Access token
            if self.refresh_token:
                await self.ensure_access_token()
                headers[hdrs.AUTHORIZATION] = f'Bearer {self.access_token}'

            async with getattr(self.sys_websession_ssl, method)(
                    url, data=data, timeout=timeout, json=json, headers=headers
            ) as resp:
                # Access token expired
                if resp.status == 401 and self.refresh_token:
                    self.access_token = None
                    continue
                yield resp
                return

        raise HomeAssistantAPIError()

    async def check_api_state(self):
        """Return True if Home-Assistant up and running."""
        with suppress(HomeAssistantAPIError):
            async with self.make_request('get', 'api/') as resp:
                if resp.status in (200, 201):
                    return True
                err = resp.status

        _LOGGER.warning("Home-Assistant API config missmatch: %d", err)
        return False

    async def send_event(self, event_type, event_data=None):
        """Send event to Home-Assistant."""
        with suppress(HomeAssistantAPIError):
            async with self.make_request(
                    'get', f'api/events/{event_type}'
            ) as resp:
                if resp.status in (200, 201):
                    return
                err = resp.status

        _LOGGER.warning("HomeAssistant event %s fails: %s", event_type, err)
        return HomeAssistantError()

    async def _block_till_run(self):
        """Block until Home-Assistant is booting up or startup timeout."""
        start_time = time.monotonic()

        def check_port():
            """Check if port is mapped."""
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                result = sock.connect_ex((str(self.api_ip), self.api_port))
                sock.close()

                # Check if the port is available
                if result == 0:
                    return True
            except OSError:
                pass
            return False

        while time.monotonic() - start_time < self.wait_boot:
            # Check if API response
            if await self.sys_run_in_executor(check_port):
                _LOGGER.info("Detect a running HomeAssistant instance")
                self._error_state = False
                return

            # wait and don't hit the system
            await asyncio.sleep(10)

            # Check if Container is is_running
            if not await self.instance.is_running():
                _LOGGER.error("Home Assistant is crashed!")
                break

        _LOGGER.warning("Don't wait anymore of HomeAssistant startup!")
        self._error_state = True
        raise HomeAssistantError()
