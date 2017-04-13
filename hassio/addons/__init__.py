"""Init file for HassIO addons."""
import logging
import os
import shutil

from .data import AddonsData
from .git import AddonsRepo
from ..const import STATE_STOPPED, STATE_STARTED
from ..dock.addon import DockerAddon

_LOGGER = logging.getLogger(__name__)


class AddonManager(AddonsData):
    """Manage addons inside HassIO."""

    def __init__(self, config, loop, dock):
        """Initialize docker base wrapper."""
        super().__init__(config)

        self.loop = loop
        self.dock = dock
        self.repo = AddonsRepo(config, loop)
        self.dockers = {}

    async def prepare(self):
        """Startup addon management."""
        # load addon repository
        if await self.repo.load():
            self.read_addons_repo()

        # load installed addons
        for addon in self.list_installed:
            self.dockers[addon] = DockerAddon(
                self.config, self.loop, self.dock, self, addon)

    async def relaod(self):
        """Update addons from repo and reload list."""
        if not await self.repo.pull():
            return
        self.read_addons_repo()

        # remove stalled addons
        tasks = []
        for addon in self.list_removed:
            _LOGGER.info("Old addon %s found")
            tasks.append(self.loop.create_task(self.dockers[addon].remove()))

        if tasks:
            await asyncio.wait(tasks, loop=self.loop)

    async def auto_boot(self, start_type):
        """Boot addons with mode auto."""
        boot_list = self.list_startup(start_type)
        tasks = []

        for addon in boot_list:
            tasks.append(self.loop.create_task(self.start_addon(addon)))

        _LOGGER.info("Startup %s run %d addons", start_type, len(tasks))
        if tasks:
            await asyncio.wait(tasks, loop=self.loop)

    async def install_addon(self, addon, version=None):
        """Install a addon."""
        if not self.exists_addon(addon):
            _LOGGER.error("Addon %s not exists for install", addon)
            return False

        if self.is_installed(addon):
            _LOGGER.error("Addon %s is already installed", addon)
            return False

        if not os.path.isdir(self.path_data(addon)):
            _LOGGER.info("Create Home-Assistant addon data folder %s",
                         self.path_data(addon))
            os.mkdir(self.path_data(addon))

        addon_docker = DockerAddon(
            self.config, self.loop, self.dock, self, addon)

        version = version or self.get_version(addon)
        if not await addon_docker.install(version):
            return False

        self.dockers[addon] = addon_docker
        self.set_install_addon(addon, version)
        return True

    async def uninstall_addon(self, addon):
        """Remove a addon."""
        if not self.is_installed(addon):
            _LOGGER.error("Addon %s is already uninstalled", addon)
            return False

        if addon not in self.dockers:
            _LOGGER.error("No docker found for addon %s", addon)
            return False

        if not await self.dockers[addon].remove():
            return False

        if os.path.isdir(self.path_data(addon)):
            _LOGGER.info("Remove Home-Assistant addon data folder %s",
                         self.path_data(addon))
            shutil.rmtree(self.path_data(addon))

        self.dockers.pop(addon)
        self.set_uninstall_addon(addon)
        return True

    async def state_addon(self, addon):
        """Return running state of addon."""
        if addon not in self.dockers:
            _LOGGER.error("No docker found for addon %s", addon)
            return

        if await self.dockers[addon].is_running():
            return STATE_STARTED
        return STATE_STOPPED

    async def start_addon(self, addon):
        """Set options and start addon."""
        if addon not in self.dockers:
            _LOGGER.error("No docker found for addon %s", addon)
            return False

        if not self.write_addon_options(addon):
            _LOGGER.error("Can't write options for addon %s", addon)
            return False

        return await self.dockers[addon].run()

    async def stop_addon(self, addon):
        """Stop addon."""
        if addon not in self.dockers:
            _LOGGER.error("No docker found for addon %s", addon)
            return False

        return await self.dockers[addon].stop()

    async def update_addon(self, addon, version=None):
        """Update addon."""
        if self.is_installed(addon):
            _LOGGER.error("Addon %s is not installed", addon)
            return False

        if addon not in self.dockers:
            _LOGGER.error("No docker found for addon %s", addon)
            return False

        version = version or self.get_version(addon)
        return await self.dockers[addon].update(version)
