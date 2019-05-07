"""Add-on Store handler."""
import asyncio
import logging
from typing import Dict, List

from ..coresys import CoreSys, CoreSysAttributes
from ..const import REPOSITORY_CORE, REPOSITORY_LOCAL
from .addon import AddonStore
from .data import StoreData
from .repository import Repository

_LOGGER = logging.getLogger(__name__)

BUILTIN_REPOSITORIES = set((REPOSITORY_CORE, REPOSITORY_LOCAL))


class StoreManager(CoreSysAttributes):
    """Manage add-ons inside Hass.io."""

    def __init__(self, coresys: CoreSys):
        """Initialize Docker base wrapper."""
        self.coresys: CoreSys = coresys
        self.data = StoreData(coresys)
        self.repositories: Dict[str, Repository] = {}

    @property
    def all(self) -> List[Repository]:
        """Return list of add-on repositories."""
        return list(self.repositories.values())

    async def load(self) -> None:
        """Start up add-on management."""
        self.data.update()

        # Init Hass.io built-in repositories
        repositories = \
            set(self.sys_config.addons_repositories) | BUILTIN_REPOSITORIES

        # Init custom repositories and load add-ons
        await self.update_repositories(repositories)

    async def reload(self) -> None:
        """Update add-ons from repository and reload list."""
        tasks = [repository.update() for repository in
                 self.repositories.values()]
        if tasks:
            await asyncio.wait(tasks)

        # read data from repositories
        self.data.update()
        self._read_addons()

    async def update_repositories(self, list_repositories):
        """Add a new custom repository."""
        new_rep = set(list_repositories)
        old_rep = set(self.repositories)

        # add new repository
        async def _add_repository(url):
            """Helper function to async add repository."""
            repository = Repository(self.coresys, url)
            if not await repository.load():
                _LOGGER.error("Can't load from repository %s", url)
                return
            self.repositories[url] = repository

            # don't add built-in repository to config
            if url not in BUILTIN_REPOSITORIES:
                self.sys_config.add_addon_repository(url)

        tasks = [_add_repository(url) for url in new_rep - old_rep]
        if tasks:
            await asyncio.wait(tasks)

        # del new repository
        for url in old_rep - new_rep - BUILTIN_REPOSITORIES:
            self.repositories.pop(url).remove()
            self.sys_config.drop_addon_repository(url)

        # update data
        self.data.update()
        self._read_addons()

    def _read_addons(self) -> None:
        """Reload add-ons inside store."""
        all_addons = set(self.data.addons)

        # calc diff
        add_addons = all_addons - set(self.sys_addons.store)
        del_addons = set(self.sys_addons.store) - all_addons

        _LOGGER.info("Load add-ons from store: %d all - %d new - %d remove",
                     len(all_addons), len(add_addons), len(del_addons))

        # new addons
        for slug in add_addons:
            self.sys_addons.store[slug] = AddonStore(self.coresys, slug)

        # remove
        for slug in del_addons:
            self.sys_addons.store.pop(slug)
