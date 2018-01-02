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
    def version(self):
        """Return version of running homeassistant."""
        return self.instance.version

    @property
    def last_version(self):
        """Return last available version of homeassistant."""
        return self._updater.version_hassio

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

        if version == self._supervisor.version:
            _LOGGER.info("Version %s is already installed", version)
            return

        if await self.instance.install(version):
            self._loop.call_later(1, self._loop.stop)
        else:
            _LOGGER.error("Update of hass.io fails!")

    @property
    def in_progress(self):
        """Return True if a task is in progress."""
        return self.instance.in_progress
