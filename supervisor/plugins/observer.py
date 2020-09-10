"""Home Assistant observer plugin.

Code: https://github.com/home-assistant/plugin-observer
"""
import asyncio
from contextlib import suppress
import logging
import secrets
from typing import Awaitable, Optional

from ..const import ATTR_ACCESS_TOKEN, ATTR_IMAGE, ATTR_VERSION
from ..coresys import CoreSys, CoreSysAttributes
from ..docker.observer import DockerObserver
from ..docker.stats import DockerStats
from ..exceptions import DockerAPIError, observerError, observerUpdateError
from ..utils.json import JsonConfig
from .const import FILE_HASSIO_OBSERVER
from .validate import SCHEMA_OBSERVER_CONFIG

_LOGGER: logging.Logger = logging.getLogger(__name__)


class Observer(CoreSysAttributes, JsonConfig):
    """Supervisor observer instance."""

    def __init__(self, coresys: CoreSys):
        """Initialize observer handler."""
        super().__init__(FILE_HASSIO_OBSERVER, SCHEMA_OBSERVER_CONFIG)
        self.coresys: CoreSys = coresys
        self.instance: DockerObserver = DockerObserver(coresys)

    @property
    def version(self) -> Optional[str]:
        """Return version of observer."""
        return self._data.get(ATTR_VERSION)

    @version.setter
    def version(self, value: str) -> None:
        """Set current version of observer."""
        self._data[ATTR_VERSION] = value

    @property
    def image(self) -> str:
        """Return current image of observer."""
        if self._data.get(ATTR_IMAGE):
            return self._data[ATTR_IMAGE]
        return f"homeassistant/{self.sys_arch.supervisor}-hassio-observer"

    @image.setter
    def image(self, value: str) -> None:
        """Return current image of observer."""
        self._data[ATTR_IMAGE] = value

    @property
    def latest_version(self) -> str:
        """Return version of latest observer."""
        return self.sys_updater.version_observer

    @property
    def need_update(self) -> bool:
        """Return true if a observer update is available."""
        return self.version != self.latest_version

    @property
    def access_token(self) -> str:
        """Return an access token for the Observer API."""
        return self._data.get(ATTR_ACCESS_TOKEN)

    @property
    def in_progress(self) -> bool:
        """Return True if a task is in progress."""
        return self.instance.in_progress

    async def load(self) -> None:
        """Load observer setup."""
        # Check observer state
        try:
            # Evaluate Version if we lost this information
            if not self.version:
                self.version = await self.instance.get_latest_version()

            await self.instance.attach(tag=self.version)
        except DockerAPIError:
            _LOGGER.info(
                "No observer plugin Docker image %s found.", self.instance.image
            )

            # Install observer
            with suppress(observerError):
                await self.install()
        else:
            self.version = self.instance.version
            self.image = self.instance.image
            self.save_data()

        # Run Observer
        with suppress(observerError):
            if not await self.instance.is_running():
                await self.start()

    async def install(self) -> None:
        """Install observer."""
        _LOGGER.info("Setup observer plugin")
        while True:
            # read audio tag and install it
            if not self.latest_version:
                await self.sys_updater.reload()

            if self.latest_version:
                with suppress(DockerAPIError):
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

    async def update(self, version: Optional[str] = None) -> None:
        """Update local HA observer."""
        version = version or self.latest_version
        old_image = self.image

        if version == self.version:
            _LOGGER.warning("Version %s is already installed for observer", version)
            return

        try:
            await self.instance.update(version, image=self.sys_updater.image_observer)
        except DockerAPIError as err:
            _LOGGER.error("HA observer update failed")
            raise observerUpdateError() from err
        else:
            self.version = version
            self.image = self.sys_updater.image_observer
            self.save_data()

        # Cleanup
        with suppress(DockerAPIError):
            await self.instance.cleanup(old_image=old_image)

        # Start observer
        await self.start()

    async def start(self) -> None:
        """Run observer."""
        # Create new API token
        if not self.access_token:
            self._data[ATTR_ACCESS_TOKEN] = secrets.token_hex(56)
            self.save_data()

        # Start Instance
        _LOGGER.info("Start observer plugin")
        try:
            await self.instance.run()
        except DockerAPIError as err:
            _LOGGER.error("Can't start observer plugin")
            raise observerError() from err

    async def stop(self) -> None:
        """Stop observer."""
        _LOGGER.info("Stop observer plugin")
        try:
            await self.instance.stop()
        except DockerAPIError as err:
            _LOGGER.error("Can't stop observer plugin")
            raise observerError() from err

    async def stats(self) -> DockerStats:
        """Return stats of observer."""
        try:
            return await self.instance.stats()
        except DockerAPIError as err:
            raise observerError() from err

    def is_running(self) -> Awaitable[bool]:
        """Return True if Docker container is running.

        Return a coroutine.
        """
        return self.instance.is_running()

    async def repair(self) -> None:
        """Repair observer container."""
        if await self.instance.exists():
            return

        _LOGGER.info("Repair HA observer %s", self.version)
        try:
            await self.instance.install(self.version)
        except DockerAPIError:
            _LOGGER.error("Repairing of HA observer failed")
