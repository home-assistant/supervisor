"""Add-on Store handler."""
import asyncio
import logging
from typing import Dict, List

from ..coresys import CoreSys, CoreSysAttributes
from ..exceptions import StoreGitError, StoreNotFound
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
        self.repositories: Dict[str, Repository] = {}

    @property
    def all(self) -> List[Repository]:
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

    @Job(conditions=[JobCondition.INTERNET_SYSTEM, JobCondition.FREE_SPACE])
    async def update_repositories(self, list_repositories):
        """Add a new custom repository."""
        job = self.sys_jobs.get_job("storemanager_update_repositories")
        new_rep = set(list_repositories)
        old_rep = {repository.source for repository in self.all}

        # add new repository
        async def _add_repository(url: str, step: int):
            """Add a repository."""
            job.update(progress=job.progress + step, stage=f"Checking {url} started")
            repository = Repository(self.coresys, url)

            # Load the repository
            try:
                await repository.load()
            except StoreGitError:
                _LOGGER.error("Can't load data from repository %s", url)
                self.sys_resolution.create_issue(
                    IssueType.CORRUPT_REPOSITORY,
                    ContextType.STORE,
                    reference=repository.slug,
                    suggestions=[SuggestionType.EXECUTE_REMOVE],
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

        job.update(progress=10, stage="Check repositories")
        repos = new_rep - old_rep
        tasks = [_add_repository(url, 80 / len(repos)) for url in repos]
        if tasks:
            await asyncio.wait(tasks)

        # Delete stale repositories
        for url in old_rep - new_rep - BUILTIN_REPOSITORIES:
            repository = self.get_from_url(url)
            await self.repositories.pop(repository.slug).remove()
            self.sys_config.drop_addon_repository(url)

        # update data
        job.update(progress=90, stage="Update addons")
        self.data.update()

        job.update(progress=95, stage="Read addons")
        self._read_addons()

        job.update(progress=100)

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
