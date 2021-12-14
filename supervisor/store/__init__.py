"""Add-on Store handler."""
import asyncio
import logging

from ..const import URL_HASSIO_ADDONS
from ..coresys import CoreSys, CoreSysAttributes
from ..exceptions import StoreError, StoreGitError, StoreJobError, StoreNotFound
from ..jobs.decorator import Job, JobCondition
from ..resolution.const import ContextType, IssueType, SuggestionType
from .addon import AddonStore
from .const import StoreType
from .data import StoreData
from .repository import Repository

_LOGGER: logging.Logger = logging.getLogger(__name__)

BUILTIN_REPOSITORIES = {StoreType.CORE.value, StoreType.LOCAL.value}


class StoreManager(CoreSysAttributes):
    """Manage add-ons inside Supervisor."""

    def __init__(self, coresys: CoreSys):
        """Initialize Docker base wrapper."""
        self.coresys: CoreSys = coresys
        self.data = StoreData(coresys)
        self.repositories: dict[str, Repository] = {}

    @property
    def all(self) -> list[Repository]:
        """Return list of add-on repositories."""
        return list(self.repositories.values())

    def get(self, slug: str) -> Repository:
        """Return Repository with slug."""
        if slug not in self.repositories:
            raise StoreNotFound()
        return self.repositories[slug]

    def get_from_url(self, url: str) -> Repository:
        """Return Repository with slug."""
        for repository in self.all:
            if repository.source != url:
                continue
            return repository
        raise StoreNotFound()

    async def load(self) -> None:
        """Start up add-on management."""
        self.data.update()

        # Init Supervisor built-in repositories
        repositories = set(self.sys_config.addons_repositories) | BUILTIN_REPOSITORIES

        # Init custom repositories and load add-ons
        await self.update_repositories(repositories)

    async def reload(self) -> None:
        """Update add-ons from repository and reload list."""
        tasks = [repository.update() for repository in self.all]
        if tasks:
            await asyncio.wait(tasks)

        # read data from repositories
        await self.load()
        self._read_addons()

    @Job(conditions=[JobCondition.INTERNET_SYSTEM])
    async def update_repositories(self, list_repositories):
        """Add a new custom repository."""
        new_rep = set(list_repositories)
        old_rep = {repository.source for repository in self.all}

        # add new repository
        async def _add_repository(url: str):
            """Add a repository."""
            if url == URL_HASSIO_ADDONS:
                url = StoreType.CORE

            repository = Repository(self.coresys, url)

            # Load the repository
            try:
                await repository.load()
            except StoreGitError:
                _LOGGER.error("Can't load data from repository %s", url)
            except StoreJobError:
                _LOGGER.warning("Skip update to later for %s", repository.slug)
                self.sys_resolution.create_issue(
                    IssueType.FATAL_ERROR,
                    ContextType.STORE,
                    reference=repository.slug,
                    suggestions=[SuggestionType.EXECUTE_RELOAD],
                )
            else:
                if not repository.validate():
                    _LOGGER.error("%s is not a valid add-on repository", url)
                    self.sys_resolution.create_issue(
                        IssueType.CORRUPT_REPOSITORY,
                        ContextType.STORE,
                        reference=repository.slug,
                        suggestions=[SuggestionType.EXECUTE_REMOVE],
                    )

            # Add Repository to list
            if repository.type == StoreType.GIT:
                self.sys_config.add_addon_repository(repository.source)
            self.repositories[repository.slug] = repository

        repos = new_rep - old_rep
        tasks = [self.sys_create_task(_add_repository(url)) for url in repos]
        if tasks:
            await asyncio.wait(tasks)

        # Delete stale repositories
        for url in old_rep - new_rep - BUILTIN_REPOSITORIES:
            repository = self.get_from_url(url)
            if repository.slug in (
                addon.repository for addon in self.sys_addons.installed
            ):
                raise StoreError(
                    f"Can't remove '{repository.source}'. It's used by installed add-ons",
                    logger=_LOGGER.error,
                )
            await self.repositories.pop(repository.slug).remove()
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

        _LOGGER.info(
            "Loading add-ons from store: %d all - %d new - %d remove",
            len(all_addons),
            len(add_addons),
            len(del_addons),
        )

        # new addons
        for slug in add_addons:
            self.sys_addons.store[slug] = AddonStore(self.coresys, slug)

        # remove
        for slug in del_addons:
            self.sys_addons.store.pop(slug)
