"""Home Assistant observer plugin.

Code: https://github.com/home-assistant/plugin-observer
"""
import asyncio
from contextlib import suppress
import logging
import secrets
from typing import Optional

import aiohttp
from awesomeversion import AwesomeVersion

from ..const import ATTR_ACCESS_TOKEN
from ..coresys import CoreSys
from ..docker.observer import DockerObserver
from ..docker.stats import DockerStats
from ..exceptions import DockerError, ObserverError, ObserverUpdateError
from .base import PluginBase
from .const import FILE_HASSIO_OBSERVER
from .validate import SCHEMA_OBSERVER_CONFIG

_LOGGER: logging.Logger = logging.getLogger(__name__)


class PluginObserver(PluginBase):
    """Supervisor observer instance."""

    def __init__(self, coresys: CoreSys):
        """Initialize observer handler."""
        super().__init__(FILE_HASSIO_OBSERVER, SCHEMA_OBSERVER_CONFIG)
        self.slug = "observer"
        self.coresys: CoreSys = coresys
        self.instance: DockerObserver = DockerObserver(coresys)

    @property
    def latest_version(self) -> Optional[AwesomeVersion]:
        """Return version of latest observer."""
        return self.sys_updater.version_observer

    @property
    def supervisor_token(self) -> str:
        """Return an access token for the Observer API."""
        return self._data.get(ATTR_ACCESS_TOKEN)

    async def load(self) -> None:
        """Load observer setup."""
        # Check observer state
        try:
            # Evaluate Version if we lost this information
            if not self.version:
                self.version = await self.instance.get_latest_version()

            await self.instance.attach(version=self.version)
        except DockerError:
            _LOGGER.info(
                "No observer plugin Docker image %s found.", self.instance.image
            )

            # Install observer
            with suppress(ObserverError):
                await self.install()
        else:
            self.version = self.instance.version
            self.image = self.instance.image
            self.save_data()

        # Run Observer
        with suppress(ObserverError):
            if not await self.instance.is_running():
                await self.start()

    async def install(self) -> None:
        """Install observer."""
        _LOGGER.info("Running setup for observer plugin")
        while True:
            # read observer tag and install it
            if not self.latest_version:
                await self.sys_updater.reload()

            if self.latest_version:
                with suppress(DockerError):
                    await self.instance.install(
                        self.latest_version, image=self.sys_updater.image_observer
                    )
                    break
            _LOGGER.warning("Error on install observer plugin. Retry in 30sec")
            await asyncio.sleep(30)

        _LOGGER.info("observer plugin now installed")
        self.version = self.instance.version
        self.image = self.sys_updater.image_observer
        self.save_data()

    async def update(self, version: Optional[AwesomeVersion] = None) -> None:
        """Update local HA observer."""
        version = version or self.latest_version
        old_image = self.image

        if version == self.version:
            _LOGGER.warning("Version %s is already installed for observer", version)
            return

        try:
            await self.instance.update(version, image=self.sys_updater.image_observer)
        except DockerError as err:
            _LOGGER.error("HA observer update failed")
            raise ObserverUpdateError() from err
        else:
            self.version = version
            self.image = self.sys_updater.image_observer
            self.save_data()

        # Cleanup
        with suppress(DockerError):
            await self.instance.cleanup(old_image=old_image)

        # Start observer
        await self.start()

    async def start(self) -> None:
        """Run observer."""
        # Create new API token
        self._data[ATTR_ACCESS_TOKEN] = secrets.token_hex(56)
        self.save_data()

        # Start Instance
        _LOGGER.info("Starting observer plugin")
        try:
            await self.instance.run()
        except DockerError as err:
            _LOGGER.error("Can't start observer plugin")
            raise ObserverError() from err

    async def stats(self) -> DockerStats:
        """Return stats of observer."""
        try:
            return await self.instance.stats()
        except DockerError as err:
            raise ObserverError() from err

    async def rebuild(self) -> None:
        """Rebuild Observer Docker container."""
        with suppress(DockerError):
            await self.instance.stop()
        await self.start()

    async def check_system_runtime(self) -> bool:
        """Check if the observer is running."""
        try:
            timeout = aiohttp.ClientTimeout(total=10)
            async with self.sys_websession.get(
                f"http://{self.sys_docker.network.observer!s}/ping", timeout=timeout
            ) as request:
                if request.status == 200:
                    return True
        except (aiohttp.ClientError, asyncio.TimeoutError):
            pass

        return False

    async def repair(self) -> None:
        """Repair observer container."""
        if await self.instance.exists():
            return

        _LOGGER.info("Repairing HA observer %s", self.version)
        try:
            await self.instance.install(self.version)
        except DockerError as err:
            _LOGGER.error("Repair of HA observer failed")
            self.sys_capture_exception(err)
