"""Home Assistant control object."""
import asyncio
from contextlib import asynccontextmanager, suppress
from datetime import datetime, timedelta
from ipaddress import IPv4Address
import logging
import os
from pathlib import Path
import re
import secrets
import shutil
import time
from typing import Any, AsyncContextManager, Awaitable, Dict, Optional
from uuid import UUID

import aiohttp
from aiohttp import hdrs
import attr
from packaging import version as pkg_version

from .const import (
    ATTR_ACCESS_TOKEN,
    ATTR_AUDIO_INPUT,
    ATTR_AUDIO_OUTPUT,
    ATTR_BOOT,
    ATTR_IMAGE,
    ATTR_VERSION_LATEST,
    ATTR_PORT,
    ATTR_REFRESH_TOKEN,
    ATTR_SSL,
    ATTR_UUID,
    ATTR_VERSION,
    ATTR_WAIT_BOOT,
    ATTR_WATCHDOG,
    FILE_HASSIO_HOMEASSISTANT,
)
from .coresys import CoreSys, CoreSysAttributes
from .docker.homeassistant import DockerHomeAssistant
from .docker.stats import DockerStats
from .exceptions import (
    DockerAPIError,
    HomeAssistantAPIError,
    HomeAssistantAuthError,
    HomeAssistantError,
    HomeAssistantUpdateError,
)
from .utils import check_port, convert_to_ascii, process_lock
from .utils.json import JsonConfig
from .validate import SCHEMA_HASS_CONFIG

_LOGGER: logging.Logger = logging.getLogger(__name__)

RE_YAML_ERROR = re.compile(r"homeassistant\.util\.yaml")


@attr.s(frozen=True)
class ConfigResult:
    """Return object from config check."""

    valid = attr.ib()
    log = attr.ib()


