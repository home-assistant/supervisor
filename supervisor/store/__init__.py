"""Add-on Store handler."""
import asyncio
import logging

from ..const import ATTR_REPOSITORIES, URL_HASSIO_ADDONS
from ..coresys import CoreSys, CoreSysAttributes
from ..exceptions import (
    StoreError,
    StoreGitCloneError,
    StoreGitError,
    StoreInvalidAddonRepo,
    StoreJobError,
    StoreNotFound,
)
from ..jobs.decorator import Job, JobCondition
from ..resolution.const import ContextType, IssueType, SuggestionType
from ..utils.common import FileConfiguration
from .addon import AddonStore
from .const import FILE_HASSIO_STORE, StoreType
from .data import StoreData
from .repository import Repository
from .validate import (
    BUILTIN_REPOSITORIES,
    SCHEMA_STORE_FILE,
    ensure_builtin_repositories,
)

_LOGGER: logging.Logger = logging.getLogger(__name__)


class StoreManager(CoreSysAttributes, FileConfiguration):
    """Manage add-ons inside Supervisor."""

    def __init__(self, coresys: CoreSys):
        """Initialize Docker base wrapper."""
        super().__init__(FILE_HASSIO_STORE, SCHEMA_STORE_FILE)
        self.coresys: CoreSys = coresys
        self.data = StoreData(coresys)
        self._repositories: dict[str, Repository] = {}

    @property
    def all(self) -> list[Repository]:
        """Return list of add-on repositories."""
        return list(self.repositories.values())

    @property
    def repositories(self) -> dict[str, Repository]:
        """Return repositories dictionary."""
        return self._repositories

    @property
    def repository_urls(self) -> list[str]:
        """Return source URL for all git repositories."""
        return [
            repository.source
            for repository in self.all
            if repository.type == StoreType.GIT
        ]

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
        await self.data.update()

        # Init custom repositories and load add-ons
        await self.update_repositories(
            self._data[ATTR_REPOSITORIES], add_with_errors=True
        )

    @Job(
        name="store_manager_reload",
        conditions=[JobCondition.SUPERVISOR_UPDATED],
        on_condition=StoreJobError,
    )
    async def reload(self) -> None:
        """Update add-ons from repository and reload list."""
        tasks = [self.sys_create_task(repository.update()) for repository in self.all]
        if tasks:
            await asyncio.wait(tasks)

        # read data from repositories
        await self.load()
        self._read_addons()

    @Job(
        name="store_manager_add_repository",
        conditions=[JobCondition.INTERNET_SYSTEM, JobCondition.SUPERVISOR_UPDATED],
        on_condition=StoreJobError,
    )
    async def add_repository(self, url: str, *, persist: bool = True) -> None:
        """Add a repository."""
        await self._add_repository(url, persist=persist, add_with_errors=False)

    async def _add_repository(
        self, url: str, *, persist: bool = True, add_with_errors: bool = False
    ) -> None:
        """Add a repository."""
        if url == URL_HASSIO_ADDONS:
            url = StoreType.CORE

        repository = Repository(self.coresys, url)

        if repository.slug in self.repositories:
            raise StoreError(f"Can't add {url}, already in the store", _LOGGER.error)

        # Load the repository
        try:
            await repository.load()
        except StoreGitCloneError as err:
            _LOGGER.error("Can't retrieve data from %s due to %s", url, err)
            if add_with_errors:
                self.sys_resolution.create_issue(
                    IssueType.FATAL_ERROR,
                    ContextType.STORE,
                    reference=repository.slug,
                    suggestions=[SuggestionType.EXECUTE_REMOVE],
                )
            else:
                await repository.remove()
                raise err

        except StoreGitError as err:
            _LOGGER.error("Can't load data from repository %s due to %s", url, err)
            if add_with_errors:
                self.sys_resolution.create_issue(
                    IssueType.FATAL_ERROR,
                    ContextType.STORE,
                    reference=repository.slug,
                    suggestions=[SuggestionType.EXECUTE_RESET],
                )
            else:
                await repository.remove()
                raise err

        except StoreJobError as err:
            _LOGGER.error("Can't add repository %s due to %s", url, err)
            if add_with_errors:
                self.sys_resolution.create_issue(
                    IssueType.FATAL_ERROR,
                    ContextType.STORE,
                    reference=repository.slug,
                    suggestions=[SuggestionType.EXECUTE_RELOAD],
                )
            else:
                await repository.remove()
                raise err

        else:
            if not repository.validate():
                if add_with_errors:
                    _LOGGER.error("%s is not a valid add-on repository", url)
                    self.sys_resolution.create_issue(
                        IssueType.CORRUPT_REPOSITORY,
                        ContextType.STORE,
                        reference=repository.slug,
                        suggestions=[SuggestionType.EXECUTE_REMOVE],
                    )
                else:
                    await repository.remove()
                    raise StoreInvalidAddonRepo(
                        f"{url} is not a valid add-on repository", logger=_LOGGER.error
                    )

        # Add Repository to list
        self.repositories[repository.slug] = repository

        # On start-up we add the saved repos to force a load. But they're already in data
        if url not in self._data[ATTR_REPOSITORIES]:
            self._data[ATTR_REPOSITORIES].append(url)
            self.save_data()

        # Persist changes
        if persist:
            await self.data.update()
            self._read_addons()

    async def remove_repository(self, repository: Repository, *, persist: bool = True):
        """Remove a repository."""
        if repository.source in BUILTIN_REPOSITORIES:
            raise StoreInvalidAddonRepo(
                "Can't remove built-in repositories!", logger=_LOGGER.error
            )

        if repository.slug in (addon.repository for addon in self.sys_addons.installed):
            raise StoreError(
                f"Can't remove '{repository.source}'. It's used by installed add-ons",
                logger=_LOGGER.error,
            )
        await self.repositories.pop(repository.slug).remove()
        self._data[ATTR_REPOSITORIES].remove(repository.source)
        self.save_data()

        if persist:
            await self.data.update()
            self._read_addons()

    @Job(name="store_manager_update_repositories")
    async def update_repositories(
        self,
        list_repositories: list[str],
        *,
        add_with_errors: bool = False,
        replace: bool = True,
    ):
        """Add a new custom repository."""
        new_rep = set(
            ensure_builtin_repositories(list_repositories)
            if replace
            else list_repositories + self.repository_urls
        )
        old_rep = {repository.source for repository in self.all}

        # Add new repositories
        add_errors = await asyncio.gather(
            *[
                self._add_repository(url, persist=False, add_with_errors=True)
                if add_with_errors
                else self.add_repository(url, persist=False)
                for url in new_rep - old_rep
            ],
            return_exceptions=True,
        )

        # Delete stale repositories
        remove_errors = await asyncio.gather(
            *[
                self.remove_repository(self.get_from_url(url), persist=False)
                for url in old_rep - new_rep - BUILTIN_REPOSITORIES
            ],
            return_exceptions=True,
        )

        # Always update data, even there are errors, some changes may have succeeded
        await self.data.update()
        self._read_addons()

        # Raise the first error we found (if any)
        for error in add_errors + remove_errors:
            if error:
                raise error

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
