"""Home Assistant multicast plugin.

Code: https://github.com/home-assistant/plugin-multicast
"""
import asyncio
from contextlib import suppress
import logging
from typing import Awaitable, Optional

from ..const import ATTR_IMAGE, ATTR_VERSION, FILE_HASSIO_MULTICAST
from ..coresys import CoreSys, CoreSysAttributes
from ..docker.multicast import DockerMulticast
from ..docker.stats import DockerStats
from ..exceptions import DockerAPIError, MulticastError, MulticastUpdateError
from ..utils.json import JsonConfig
from .validate import SCHEMA_MULTICAST_CONFIG

_LOGGER: logging.Logger = logging.getLogger(__name__)


class Multicast(JsonConfig, CoreSysAttributes):
    """Home Assistant core object for handle it."""

    def __init__(self, coresys: CoreSys):
        """Initialize hass object."""
        super().__init__(FILE_HASSIO_MULTICAST, SCHEMA_MULTICAST_CONFIG)
        self.coresys: CoreSys = coresys
        self.instance: DockerMulticast = DockerMulticast(coresys)

    @property
    def version(self) -> Optional[str]:
        """Return current version of Multicast."""
        return self._data.get(ATTR_VERSION)

    @version.setter
    def version(self, value: str) -> None:
        """Return current version of Multicast."""
        self._data[ATTR_VERSION] = value

    @property
    def image(self) -> str:
        """Return current image of Multicast."""
        if self._data.get(ATTR_IMAGE):
            return self._data[ATTR_IMAGE]
        return f"homeassistant/{self.sys_arch.supervisor}-hassio-multicast"

    @image.setter
    def image(self, value: str) -> None:
        """Return current image of Multicast."""
        self._data[ATTR_IMAGE] = value

    @property
    def latest_version(self) -> Optional[str]:
        """Return latest version of Multicast."""
        return self.sys_updater.version_multicast

    @property
    def in_progress(self) -> bool:
        """Return True if a task is in progress."""
        return self.instance.in_progress

    @property
    def need_update(self) -> bool:
        """Return True if an update is available."""
        return self.version != self.latest_version

    async def load(self) -> None:
        """Load multicast setup."""
        # Check Multicast state
        try:
            # Evaluate Version if we lost this information
            if not self.version:
                self.version = await self.instance.get_latest_version(key=int)

            await self.instance.attach(tag=self.version)
        except DockerAPIError:
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
            if await self.instance.is_running():
                await self.restart()
            else:
                await self.start()

    async def install(self) -> None:
        """Install Multicast."""
        _LOGGER.info("Setup Multicast plugin")
        while True:
            # read homeassistant tag and install it
            if not self.latest_version:
                await self.sys_updater.reload()

            if self.latest_version:
                with suppress(DockerAPIError):
                    await self.instance.install(
                        self.latest_version, image=self.sys_updater.image_multicast
                    )
                    break
            _LOGGER.warning("Error on install Multicast plugin. Retry in 30sec")
            await asyncio.sleep(30)

        _LOGGER.info("Multicast plugin now installed")
        self.version = self.instance.version
        self.image = self.sys_updater.image_multicast
        self.save_data()

    async def update(self, version: Optional[str] = None) -> None:
        """Update Multicast plugin."""
        version = version or self.latest_version
        old_image = self.image

        if version == self.version:
            _LOGGER.warning("Version %s is already installed for Multicast", version)
            return

        # Update
        try:
            await self.instance.update(version, image=self.sys_updater.image_multicast)
        except DockerAPIError:
            _LOGGER.error("Multicast update fails")
            raise MulticastUpdateError() from None
        else:
            self.version = version
            self.image = self.sys_updater.image_multicast
            self.save_data()

        # Cleanup
        with suppress(DockerAPIError):
            await self.instance.cleanup(old_image=old_image)

        # Start Multicast plugin
        await self.start()

    async def restart(self) -> None:
        """Restart Multicast plugin."""
        _LOGGER.info("Restart Multicast plugin")
        try:
            await self.instance.restart()
        except DockerAPIError:
            _LOGGER.error("Can't start Multicast plugin")
            raise MulticastError()

    async def start(self) -> None:
        """Run Multicast."""
        _LOGGER.info("Start Multicast plugin")
        try:
            await self.instance.run()
        except DockerAPIError:
            _LOGGER.error("Can't start Multicast plugin")
            raise MulticastError()

    async def stop(self) -> None:
        """Stop Multicast."""
        _LOGGER.info("Stop Multicast plugin")
        try:
            await self.instance.stop()
        except DockerAPIError:
            _LOGGER.error("Can't stop Multicast plugin")
            raise MulticastError()

    def logs(self) -> Awaitable[bytes]:
        """Get Multicast docker logs.

        Return Coroutine.
        """
        return self.instance.logs()

    async def stats(self) -> DockerStats:
        """Return stats of Multicast."""
        try:
            return await self.instance.stats()
        except DockerAPIError:
            raise MulticastError() from None

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

    async def repair(self) -> None:
        """Repair Multicast plugin."""
        if await self.instance.exists():
            return

        _LOGGER.info("Repair Multicast %s", self.version)
        try:
            await self.instance.install(self.version)
        except DockerAPIError:
            _LOGGER.error("Repairing of Multicast fails")