class HomeAssistant(JsonConfig, CoreSysAttributes):
    """Home Assistant core object for handle it."""

    def __init__(self, coresys: CoreSys):
        """Initialize Home Assistant object."""
        super().__init__(FILE_HASSIO_HOMEASSISTANT, SCHEMA_HASS_CONFIG)
        self.coresys: CoreSys = coresys
        self.instance: DockerHomeAssistant = DockerHomeAssistant(coresys)
        self.lock: asyncio.Lock = asyncio.Lock(loop=coresys.loop)
        self._error_state: bool = False

        # We don't persist access tokens. Instead we fetch new ones when needed
        self.access_token: Optional[str] = None
        self._access_token_expires: Optional[datetime] = None

    async def load(self) -> None:
        """Prepare Home Assistant object."""
        try:
            # Evaluate Version if we lost this information
            if not self.version:
                self.version = await self.instance.get_latest_version(
                    key=pkg_version.parse
                )

            await self.instance.attach(tag=self.version)
        except DockerAPIError:
            _LOGGER.info("No Home Assistant Docker image %s found.", self.image)
            await self.install_landingpage()
        else:
            self.version = self.instance.version
            self.image = self.instance.image
            self.save_data()

    @property
    def machine(self) -> str:
        """Return the system machines."""
        return self.instance.machine

    @property
    def arch(self) -> str:
        """Return arch of running Home Assistant."""
        return self.instance.arch

    @property
    def error_state(self) -> bool:
        """Return True if system is in error."""
        return self._error_state

    @property
    def ip_address(self) -> IPv4Address:
        """Return IP of Home Assistant instance."""
        return self.instance.ip_address

    @property
    def api_port(self) -> int:
        """Return network port to Home Assistant instance."""
        return self._data[ATTR_PORT]

    @api_port.setter
    def api_port(self, value: int) -> None:
        """Set network port for Home Assistant instance."""
        self._data[ATTR_PORT] = value

    @property
    def api_ssl(self) -> bool:
        """Return if we need ssl to Home Assistant instance."""
        return self._data[ATTR_SSL]

    @api_ssl.setter
    def api_ssl(self, value: bool):
        """Set SSL for Home Assistant instance."""
        self._data[ATTR_SSL] = value

    @property
    def api_url(self) -> str:
        """Return API url to Home Assistant."""
        return "{}://{}:{}".format(
            "https" if self.api_ssl else "http", self.ip_address, self.api_port
        )

    @property
    def watchdog(self) -> bool:
        """Return True if the watchdog should protect Home Assistant."""
        return self._data[ATTR_WATCHDOG]

    @watchdog.setter
    def watchdog(self, value: bool):
        """Return True if the watchdog should protect Home Assistant."""
        self._data[ATTR_WATCHDOG] = value

    @property
    def wait_boot(self) -> int:
        """Return time to wait for Home Assistant startup."""
        return self._data[ATTR_WAIT_BOOT]

    @wait_boot.setter
    def wait_boot(self, value: int):
        """Set time to wait for Home Assistant startup."""
        self._data[ATTR_WAIT_BOOT] = value

    @property
    def latest_version(self) -> str:
        """Return last available version of Home Assistant."""
        return self.sys_updater.version_homeassistant

    @latest_version.setter
    def latest_version(self, value: str):
        """Set last available version of Home Assistant."""
        if value:
            self._data[ATTR_VERSION_LATEST] = value
        else:
            self._data.pop(ATTR_VERSION_LATEST, None)

    @property
    def image(self) -> str:
        """Return image name of the Home Assistant container."""
        if self._data.get(ATTR_IMAGE):
            return self._data[ATTR_IMAGE]
        return os.environ["HOMEASSISTANT_REPOSITORY"]

    @image.setter
    def image(self, value: str) -> None:
        """Set image name of Home Assistant container."""
        self._data[ATTR_IMAGE] = value

    @property
    def version(self) -> Optional[str]:
        """Return version of local version."""
        return self._data.get(ATTR_VERSION)

    @version.setter
    def version(self, value: str) -> None:
        """Set installed version."""
        self._data[ATTR_VERSION] = value

    @property
    def boot(self) -> bool:
        """Return True if Home Assistant boot is enabled."""
        return self._data[ATTR_BOOT]

    @boot.setter
    def boot(self, value: bool):
        """Set Home Assistant boot options."""
        self._data[ATTR_BOOT] = value

    @property
    def uuid(self) -> UUID:
        """Return a UUID of this Home Assistant instance."""
        return self._data[ATTR_UUID]

    @property
    def supervisor_token(self) -> str:
        """Return an access token for the Supervisor API."""
        return self._data.get(ATTR_ACCESS_TOKEN)

    @property
    def refresh_token(self) -> str:
        """Return the refresh token to authenticate with Home Assistant."""
        return self._data.get(ATTR_REFRESH_TOKEN)

    @refresh_token.setter
    def refresh_token(self, value: str):
        """Set Home Assistant refresh_token."""
        self._data[ATTR_REFRESH_TOKEN] = value

    @property
    def path_pulse(self):
        """Return path to asound config."""
        return Path(self.sys_config.path_tmp, "homeassistant_pulse")

    @property
    def path_extern_pulse(self):
        """Return path to asound config for Docker."""
        return Path(self.sys_config.path_extern_tmp, "homeassistant_pulse")

    @property
    def audio_output(self) -> Optional[str]:
        """Return a pulse profile for output or None."""
        return self._data[ATTR_AUDIO_OUTPUT]

    @audio_output.setter
    def audio_output(self, value: Optional[str]):
        """Set audio output profile settings."""
        self._data[ATTR_AUDIO_OUTPUT] = value

    @property
    def audio_input(self) -> Optional[str]:
        """Return pulse profile for input or None."""
        return self._data[ATTR_AUDIO_INPUT]

    @audio_input.setter
    def audio_input(self, value: Optional[str]):
        """Set audio input settings."""
        self._data[ATTR_AUDIO_INPUT] = value

    @process_lock
    async def install_landingpage(self) -> None:
        """Install a landing page."""
        _LOGGER.info("Setup HomeAssistant landingpage")
        while True:
            try:
                await self.instance.install(
                    "landingpage", image=self.sys_updater.image_homeassistant
                )
            except DockerAPIError:
                _LOGGER.warning("Fails install landingpage, retry after 30sec")
                await asyncio.sleep(30)
            else:
                self.version = self.instance.version
                self.image = self.sys_updater.image_homeassistant
                self.save_data()
                break

        # Start landingpage
        _LOGGER.info("Start HomeAssistant landingpage")
        with suppress(HomeAssistantError):
            await self._start()

    @process_lock
    async def install(self) -> None:
        """Install a landing page."""
        _LOGGER.info("Setup Home Assistant")
        while True:
            # read homeassistant tag and install it
            if not self.latest_version:
                await self.sys_updater.reload()

            tag = self.latest_version
            if tag:
                with suppress(DockerAPIError):
                    await self.instance.update(
                        tag, image=self.sys_updater.image_homeassistant
                    )
                    break
            _LOGGER.warning("Error on install Home Assistant. Retry in 30sec")
            await asyncio.sleep(30)

        _LOGGER.info("Home Assistant docker now installed")
        self.version = self.instance.version
        self.image = self.sys_updater.image_homeassistant
        self.save_data()

        # finishing
        try:
            _LOGGER.info("Start Home Assistant")
            await self._start()
        except HomeAssistantError:
            _LOGGER.error("Can't start Home Assistant!")

        # Cleanup
        with suppress(DockerAPIError):
            await self.instance.cleanup()

    @process_lock
    async def update(self, version: Optional[str] = None) -> None:
        """Update HomeAssistant version."""
        version = version or self.latest_version
        old_image = self.image
        rollback = self.version if not self.error_state else None
        running = await self.instance.is_running()
        exists = await self.instance.exists()

        if exists and version == self.instance.version:
            _LOGGER.warning("Version %s is already installed", version)
            return

        # process an update
        async def _update(to_version: str) -> None:
            """Run Home Assistant update."""
            _LOGGER.info("Update Home Assistant to version %s", to_version)
            try:
                await self.instance.update(
                    to_version, image=self.sys_updater.image_homeassistant
                )
            except DockerAPIError:
                _LOGGER.warning("Update Home Assistant image fails")
                raise HomeAssistantUpdateError() from None
            else:
                self.version = self.instance.version
                self.image = self.sys_updater.image_homeassistant

            if running:
                await self._start()
            _LOGGER.info("Successful run Home Assistant %s", to_version)

            # Successfull - last step
            self.save_data()
            with suppress(DockerAPIError):
                await self.instance.cleanup(old_image=old_image)

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

    async def _start(self) -> None:
        """Start Home Assistant Docker & wait."""
        # Create new API token
        self._data[ATTR_ACCESS_TOKEN] = secrets.token_hex(56)
        self.save_data()

        # Write audio settings
        self.write_pulse()

        try:
            await self.instance.run()
        except DockerAPIError:
            raise HomeAssistantError() from None
        await self._block_till_run()

    @process_lock
    async def start(self) -> None:
        """Run Home Assistant docker."""
        if await self.instance.is_running():
            _LOGGER.warning("Home Assistant is already running!")
            return

        # Instance/Container exists, simple start
        if await self.instance.is_initialize():
            try:
                await self.instance.start()
            except DockerAPIError:
                raise HomeAssistantError() from None

            await self._block_till_run()
        # No Instance/Container found, extended start
        else:
            await self._start()

    @process_lock
    async def stop(self) -> None:
        """Stop Home Assistant Docker.

        Return a coroutine.
        """
        try:
            return await self.instance.stop(remove_container=False)
        except DockerAPIError:
            raise HomeAssistantError() from None

    @process_lock
    async def restart(self) -> None:
        """Restart Home Assistant Docker."""
        try:
            await self.instance.restart()
        except DockerAPIError:
            raise HomeAssistantError() from None

        await self._block_till_run()

    @process_lock
    async def rebuild(self) -> None:
        """Rebuild Home Assistant Docker container."""
        with suppress(DockerAPIError):
            await self.instance.stop()
        await self._start()

    def logs(self) -> Awaitable[bytes]:
        """Get HomeAssistant docker logs.

        Return a coroutine.
        """
        return self.instance.logs()

    async def stats(self) -> DockerStats:
        """Return stats of Home Assistant.

        Return a coroutine.
        """
        try:
            return await self.instance.stats()
        except DockerAPIError:
            raise HomeAssistantError() from None

    def is_running(self) -> Awaitable[bool]:
        """Return True if Docker container is running.

        Return a coroutine.
        """
        return self.instance.is_running()

    def is_fails(self) -> Awaitable[bool]:
        """Return True if a Docker container is fails state.

        Return a coroutine.
        """
        return self.instance.is_fails()

    @property
    def in_progress(self) -> bool:
        """Return True if a task is in progress."""
        return self.instance.in_progress or self.lock.locked()

    async def check_config(self) -> ConfigResult:
        """Run Home Assistant config check."""
        result = await self.instance.execute_command(
            "python3 -m homeassistant -c /config --script check_config"
        )

        # If not valid
        if result.exit_code is None:
            _LOGGER.error("Fatal error on config check!")
            raise HomeAssistantError()

        # Convert output
        log = convert_to_ascii(result.output)
        _LOGGER.debug("Result config check: %s", log.strip())

        # Parse output
        if result.exit_code != 0 or RE_YAML_ERROR.search(log):
            _LOGGER.error("Invalid Home Assistant config found!")
            return ConfigResult(False, log)

        _LOGGER.info("Home Assistant config is valid")
        return ConfigResult(True, log)

    async def ensure_access_token(self) -> None:
        """Ensures there is an access token."""
        if (
            self.access_token is not None
            and self._access_token_expires > datetime.utcnow()
        ):
            return

        with suppress(asyncio.TimeoutError, aiohttp.ClientError):
            async with self.sys_websession_ssl.post(
                f"{self.api_url}/auth/token",
                timeout=30,
                data={
                    "grant_type": "refresh_token",
                    "refresh_token": self.refresh_token,
                },
            ) as resp:
                if resp.status != 200:
                    _LOGGER.error("Can't update Home Assistant access token!")
                    raise HomeAssistantAuthError()

                _LOGGER.info("Updated Home Assistant API token")
                tokens = await resp.json()
                self.access_token = tokens["access_token"]
                self._access_token_expires = datetime.utcnow() + timedelta(
                    seconds=tokens["expires_in"]
                )

    @asynccontextmanager
    async def make_request(
        self,
        method: str,
        path: str,
        json: Optional[Dict[str, Any]] = None,
        content_type: Optional[str] = None,
        data: Any = None,
        timeout: int = 30,
        params: Optional[Dict[str, str]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> AsyncContextManager[aiohttp.ClientResponse]:
        """Async context manager to make a request with right auth."""
        url = f"{self.api_url}/{path}"
        headers = headers or {}

        # Passthrough content type
        if content_type is not None:
            headers[hdrs.CONTENT_TYPE] = content_type

        for _ in (1, 2):
            # Prepare Access token
            if self.refresh_token:
                await self.ensure_access_token()
                headers[hdrs.AUTHORIZATION] = f"Bearer {self.access_token}"

            try:
                async with getattr(self.sys_websession_ssl, method)(
                    url,
                    data=data,
                    timeout=timeout,
                    json=json,
                    headers=headers,
                    params=params,
                ) as resp:
                    # Access token expired
                    if resp.status == 401 and self.refresh_token:
                        self.access_token = None
                        continue
                    yield resp
                    return
            except (asyncio.TimeoutError, aiohttp.ClientError) as err:
                _LOGGER.error("Error on call %s: %s", url, err)
                break

        raise HomeAssistantAPIError()

    async def check_api_state(self) -> bool:
        """Return True if Home Assistant up and running."""
        with suppress(HomeAssistantAPIError):
            async with self.make_request("get", "api/") as resp:
                if resp.status in (200, 201):
                    return True
                status = resp.status
            _LOGGER.warning("Home Assistant API config mismatch: %s", status)

        return False

    async def _block_till_run(self) -> None:
        """Block until Home-Assistant is booting up or startup timeout."""
        start_time = time.monotonic()

        # Database migration
        migration_progress = False
        migration_file = Path(self.sys_config.path_homeassistant, ".migration_progress")

        # PIP installation
        pip_progress = False
        pip_file = Path(self.sys_config.path_homeassistant, ".pip_progress")

        while True:
            await asyncio.sleep(5)

            # 1: Check if Container is is_running
            if not await self.instance.is_running():
                _LOGGER.error("Home Assistant has crashed!")
                break

            # 2: Check if API response
            if await self.sys_run_in_executor(
                check_port, self.ip_address, self.api_port
            ):
                _LOGGER.info("Detect a running Home Assistant instance")
                self._error_state = False
                return

            # 3: Running DB Migration
            if migration_file.exists():
                if not migration_progress:
                    migration_progress = True
                    _LOGGER.info("Home Assistant record migration in progress")
                continue
            if migration_progress:
                migration_progress = False  # Reset start time
                start_time = time.monotonic()
                _LOGGER.info("Home Assistant record migration done")

            # 4: Running PIP installation
            if pip_file.exists():
                if not pip_progress:
                    pip_progress = True
                    _LOGGER.info("Home Assistant pip installation in progress")
                continue
            if pip_progress:
                pip_progress = False  # Reset start time
                start_time = time.monotonic()
                _LOGGER.info("Home Assistant pip installation done")

            # 5: Timeout
            if time.monotonic() - start_time > self.wait_boot:
                _LOGGER.warning("Don't wait anymore of Home Assistant startup!")
                break

        self._error_state = True
        raise HomeAssistantError()

    async def repair(self):
        """Repair local Home Assistant data."""
        if await self.instance.exists():
            return

        _LOGGER.info("Repair Home Assistant %s", self.version)
        await self.sys_run_in_executor(
            self.sys_docker.network.stale_cleanup, self.instance.name
        )

        # Pull image
        try:
            await self.instance.install(self.version)
        except DockerAPIError:
            _LOGGER.error("Repairing of Home Assistant fails")

    def write_pulse(self):
        """Write asound config to file and return True on success."""
        pulse_config = self.sys_audio.pulse_client(
            input_profile=self.audio_input, output_profile=self.audio_output
        )

        # Cleanup wrong maps
        if self.path_pulse.is_dir():
            shutil.rmtree(self.path_pulse, ignore_errors=True)

        # Write pulse config
        try:
            with self.path_pulse.open("w") as config_file:
                config_file.write(pulse_config)
        except OSError as err:
            _LOGGER.error("Home Assistant can't write pulse/client.config: %s", err)
        else:
            _LOGGER.info("Update pulse/client.config: %s", self.path_pulse)
