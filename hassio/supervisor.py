"""Home Assistant control object."""
import asyncio
import logging
from pathlib import Path
from tempfile import TemporaryDirectory

import aiohttp

from .coresys import CoreSysAttributes
from .docker.supervisor import DockerSupervisor
from .const import URL_HASSIO_APPARMOR
from .exceptions import HostAppArmorError

_LOGGER = logging.getLogger(__name__)


class Supervisor(CoreSysAttributes):
    """Home Assistant core object for handle it."""

    def __init__(self, coresys):
        """Initialize hass object."""
        self.coresys = coresys
        self.instance = DockerSupervisor(coresys)

    async def load(self):
        """Prepare Home Assistant object."""
        if not await self.instance.attach():
            _LOGGER.fatal("Can't setup Supervisor Docker container!")
        await self.instance.cleanup()

    @property
    def need_update(self):
        """Return True if an update is available."""
        return self.version != self.last_version

    @property
    def version(self):
        """Return version of running Home Assistant."""
        return self.instance.version

    @property
    def last_version(self):
        """Return last available version of Home Assistant."""
        return self.sys_updater.version_hassio

    @property
    def image(self):
        """Return image name of Home Assistant container."""
        return self.instance.image

    @property
    def arch(self):
        """Return arch of the Hass.io container."""
        return self.instance.arch

    async def update_apparmor(self):
        """Fetch last version and update profile."""
        url = URL_HASSIO_APPARMOR
        try:
            _LOGGER.info("Fetch AppArmor profile %s", url)
            async with self.sys_websession.get(url, timeout=10) as request:
                data = await request.text()

        except (aiohttp.ClientError, asyncio.TimeoutError) as err:
            _LOGGER.warning("Can't fetch AppArmor profile: %s", err)
            return

        with TemporaryDirectory(dir=self.sys_config.path_tmp) as tmp_dir:
            profile_file = Path(tmp_dir, 'apparmor.txt')
            try:
                profile_file.write_text(data)
            except OSError as err:
                _LOGGER.error("Can't write temporary profile: %s", err)
                return
            try:
                await self.sys_host.apparmor.load_profile(
                    "hassio-supervisor", profile_file)
            except HostAppArmorError:
                _LOGGER.error("Can't update AppArmor profile!")

    async def update(self, version=None):
        """Update Home Assistant version."""
        version = version or self.last_version

        if version == self.sys_supervisor.version:
            _LOGGER.warning("Version %s is already installed", version)
            return

        _LOGGER.info("Update Supervisor to version %s", version)
        if await self.instance.install(version):
            await self.update_apparmor()
            self.sys_loop.call_later(1, self.sys_loop.stop)
            return True

        _LOGGER.error("Update of Hass.io fails!")
        return False

    @property
    def in_progress(self):
        """Return True if a task is in progress."""
        return self.instance.in_progress

    def logs(self):
        """Get Supervisor docker logs.

        Return a coroutine.
        """
        return self.instance.logs()

    def stats(self):
        """Return stats of Supervisor.

        Return a coroutine.
        """
        return self.instance.stats()
