"""Home Assistant cli plugin.

Code: https://github.com/home-assistant/plugin-cli
"""
import asyncio
from contextlib import suppress
import logging
import secrets
from typing import Awaitable, Optional

from ..const import ATTR_ACCESS_TOKEN, ATTR_IMAGE, ATTR_VERSION
from ..coresys import CoreSys, CoreSysAttributes
from ..docker.cli import DockerCli
from ..docker.stats import DockerStats
from ..exceptions import CliError, CliUpdateError, DockerError
from ..utils.json import JsonConfig
from .const import FILE_HASSIO_CLI
from .validate import SCHEMA_CLI_CONFIG

_LOGGER: logging.Logger = logging.getLogger(__name__)


class HaCli(CoreSysAttributes, JsonConfig):
    """HA cli interface inside supervisor."""

    def __init__(self, coresys: CoreSys):
        """Initialize cli handler."""
        super().__init__(FILE_HASSIO_CLI, SCHEMA_CLI_CONFIG)
        self.coresys: CoreSys = coresys
        self.instance: DockerCli = DockerCli(coresys)

    @property
    def version(self) -> Optional[str]:
        """Return version of cli."""
        return self._data.get(ATTR_VERSION)

    @version.setter
    def version(self, value: str) -> None:
        """Set current version of cli."""
        self._data[ATTR_VERSION] = value

    @property
    def image(self) -> str:
        """Return current image of cli."""
        if self._data.get(ATTR_IMAGE):
            return self._data[ATTR_IMAGE]
        return f"homeassistant/{self.sys_arch.supervisor}-hassio-cli"

    @image.setter
    def image(self, value: str) -> None:
        """Return current image of cli."""
        self._data[ATTR_IMAGE] = value

    @property
    def latest_version(self) -> str:
        """Return version of latest cli."""
        return self.sys_updater.version_cli

    @property
    def need_update(self) -> bool:
        """Return true if a cli update is available."""
        return self.version != self.latest_version

    @property
    def supervisor_token(self) -> str:
        """Return an access token for the Supervisor API."""
        return self._data.get(ATTR_ACCESS_TOKEN)

    @property
    def in_progress(self) -> bool:
        """Return True if a task is in progress."""
        return self.instance.in_progress

    async def load(self) -> None:
        """Load cli setup."""
        # Check cli state
        try:
            # Evaluate Version if we lost this information
            if not self.version:
                self.version = await self.instance.get_latest_version()

            await self.instance.attach(tag=self.version)
        except DockerError:
            _LOGGER.info("No cli plugin Docker image %s found.", self.instance.image)

            # Install cli
            with suppress(CliError):
                await self.install()
        else:
            self.version = self.instance.version
            self.image = self.instance.image
            self.save_data()

        # Run CLI
        with suppress(CliError):
            if not await self.instance.is_running():
                await self.start()

    async def install(self) -> None:
        """Install cli."""
        _LOGGER.info("Setup cli plugin")
        while True:
            # read audio tag and install it
            if not self.latest_version:
                await self.sys_updater.reload()

            if self.latest_version:
                with suppress(DockerError):
                    await self.instance.install(
                        self.latest_version,
                        image=self.sys_updater.image_cli,
                        latest=True,
                    )
                    break
            _LOGGER.warning("Error on install cli plugin. Retry in 30sec")
            await asyncio.sleep(30)

        _LOGGER.info("cli plugin now installed")
        self.version = self.instance.version
        self.image = self.sys_updater.image_cli
        self.save_data()

    async def update(self, version: Optional[str] = None) -> None:
        """Update local HA cli."""
        version = version or self.latest_version
        old_image = self.image

        if version == self.version:
            _LOGGER.warning("Version %s is already installed for cli", version)
            return

        try:
            await self.instance.update(
                version, image=self.sys_updater.image_cli, latest=True
            )
        except DockerError as err:
            _LOGGER.error("HA cli update failed")
            raise CliUpdateError() from err
        else:
            self.version = version
            self.image = self.sys_updater.image_cli
            self.save_data()

        # Cleanup
        with suppress(DockerError):
            await self.instance.cleanup(old_image=old_image)

        # Start cli
        await self.start()

    async def start(self) -> None:
        """Run cli."""
        # Create new API token
        self._data[ATTR_ACCESS_TOKEN] = secrets.token_hex(56)
        self.save_data()

        # Start Instance
        _LOGGER.info("Start cli plugin")
        try:
            await self.instance.run()
        except DockerError as err:
            _LOGGER.error("Can't start cli plugin")
            raise CliError() from err

    async def stop(self) -> None:
        """Stop cli."""
        _LOGGER.info("Stop cli plugin")
        try:
            await self.instance.stop()
        except DockerError as err:
            _LOGGER.error("Can't stop cli plugin")
            raise CliError() from err

    async def stats(self) -> DockerStats:
        """Return stats of cli."""
        try:
            return await self.instance.stats()
        except DockerError as err:
            raise CliError() from err

    def is_running(self) -> Awaitable[bool]:
        """Return True if Docker container is running.

        Return a coroutine.
        """
        return self.instance.is_running()

    async def repair(self) -> None:
        """Repair cli container."""
        if await self.instance.exists():
            return

        _LOGGER.info("Repair HA cli %s", self.version)
        try:
            await self.instance.install(self.version, latest=True)
        except DockerError as err:
            _LOGGER.error("Repairing of HA cli failed")
            self.sys_capture_exception(err)
