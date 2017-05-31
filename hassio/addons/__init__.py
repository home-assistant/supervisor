"""Init file for HassIO addons."""
import asyncio
import logging
import shutil

from .data import AddonsData
from .git import AddonsRepoHassIO, AddonsRepoCustom
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
        self.repositories = []
        self.dockers = {}

    async def prepare(self, arch):
        """Startup addon management."""
        self.arch = arch

        # init hassio repository
        self.repositories.append(AddonsRepoHassIO(self.config, self.loop))

        # init custom repositories
        for url in self.config.addons_repositories:
            self.repositories.append(
                AddonsRepoCustom(self.config, self.loop, url))

        # load addon repository
        tasks = [addon.load() for addon in self.repositories]
        if tasks:
            await asyncio.wait(tasks, loop=self.loop)

            # read data from repositories
            self.read_data_from_repositories()
            self.merge_update_config()

        # load installed addons
        for addon in self.list_installed:
            self.dockers[addon] = DockerAddon(
                self.config, self.loop, self.dock, self, addon)
            await self.dockers[addon].attach()

    async def add_git_repository(self, url):
        """Add a new custom repository."""
        if url in self.config.addons_repositories:
            _LOGGER.warning("Repository already exists %s", url)
            return False

        repo = AddonsRepoCustom(self.config, self.loop, url)

        if not await repo.load():
            _LOGGER.error("Can't load from repository %s", url)
            return False

        self.config.addons_repositories = url
        self.repositories.append(repo)
        return True

    def drop_git_repository(self, url):
        """Remove a custom repository."""
        for repo in self.repositories:
            if repo.url == url:
                self.repositories.remove(repo)
                self.config.drop_addon_repository(url)
                repo.remove()
                return True

        return False

    async def reload(self):
        """Update addons from repo and reload list."""
        tasks = [addon.pull() for addon in self.repositories]
        if not tasks:
            return

        await asyncio.wait(tasks, loop=self.loop)

        # read data from repositories
        self.read_data_from_repositories()
        self.merge_update_config()

        # remove stalled addons
        for addon in self.list_detached:
            _LOGGER.warning("Dedicated addon '%s' found!", addon)

    async def auto_boot(self, start_type):
        """Boot addons with mode auto."""
        boot_list = self.list_startup(start_type)
        tasks = [self.start(addon) for addon in boot_list]

        _LOGGER.info("Startup %s run %d addons", start_type, len(tasks))
        if tasks:
            await asyncio.wait(tasks, loop=self.loop)

    async def install(self, addon, version=None):
        """Install a addon."""
        if not self.exists_addon(addon):
            _LOGGER.error("Addon %s not exists for install", addon)
            return False

        if self.arch not in self.get_arch(addon):
            _LOGGER.error("Addon %s not supported on %s", addon, self.arch)
            return False

        if self.is_installed(addon):
            _LOGGER.error("Addon %s is already installed", addon)
            return False

        if not self.path_data(addon).is_dir():
            _LOGGER.info("Create Home-Assistant addon data folder %s",
                         self.path_data(addon))
            self.path_data(addon).mkdir()

        addon_docker = DockerAddon(
            self.config, self.loop, self.dock, self, addon)

        version = version or self.get_last_version(addon)
        if not await addon_docker.install(version):
            return False

        self.dockers[addon] = addon_docker
        self.set_addon_install(addon, version)
        return True

    async def uninstall(self, addon):
        """Remove a addon."""
        if not self.is_installed(addon):
            _LOGGER.error("Addon %s is already uninstalled", addon)
            return False

        if addon not in self.dockers:
            _LOGGER.error("No docker found for addon %s", addon)
            return False

        if not await self.dockers[addon].remove():
            return False

        if self.path_data(addon).is_dir():
            _LOGGER.info("Remove Home-Assistant addon data folder %s",
                         self.path_data(addon))
            shutil.rmtree(str(self.path_data(addon)))

        self.dockers.pop(addon)
        self.set_addon_uninstall(addon)
        return True

    async def state(self, addon):
        """Return running state of addon."""
        if addon not in self.dockers:
            _LOGGER.error("No docker found for addon %s", addon)
            return

        if await self.dockers[addon].is_running():
            return STATE_STARTED
        return STATE_STOPPED

    async def start(self, addon):
        """Set options and start addon."""
        if addon not in self.dockers:
            _LOGGER.error("No docker found for addon %s", addon)
            return False

        if not self.write_addon_options(addon):
            _LOGGER.error("Can't write options for addon %s", addon)
            return False

        return await self.dockers[addon].run()

    async def stop(self, addon):
        """Stop addon."""
        if addon not in self.dockers:
            _LOGGER.error("No docker found for addon %s", addon)
            return False

        return await self.dockers[addon].stop()

    async def update(self, addon, version=None):
        """Update addon."""
        if addon not in self.dockers:
            _LOGGER.error("No docker found for addon %s", addon)
            return False

        version = version or self.get_last_version(addon)

        # update
        if not await self.dockers[addon].update(version):
            return False

        self.set_addon_update(addon, version)
        return True

    async def restart(self, addon):
        """Restart addon."""
        if addon not in self.dockers:
            _LOGGER.error("No docker found for addon %s", addon)
            return False

        if not self.write_addon_options(addon):
            _LOGGER.error("Can't write options for addon %s", addon)
            return False

        return await self.dockers[addon].restart()

    async def logs(self, addon):
        """Return addons log output."""
        if addon not in self.dockers:
            _LOGGER.error("No docker found for addon %s", addon)
            return False

        return await self.dockers[addon].logs()
