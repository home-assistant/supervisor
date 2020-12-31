"""Home Assistant multicast plugin.

Code: https://github.com/home-assistant/plugin-multicast
"""
import asyncio
from contextlib import suppress
import logging
from typing import Awaitable, Optional

from awesomeversion import AwesomeVersion

from ..coresys import CoreSys
from ..docker.multicast import DockerMulticast
from ..docker.stats import DockerStats
from ..exceptions import DockerError, MulticastError, MulticastUpdateError
from .base import PluginBase
from .const import FILE_HASSIO_MULTICAST
from .validate import SCHEMA_MULTICAST_CONFIG

_LOGGER: logging.Logger = logging.getLogger(__name__)


class PluginMulticast(PluginBase):
    """Home Assistant core object for handle it."""

    def __init__(self, coresys: CoreSys):
        """Initialize hass object."""
        super().__init__(FILE_HASSIO_MULTICAST, SCHEMA_MULTICAST_CONFIG)
        self.slug = "multicast"
        self.coresys: CoreSys = coresys
        self.instance: DockerMulticast = DockerMulticast(coresys)

    @property
    def latest_version(self) -> Optional[AwesomeVersion]:
        """Return latest version of Multicast."""
        return self.sys_updater.version_multicast

    @property
    def in_progress(self) -> bool:
        """Return True if a task is in progress."""
        return self.instance.in_progress

    async def load(self) -> None:
        """Load multicast setup."""
        # Check Multicast state
        try:
            # Evaluate Version if we lost this information
            if not self.version:
                self.version = await self.instance.get_latest_version()

            await self.instance.attach(version=self.version)
        except DockerError:
            _LOGGER.info(
                "No Multicast plugin Docker image %s found.", self.instance.image
            )

            # Install Multicast plugin
            with suppress(MulticastError):
                await self.install()
        else:
            self.version = self.instance.version
            self.image = self.instance.image
            self.save_data()

        # Run Multicast plugin
        with suppress(MulticastError):
            if not await self.instance.is_running():
                await self.start()

    async def install(self) -> None:
        """Install Multicast."""
        _LOGGER.info("Running setup for Multicast plugin")
        while True:
            # read homeassistant tag and install it
            if not self.latest_version:
                await self.sys_updater.reload()

            if self.latest_version:
                with suppress(DockerError):
                    await self.instance.install(
                        self.latest_version, image=self.sys_updater.image_multicast
                    )
                    break
            _LOGGER.warning("Error on install Multicast plugin. Retry in 30sec")
            await asyncio.sleep(30)

        _LOGGER.info("Multicast plugin is now installed")
        self.version = self.instance.version
        self.image = self.sys_updater.image_multicast
        self.save_data()

    async def update(self, version: Optional[AwesomeVersion] = None) -> None:
        """Update Multicast plugin."""
        version = version or self.latest_version
        old_image = self.image

        if version == self.version:
            _LOGGER.warning("Version %s is already installed for Multicast", version)
            return

        # Update
        try:
            await self.instance.update(version, image=self.sys_updater.image_multicast)
        except DockerError as err:
            _LOGGER.error("Multicast update failed")
            raise MulticastUpdateError() from err
        else:
            self.version = version
            self.image = self.sys_updater.image_multicast
            self.save_data()

        # Cleanup
        with suppress(DockerError):
            await self.instance.cleanup(old_image=old_image)

        # Start Multicast plugin
        await self.start()

    async def restart(self) -> None:
        """Restart Multicast plugin."""
        _LOGGER.info("Restarting Multicast plugin")
        try:
            await self.instance.restart()
        except DockerError as err:
            _LOGGER.error("Can't start Multicast plugin")
            raise MulticastError() from err

    async def start(self) -> None:
        """Run Multicast."""
        _LOGGER.info("Starting Multicast plugin")
        try:
            await self.instance.run()
        except DockerError as err:
            _LOGGER.error("Can't start Multicast plugin")
            raise MulticastError() from err

    async def stop(self) -> None:
        """Stop Multicast."""
        _LOGGER.info("Stopping Multicast plugin")
        try:
            await self.instance.stop()
        except DockerError as err:
            _LOGGER.error("Can't stop Multicast plugin")
            raise MulticastError() from err

    def logs(self) -> Awaitable[bytes]:
        """Get Multicast docker logs.

        Return Coroutine.
        """
        return self.instance.logs()

    async def stats(self) -> DockerStats:
        """Return stats of Multicast."""
        try:
            return await self.instance.stats()
        except DockerError as err:
            raise MulticastError() from err

    def is_running(self) -> Awaitable[bool]:
        """Return True if Docker container is running.

        Return a coroutine.
        """
        return self.instance.is_running()

    def is_failed(self) -> Awaitable[bool]:
        """Return True if a Docker container is failed state.

        Return a coroutine.
        """
        return self.instance.is_failed()

    async def repair(self) -> None:
        """Repair Multicast plugin."""
        if await self.instance.exists():
            return

        _LOGGER.info("Repairing Multicast %s", self.version)
        try:
            await self.instance.install(self.version)
        except DockerError as err:
            _LOGGER.error("Repair of Multicast failed")
            self.sys_capture_exception(err)
