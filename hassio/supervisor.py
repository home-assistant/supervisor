"""HomeAssistant control object."""
import logging

from .coresys import CoreSysAttributes
from .docker.supervisor import DockerSupervisor

_LOGGER = logging.getLogger(__name__)


class Supervisor(CoreSysAttributes):
    """Hass core object for handle it."""

    def __init__(self, coresys):
        """Initialize hass object."""
        self.coresys = coresys
        self.instance = DockerSupervisor(coresys)

    async def load(self):
        """Prepare HomeAssistant object."""
        if not await self.instance.attach():
            _LOGGER.fatal("Can't setup supervisor docker container!")
        await self.instance.cleanup()

    @property
    def need_update(self):
        """Return True if an update is available."""
        return self.version != self.last_version

    @property
    def version(self):
        """Return version of running homeassistant."""
        return self.instance.version

    @property
    def last_version(self):
        """Return last available version of homeassistant."""
        return self.sys_updater.version_hassio

    @property
    def image(self):
        """Return image name of hass containter."""
        return self.instance.image

    @property
    def arch(self):
        """Return arch of hass.io containter."""
        return self.instance.arch

    async def update(self, version=None):
        """Update HomeAssistant version."""
        version = version or self.last_version

        if version == self.sys_supervisor.version:
            _LOGGER.warning("Version %s is already installed", version)
            return

        _LOGGER.info("Update supervisor to version %s", version)
        if await self.instance.install(version):
            self.sys_loop.call_later(1, self.sys_loop.stop)
            return True

        _LOGGER.error("Update of hass.io fails!")
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
