"""Init file for HassIO addons."""
import logging

from .config import AddonsConfig
from .git import AddonsRepo
from ..docker.addon import DockerAddon

_LOGGER = logging.getLogger(__name__)


class AddonsManager(object):
    """Manage addons inside HassIO."""

    def __init__(self, config, loop, dock):
        """Initialize docker base wrapper."""
        self.config = config
        self.loop = loop
        self.dock = dock
        self.repo = AddonsRepo(config, loop)
        self.addons = AddonsConfig(config)
        self.dockers = {}

    async def prepare(self):
        """Startup addon management."""
        # load addon repository
        if await self.repo.load():
            self.addons.read_addons_repo()

    async def relaod_addons(self):
        """Update addons from repo and reload list."""
        if not await self.repo.pull():
            return
        self.addons.read_addons_repo()
