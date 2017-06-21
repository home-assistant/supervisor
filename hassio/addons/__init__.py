"""Init file for HassIO addons."""
import asyncio
import logging

from .addon import Addon
from .repository import Repository
from .data import AddonsData
from ..const import (
    STATE_STOPPED, STATE_STARTED, REPOSITORY_CORE, REPOSITORY_LOCAL, BOOT_AUTO)

_LOGGER = logging.getLogger(__name__)


class AddonManager(AddonsData):
    """Manage addons inside HassIO."""

    def __init__(self, config, loop, dock):
        """Initialize docker base wrapper."""
        self.loop = loop
        self.dock = dock
        self.data = AddonsData(config)
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

    def get_addon(self, addon_slug):
        """Return a adddon from slug."""
        return self.addons.get(addon_slug)

    async def prepare(self, arch):
        """Startup addon management."""
        self.data.arch = self.arch

        # init hassio repositories
        repositories = set(self.config.addons_repositories) | \
            (REPOSITORY_CORE, REPOSITORY_LOCAL)

        # init custom repositories
        tasks = []
        for url in repositories:
            repository = Repository(self.config, self.loop, self.data, url)
            tasks.append(repository.load())

            self.repositories[url] = repository

        # load addon repository
        if tasks:
            await asyncio.wait(tasks, loop=self.loop)

        # init addons
        await self.load_addons()

    async def add_repository(self, url):
        """Add a new custom repository."""
        if url in self.config.addons_repositories:
            _LOGGER.warning("Repository already exists %s", url)
            return False

        repository = Repository(self.config, self.loop, self.data, url)

        if not await repository.load():
            _LOGGER.error("Can't load from repository %s", url)
            return False

        self.config.addons_repositories = url
        self.repositories[url] = repository
        return True

    def drop_repository(self, url):
        """Remove a custom repository."""
        if url not in self.repositories:
            _LOGGER.warning("Repository %s not found!", url)
            return False

        self.repositories.pop(url).remove()
        self.config.drop_addon_repository(url)
        return True

    async def reload(self):
        """Update addons from repo and reload list."""
        tasks = [repository.pull() for repository in self.repositories]
        if tasks:
            await asyncio.wait(tasks, loop=self.loop)

        # read data from repositories
        self.data.reload()

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
