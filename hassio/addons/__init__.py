"""Init file for HassIO addons."""
import asyncio
import logging

from .addon import Addon
from .repository import Repository
from .data import Data
from ..const import REPOSITORY_CORE, REPOSITORY_LOCAL, BOOT_AUTO

_LOGGER = logging.getLogger(__name__)


class AddonManager(object):
    """Manage addons inside HassIO."""

    def __init__(self, config, loop, dock):
        """Initialize docker base wrapper."""
        self.loop = loop
        self.config = config
        self.dock = dock
        self.data = Data(config)
        self.addons = {}
        self.repositories = {}

    @property
    def list_addons(self):
        """Return a list of all addons."""
        return list(self.addons.values())

    @property
    def list_repositories(self):
        """Return list of addon repositories."""
        return list(self.repositories.values())

    def get(self, addon_slug):
        """Return a adddon from slug."""
        return self.addons.get(addon_slug)

    async def prepare(self, arch):
        """Startup addon management."""
        self.data.arch = arch

        # read from repositories
        self.data.reload()

        # init hassio repositories
        repositories = set(self.config.addons_repositories) | \
            set((REPOSITORY_CORE, REPOSITORY_LOCAL))

        # init repositories & load addons
        await self.load_repositories(repositories)

    async def reload(self):
        """Update addons from repo and reload list."""
        tasks = [repository.update() for repository in
                 self.repositories.values()]
        if tasks:
            await asyncio.wait(tasks, loop=self.loop)

        # read data from repositories
        self.data.reload()

        # update addons
        await self.load_addons()

    async def load_repositories(self, list_repositories):
        """Add a new custom repository."""
        new_rep = set(list_repositories)
        old_rep = set(self.repositories)

        # add new repository
        async def _add_repository(url):
            """Helper function to async add repository."""
            repository = Repository(self.config, self.loop, self.data, url)
            if not await repository.load():
                _LOGGER.error("Can't load from repository %s", url)
                return

            self.config.addons_repositories = url
            self.repositories[url] = repository

        tasks = [_add_repository(url) for url in new_rep - old_rep]
        if tasks:
            await asyncio.wait(tasks, loop=self.loop)

        # del new repository
        for url in old_rep - new_rep:
            self.repositories.pop(url).remove()
            self.config.drop_addon_repository(url)

        # update data
        self.data.reload()
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
                self.config, self.loop, self.dock, self.data, addon_slug)

            tasks.append(addon.load())
            self.addons[addon_slug] = addon

        if tasks:
            await asyncio.wait(tasks, loop=self.loop)

        # remove
        for addon_slug in del_addons:
            self.addons.pop(addon_slug)

    async def auto_boot(self, stage):
        """Boot addons with mode auto."""
        tasks = []
        for addon in self.addons.values():
            if addon.is_installed and addon.boot == BOOT_AUTO and \
                    addon.startup == stage:
                tasks.append(addon.start())

        _LOGGER.info("Startup %s run %d addons", stage, len(tasks))
        if tasks:
            await asyncio.wait(tasks, loop=self.loop)
