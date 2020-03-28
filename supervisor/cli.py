"""CLI support on supervisor."""
import asyncio
from contextlib import suppress
import logging
import secrets
from typing import Awaitable, Optional

from .const import ATTR_ACCESS_TOKEN, ATTR_VERSION, FILE_HASSIO_CLI
from .coresys import CoreSys, CoreSysAttributes
from .docker.cli import DockerCli
from .docker.stats import DockerStats
from .exceptions import CliError, CliUpdateError, DockerAPIError
from .utils.json import JsonConfig
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
                self.version = await self.instance.get_latest_version(key=int)

            await self.instance.attach(tag=self.version)
        except DockerAPIError:
            _LOGGER.info("No Audio plugin Docker image %s found.", self.instance.image)

            # Install cli
            with suppress(CliError):
                await self.install()
        else:
            self.version = self.instance.version
            self.save_data()

        # Run PulseAudio
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
                with suppress(DockerAPIError):
                    await self.instance.install(self.latest_version)
                    break
            _LOGGER.warning("Error on install cli plugin. Retry in 30sec")
            await asyncio.sleep(30)

        _LOGGER.info("cli plugin now installed")
        self.version = self.instance.version
        self.save_data()

    async def update(self, version: Optional[str] = None) -> None:
        """Update local HA cli."""
        version = version or self.latest_version

        if version == self.version:
            _LOGGER.warning("Version %s is already installed for cli", version)
            return

        try:
            await self.instance.update(version, latest=True)
        except DockerAPIError:
            _LOGGER.error("HA cli update fails")
            raise CliUpdateError() from None

        # Cleanup
        with suppress(DockerAPIError):
            await self.instance.cleanup()
        
        self.version = version
        self.save_data()

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
        except DockerAPIError:
            _LOGGER.error("Can't start cli plugin")
            raise CliError() from None

    async def stats(self) -> DockerStats:
        """Return stats of cli."""
        try:
            return await self.instance.stats()
        except DockerAPIError:
            raise CliError() from None

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
        except DockerAPIError:
            _LOGGER.error("Repairing of HA cli fails")
