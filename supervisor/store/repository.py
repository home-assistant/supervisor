"""Represent a Supervisor repository."""

from __future__ import annotations

from abc import ABC, abstractmethod
import logging
from pathlib import Path

import voluptuous as vol

from supervisor.utils import get_latest_mtime

from ..const import ATTR_MAINTAINER, ATTR_NAME, ATTR_URL, FILE_SUFFIX_CONFIGURATION
from ..coresys import CoreSys, CoreSysAttributes
from ..exceptions import ConfigurationFileError, StoreError
from ..utils.common import read_json_or_yaml_file
from .const import StoreType
from .git import GitRepo
from .utils import get_hash_from_repository
from .validate import SCHEMA_REPOSITORY_CONFIG, BuiltinRepository

_LOGGER: logging.Logger = logging.getLogger(__name__)
UNKNOWN = "unknown"


class Repository(CoreSysAttributes, ABC):
    """Add-on store repository in Supervisor."""

    def __init__(self, coresys: CoreSys, repository: str):
        """Initialize add-on store repository object."""
        self._slug: str
        self._type: StoreType
        self.coresys: CoreSys = coresys
        self.source: str = repository

    @staticmethod
    def create(coresys: CoreSys, repository: str) -> Repository:
        """Create a repository instance."""
        if repository == StoreType.LOCAL:
            return RepositoryLocal(coresys)
        if repository in BuiltinRepository:
            return RepositoryGitBuiltin(coresys, BuiltinRepository(repository))
        return RepositoryCustom(coresys, repository)

    def __repr__(self) -> str:
        """Return internal representation."""
        return f"<Store.Repository: {self.slug} / {self.source}>"

    @property
    def slug(self) -> str:
        """Return repo slug."""
        return self._slug

    @property
    def type(self) -> StoreType:
        """Return type of the store."""
        return self._type

    @property
    def data(self) -> dict:
        """Return data struct repository."""
        return self.sys_store.data.repositories.get(self.slug, {})

    @property
    def name(self) -> str:
        """Return name of repository."""
        return self.data.get(ATTR_NAME, UNKNOWN)

    @property
    def url(self) -> str:
        """Return URL of repository."""
        return self.data.get(ATTR_URL, self.source)

    @property
    def maintainer(self) -> str:
        """Return url of repository."""
        return self.data.get(ATTR_MAINTAINER, UNKNOWN)

    @abstractmethod
    async def validate(self) -> bool:
        """Check if store is valid."""

    @abstractmethod
    async def load(self) -> None:
        """Load addon repository."""

    @abstractmethod
    async def update(self) -> bool:
        """Update add-on repository.

        Returns True if the repository was updated.
        """

    @abstractmethod
    async def remove(self) -> None:
        """Remove add-on repository."""

    @abstractmethod
    async def reset(self) -> None:
        """Reset add-on repository to fix corruption issue with files."""


class RepositoryBuiltin(Repository, ABC):
    """A built-in add-on repository."""

    def __init__(self, coresys: CoreSys, builtin: BuiltinRepository) -> None:
        """Initialize object."""
        super().__init__(coresys, builtin.value)
        self._builtin = builtin
        self._slug = builtin.id
        self._type = builtin.type

    async def validate(self) -> bool:
        """Assume built-in repositories are always valid."""
        return True

    async def remove(self) -> None:
        """Raise. Not supported for built-in repositories."""
        raise StoreError("Can't remove built-in repositories!", _LOGGER.error)


class RepositoryGit(Repository, ABC):
    """A git based add-on repository."""

    _git: GitRepo

    async def load(self) -> None:
        """Load addon repository."""
        await self._git.load()

    async def update(self) -> bool:
        """Update add-on repository.

        Returns True if the repository was updated.
        """
        if not await self.validate():
            return False

        return await self._git.pull()

    async def validate(self) -> bool:
        """Check if store is valid."""

        def validate_file() -> bool:
            # If exists?
            for filetype in FILE_SUFFIX_CONFIGURATION:
                repository_file = Path(self._git.path / f"repository{filetype}")
                if repository_file.exists():
                    break

            if not repository_file.exists():
                return False

            # If valid?
            try:
                SCHEMA_REPOSITORY_CONFIG(read_json_or_yaml_file(repository_file))
            except (ConfigurationFileError, vol.Invalid) as err:
                _LOGGER.warning("Could not validate repository configuration %s", err)
                return False

            return True

        return await self.sys_run_in_executor(validate_file)

    async def reset(self) -> None:
        """Reset add-on repository to fix corruption issue with files."""
        await self._git.reset()
        await self.load()


class RepositoryLocal(RepositoryBuiltin):
    """A local add-on repository."""

    def __init__(self, coresys: CoreSys) -> None:
        """Initialize object."""
        super().__init__(coresys, BuiltinRepository.LOCAL)
        self._latest_mtime: float | None = None

    async def load(self) -> None:
        """Load addon repository."""
        self._latest_mtime, _ = await self.sys_run_in_executor(
            get_latest_mtime, self.sys_config.path_addons_local
        )

    async def update(self) -> bool:
        """Update add-on repository.

        Returns True if the repository was updated.
        """
        # Check local modifications
        latest_mtime, modified_path = await self.sys_run_in_executor(
            get_latest_mtime, self.sys_config.path_addons_local
        )
        if self._latest_mtime != latest_mtime:
            _LOGGER.debug(
                "Local modifications detected in %s repository: %s",
                self.slug,
                modified_path,
            )
            self._latest_mtime = latest_mtime
            return True

        return False

    async def reset(self) -> None:
        """Raise. Not supported for local repository."""
        raise StoreError(
            "Can't reset local repository as it is not git based!", _LOGGER.error
        )


class RepositoryGitBuiltin(RepositoryBuiltin, RepositoryGit):
    """A built-in add-on repository based on git."""

    def __init__(self, coresys: CoreSys, builtin: BuiltinRepository) -> None:
        """Initialize object."""
        super().__init__(coresys, builtin)
        self._git = GitRepo(coresys, builtin.get_path(coresys), builtin.url)


class RepositoryCustom(RepositoryGit):
    """A custom add-on repository."""

    def __init__(self, coresys: CoreSys, url: str) -> None:
        """Initialize object."""
        super().__init__(coresys, url)
        self._slug = get_hash_from_repository(url)
        self._type = StoreType.GIT
        self._git = GitRepo(coresys, coresys.config.path_addons_git / self._slug, url)

    async def remove(self) -> None:
        """Remove add-on repository."""
        await self._git.remove()
