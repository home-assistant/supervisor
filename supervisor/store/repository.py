"""Represent a Supervisor repository."""

from __future__ import annotations

from abc import ABC, abstractmethod
import logging
from pathlib import Path

import voluptuous as vol

from supervisor.utils import get_latest_mtime

from ..const import (
    ATTR_MAINTAINER,
    ATTR_NAME,
    ATTR_URL,
    FILE_SUFFIX_CONFIGURATION,
    REPOSITORY_LOCAL,
    URL_HASSIO_ADDONS,
)
from ..coresys import CoreSys, CoreSysAttributes
from ..exceptions import ConfigurationFileError, StoreError
from ..utils.common import read_json_or_yaml_file
from .git import GitRepo
from .types import BuiltinRepository
from .utils import get_hash_from_repository
from .validate import SCHEMA_REPOSITORY_CONFIG

_LOGGER: logging.Logger = logging.getLogger(__name__)
UNKNOWN = "unknown"


class Repository(CoreSysAttributes, ABC):
    """Add-on store repository in Supervisor."""

    def __init__(self, coresys: CoreSys, repository: str, local_path: Path, slug: str):
        """Initialize add-on store repository object."""
        self._slug: str = slug
        self._local_path: Path = local_path
        self.coresys: CoreSys = coresys
        self.source: str = repository

    @staticmethod
    def create(coresys: CoreSys, repository: str) -> Repository:
        """Create a repository instance."""
        if repository == REPOSITORY_LOCAL:
            slug = REPOSITORY_LOCAL
            local_path = coresys.config.path_addons_local
            return RepositoryLocal(coresys, local_path, slug)
        if repository in BuiltinRepository:
            builtin = BuiltinRepository(repository)
            if builtin == BuiltinRepository.CORE:
                slug = "core"
                local_path = coresys.config.path_addons_core
                url = URL_HASSIO_ADDONS
            else:
                # For other builtin repositories (URL-based)
                slug = get_hash_from_repository(repository)
                local_path = coresys.config.path_addons_git / slug
                url = repository
            return RepositoryGitBuiltin(coresys, repository, local_path, slug, url)
        # Custom repositories
        slug = get_hash_from_repository(repository)
        local_path = coresys.config.path_addons_git / slug
        return RepositoryCustom(coresys, repository, local_path, slug)

    def __repr__(self) -> str:
        """Return internal representation."""
        return f"<Store.Repository: {self.slug} / {self.source}>"

    @property
    def slug(self) -> str:
        """Return repo slug."""
        return self._slug

    @property
    def local_path(self) -> Path:
        """Return local path to repository."""
        return self._local_path

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

    def __init__(
        self, coresys: CoreSys, repository: str, local_path: Path, slug: str
    ) -> None:
        """Initialize object."""
        super().__init__(coresys, repository, local_path, slug)

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

    def __init__(self, coresys: CoreSys, local_path: Path, slug: str) -> None:
        """Initialize object."""
        super().__init__(coresys, BuiltinRepository.LOCAL.value, local_path, slug)
        self._latest_mtime: float | None = None

    async def load(self) -> None:
        """Load addon repository."""
        self._latest_mtime, _ = await self.sys_run_in_executor(
            get_latest_mtime, self.local_path
        )

    async def update(self) -> bool:
        """Update add-on repository.

        Returns True if the repository was updated.
        """
        # Check local modifications
        latest_mtime, modified_path = await self.sys_run_in_executor(
            get_latest_mtime, self.local_path
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

    def __init__(
        self, coresys: CoreSys, repository: str, local_path: Path, slug: str, url: str
    ) -> None:
        """Initialize object."""
        super().__init__(coresys, repository, local_path, slug)
        self._git = GitRepo(coresys, local_path, url)


class RepositoryCustom(RepositoryGit):
    """A custom add-on repository."""

    def __init__(self, coresys: CoreSys, url: str, local_path: Path, slug: str) -> None:
        """Initialize object."""
        super().__init__(coresys, url, local_path, slug)
        self._git = GitRepo(coresys, local_path, url)

    async def remove(self) -> None:
        """Remove add-on repository."""
        await self._git.remove()
