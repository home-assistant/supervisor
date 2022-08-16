"""Home Assistant observer plugin.

Code: https://github.com/home-assistant/plugin-observer
"""
import asyncio
from contextlib import suppress
import logging
import secrets

import aiohttp
from awesomeversion import AwesomeVersion

from ..const import ATTR_ACCESS_TOKEN
from ..coresys import CoreSys
from ..docker.const import ContainerState
from ..docker.observer import DockerObserver
from ..docker.stats import DockerStats
from ..exceptions import (
    DockerError,
    ObserverError,
    ObserverJobError,
    ObserverUpdateError,
)
from ..jobs.const import JobExecutionLimit
from ..jobs.decorator import Job
from .base import PluginBase
from .const import (
    FILE_HASSIO_OBSERVER,
    PLUGIN_UPDATE_CONDITIONS,
    WATCHDOG_THROTTLE_MAX_CALLS,
    WATCHDOG_THROTTLE_PERIOD,
)
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
    def latest_version(self) -> AwesomeVersion | None:
        """Return version of latest observer."""
        return self.sys_updater.version_observer

    @property
    def supervisor_token(self) -> str:
        """Return an access token for the Observer API."""
        return self._data.get(ATTR_ACCESS_TOKEN)

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

    @Job(
        conditions=PLUGIN_UPDATE_CONDITIONS,
        on_condition=ObserverJobError,
    )
    async def update(self, version: AwesomeVersion | None = None) -> None:
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

    @Job(
        limit=JobExecutionLimit.THROTTLE_RATE_LIMIT,
        throttle_period=WATCHDOG_THROTTLE_PERIOD,
        throttle_max_calls=WATCHDOG_THROTTLE_MAX_CALLS,
        on_condition=ObserverJobError,
    )
    async def _restart_after_problem(self, state: ContainerState):
        """Restart unhealthy or failed plugin."""
        return await super()._restart_after_problem(state)
