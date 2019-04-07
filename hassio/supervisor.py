"""Home Assistant control object."""
import asyncio
from contextlib import suppress
from ipaddress import IPv4Address
import logging
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Awaitable, Optional

import aiohttp

from .const import URL_HASSIO_APPARMOR
from .coresys import CoreSys, CoreSysAttributes
from .docker.stats import DockerStats
from .docker.supervisor import DockerSupervisor
from .exceptions import (
    DockerAPIError,
    HostAppArmorError,
    SupervisorError,
    SupervisorUpdateError,
)

_LOGGER = logging.getLogger(__name__)


class Supervisor(CoreSysAttributes):
    """Home Assistant core object for handle it."""

    def __init__(self, coresys: CoreSys):
        """Initialize hass object."""
        self.coresys: CoreSys = coresys
        self.instance: DockerSupervisor = DockerSupervisor(coresys)

    async def load(self) -> None:
        """Prepare Home Assistant object."""
        try:
            await self.instance.attach()
        except DockerAPIError:
            _LOGGER.fatal("Can't setup Supervisor Docker container!")

        with suppress(DockerAPIError):
            await self.instance.cleanup()

    @property
    def ip_address(self) -> IPv4Address:
        """Return IP of Supervisor instance."""
        return self.instance.ip_address

    @property
    def need_update(self) -> bool:
        """Return True if an update is available."""
        return self.version != self.latest_version

    @property
    def version(self) -> str:
        """Return version of running Home Assistant."""
        return self.instance.version

    @property
    def latest_version(self) -> str:
        """Return last available version of Home Assistant."""
        return self.sys_updater.version_hassio

    @property
    def image(self) -> str:
        """Return image name of Home Assistant container."""
        return self.instance.image

    @property
    def arch(self) -> str:
        """Return arch of the Hass.io container."""
        return self.instance.arch

    async def update_apparmor(self) -> None:
        """Fetch last version and update profile."""
        url = URL_HASSIO_APPARMOR
        try:
            _LOGGER.info("Fetch AppArmor profile %s", url)
            async with self.sys_websession.get(url, timeout=10) as request:
                data = await request.text()

        except (aiohttp.ClientError, asyncio.TimeoutError) as err:
            _LOGGER.warning("Can't fetch AppArmor profile: %s", err)
            raise SupervisorError() from None

        with TemporaryDirectory(dir=self.sys_config.path_tmp) as tmp_dir:
            profile_file = Path(tmp_dir, "apparmor.txt")
            try:
                profile_file.write_text(data)
            except OSError as err:
                _LOGGER.error("Can't write temporary profile: %s", err)
                raise SupervisorError() from None

            try:
                await self.sys_host.apparmor.load_profile(
                    "hassio-supervisor", profile_file
                )
            except HostAppArmorError:
                _LOGGER.error("Can't update AppArmor profile!")
                raise SupervisorError() from None

    async def update(self, version: Optional[str] = None) -> None:
        """Update Home Assistant version."""
        version = version or self.latest_version

        if version == self.sys_supervisor.version:
            _LOGGER.warning("Version %s is already installed", version)
            return

        _LOGGER.info("Update Supervisor to version %s", version)
        try:
            await self.instance.install(version)
        except DockerAPIError:
            _LOGGER.error("Update of Hass.io fails!")
            raise SupervisorUpdateError() from None

        with suppress(SupervisorError):
            await self.update_apparmor()
        self.sys_loop.call_later(1, self.sys_loop.stop)

    @property
    def in_progress(self) -> bool:
        """Return True if a task is in progress."""
        return self.instance.in_progress

    def logs(self) -> Awaitable[bytes]:
        """Get Supervisor docker logs.

        Return Coroutine.
        """
        return self.instance.logs()

    async def stats(self) -> DockerStats:
        """Return stats of Supervisor."""
        try:
            return await self.instance.stats()
        except DockerAPIError:
            raise SupervisorError() from None
