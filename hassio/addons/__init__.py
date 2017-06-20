"""Init file for HassIO addons."""
import asyncio
import logging
import shutil

from .addon import Addon
from .data import AddonsData
from .git import AddonsRepoHassIO, AddonsRepoCustom
from ..const import STATE_STOPPED, STATE_STARTED
from ..dock.addon import DockerAddon

_LOGGER = logging.getLogger(__name__)


class AddonManager(AddonsData):
    """Manage addons inside HassIO."""

    def __init__(self, config, loop, dock):
        """Initialize docker base wrapper."""
        self.loop = loop
        self.dock = dock
        self.data = AddonsData(config)
        self.addons = {}
        self.repositories = []

    @property
    def list_addons(self):
        """Return a list of all addons."""
        return list(self.addons.values())

    @property
    def list_repositories(self):
        """Return list of addon repositories."""
        return list(self._data.repositories.values())

    async def prepare(self, arch):
        """Startup addon management."""
        self.arch = arch
        self.data.arch = self.arch

        # init hassio repository
        self._repositories.append(AddonsRepoHassIO(self.config, self.loop))

        # init custom repositories
        for url in self.config.addons_repositories:
            self._repositories.append(
                AddonsRepoCustom(self.config, self.loop, url))

        # load addon repository
        tasks = [repo.load() for repo in self._repositories]
        if tasks:
            await asyncio.wait(tasks, loop=self.loop)

            # read data from repositories
            self.data.read_data_from_repositories()
            self.data.merge_update_config()

        # init addons
        await self.load_addons()

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
        tasks = [repository.pull() for repository in self.repositories]
        if not tasks:
            return

        await asyncio.wait(tasks, loop=self.loop)

        # read data from repositories
        self.data.read_data_from_repositories()
        self.data.merge_update_config()

        # update addons
        await self.load_addons()

    async def load_addons(self):
        """Update/add internal addon store."""
        all_addons = set(self.data.system) | set(self.data.cache)

        # calc diff
        add_addons = all_addons - set(self.addons)
        del_addons = set(self.addons) - all_addons

        _LOGGER.info("Load addons: %d all - %d new - %d remove",
                     len(all_addons), len(add_addons), len(del_addons))

        # new addons
        tasks = []
        for addon_slug in add_addons:
            addon = Addon(
                self.conf, self.loop, self.dock, self.data, addon_slug)

            tasks.append(addon.load())
            self.addons[addon_slug] = addon

        if tasks:
            await asyncio.wait(tasks, loop=self.loop)

        # remove
        for addon_slug in del_addons:
            self.addons.pop(addon_slug)

    async def auto_boot(self, start_type):
        """Boot addons with mode auto."""
        tasks = []
        for addon in self.addons.values():
            if addon.is_installed and addon.boot == BOOT_AUTO and \
                    addon.startup == start_type:
                tasks.append(addon.start())

        _LOGGER.info("Startup %s run %d addons", start_type, len(tasks))
        if tasks:
            await asyncio.wait(tasks, loop=self.loop)
