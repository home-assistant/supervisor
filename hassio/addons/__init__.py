"""Init file for HassIO addons."""
import logging
import os
import shutil

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

        # load installed addons
        for addon in self.addons.list_installed:
            self.dockers[addon] = DockerAddon(
                self.config, self.loop, self.dock, self.addons, addon)

    async def relaod_addons(self):
        """Update addons from repo and reload list."""
        if not await self.repo.pull():
            return
        self.addons.read_addons_repo()

    async def install_addon(self, addon, version=None):
        """Install a addon."""
        if not self.addons.exists_addon(addon):
            _LOGGER.error("Addon %s not exists for install.", addon)
            return False

        if self.addons.is_installed(addon):
            _LOGGER.error("Addon %s is allready installed.", addon)
            return False

        if not os.path.isdir(self.addons.path_data(addon)):
            _LOGGER.info("Create Home-Assistant addon data folder %s",
                         self.addon.path_data(addon))
            os.mkdir(self.addons.path_data(addon))

        addon_docker = DockerAddon(
            self.config, self.loop, self.dock, self.addons, addon)

        version = version or self.addons.get_version(addon)
        if not await addon_docker.install(version):
            _LOGGER.error("Can't install addon %s version %s.", addon, version)
            return False

        self.dockers[addon] = addon_docker
        self.addons.set_install_addon(addon, version)
        return True

    async def uninstall_addon(self, addon):
        """Remove a addon."""
        if self.addons.is_installed(addon):
            _LOGGER.error("Addon %s is allready installed.", addon)
            return False

        if addon not in self.dockers:
            _LOGGER.error("No docker found for addon %s.", addon)
            return False

        if not await self.dockers[addon].remove(version):
            _LOGGER.error("Can't install addon %s.", addon)
            return False

        if os.path.isdir(self.addons.path_data(addon)):
            _LOGGER.info("Remove Home-Assistant addon data folder %s",
                         self.addon.path_data(addon))
            shutil.rmtree(self.addons.path_data(addon))

        self.dockers.pop(addon)
        self.addons.set_uninstall_addon(addon)
        return True
