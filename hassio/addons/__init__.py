"""Init file for HassIO addons."""
import asyncio
import logging

from .addon import Addon
from .repository import Repository
from .data import AddonsData
from ..const import REPOSITORY_CORE, REPOSITORY_LOCAL, BOOT_AUTO, STATE_STARTED
from ..coresys import CoreSysAttributes

_LOGGER = logging.getLogger(__name__)

BUILTIN_REPOSITORIES = set((REPOSITORY_CORE, REPOSITORY_LOCAL))


class AddonManager(CoreSysAttributes):
    """Manage addons inside HassIO."""

    def __init__(self, coresys):
        """Initialize docker base wrapper."""
        self.coresys = coresys
        self.data = AddonsData(coresys)
        self.addons_obj = {}
        self.repositories_obj = {}

    @property
    def list_addons(self):
        """Return a list of all addons."""
        return list(self.addons_obj.values())

    @property
    def list_installed(self):
        """Return a list of installed addons."""
        return [addon for addon in self.addons_obj.values()
                if addon.is_installed]

    @property
    def list_repositories(self):
        """Return list of addon repositories."""
        return list(self.repositories_obj.values())

    def get(self, addon_slug):
        """Return an add-on from slug."""
        return self.addons_obj.get(addon_slug)

    def from_uuid(self, uuid):
        """Return an add-on from uuid."""
        for addon in self.list_addons:
            if addon.is_installed and uuid == addon.uuid:
                return addon
        return None

    async def load(self):
        """Startup addon management."""
        self.data.reload()

        # init hassio built-in repositories
        repositories = \
            set(self.sys_config.addons_repositories) | BUILTIN_REPOSITORIES

        # init custom repositories & load addons
        await self.load_repositories(repositories)

    async def reload(self):
        """Update addons from repo and reload list."""
        tasks = [repository.update() for repository in
                 self.repositories_obj.values()]
        if tasks:
            await asyncio.wait(tasks)

        # read data from repositories
        self.data.reload()

        # update addons
        await self.load_addons()

    async def load_repositories(self, list_repositories):
        """Add a new custom repository."""
        new_rep = set(list_repositories)
        old_rep = set(self.repositories_obj)

        # add new repository
        async def _add_repository(url):
            """Helper function to async add repository."""
            repository = Repository(self.coresys, url)
            if not await repository.load():
                _LOGGER.error("Can't load from repository %s", url)
                return
            self.repositories_obj[url] = repository

            # don't add built-in repository to config
            if url not in BUILTIN_REPOSITORIES:
                self.sys_config.add_addon_repository(url)

        tasks = [_add_repository(url) for url in new_rep - old_rep]
        if tasks:
            await asyncio.wait(tasks)

        # del new repository
        for url in old_rep - new_rep - BUILTIN_REPOSITORIES:
            self.repositories_obj.pop(url).remove()
            self.sys_config.drop_addon_repository(url)

        # update data
        self.data.reload()
        await self.load_addons()

    async def load_addons(self):
        """Update/add internal addon store."""
        all_addons = set(self.data.system) | set(self.data.cache)

        # calc diff
        add_addons = all_addons - set(self.addons_obj)
        del_addons = set(self.addons_obj) - all_addons

        _LOGGER.info("Load addons: %d all - %d new - %d remove",
                     len(all_addons), len(add_addons), len(del_addons))

        # new addons
        tasks = []
        for addon_slug in add_addons:
            addon = Addon(self.coresys, addon_slug)

            tasks.append(addon.load())
            self.addons_obj[addon_slug] = addon

        if tasks:
            await asyncio.wait(tasks)

        # remove
        for addon_slug in del_addons:
            self.addons_obj.pop(addon_slug)

    async def boot(self, stage):
        """Boot addons with mode auto."""
        tasks = []
        for addon in self.addons_obj.values():
            if addon.is_installed and addon.boot == BOOT_AUTO and \
                    addon.startup == stage:
                tasks.append(addon.start())

        _LOGGER.info("Startup %s run %d addons", stage, len(tasks))
        if tasks:
            await asyncio.wait(tasks)
            await asyncio.sleep(self.sys_config.wait_boot)

    async def shutdown(self, stage):
        """Shutdown addons."""
        tasks = []
        for addon in self.addons_obj.values():
            if addon.is_installed and \
                    await addon.state() == STATE_STARTED and \
                    addon.startup == stage:
                tasks.append(addon.stop())

        _LOGGER.info("Shutdown %s stop %d addons", stage, len(tasks))
        if tasks:
            await asyncio.wait(tasks)
