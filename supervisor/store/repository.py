"""Represent a Supervisor repository."""

import logging
from pathlib import Path

import voluptuous as vol

from supervisor.utils import get_latest_mtime

from ..const import ATTR_MAINTAINER, ATTR_NAME, ATTR_URL, FILE_SUFFIX_CONFIGURATION
from ..coresys import CoreSys, CoreSysAttributes
from ..exceptions import ConfigurationFileError, StoreError
from ..utils.common import read_json_or_yaml_file
from .const import StoreType
from .git import GitRepo, GitRepoCustom, GitRepoHassIO
from .utils import get_hash_from_repository
from .validate import SCHEMA_REPOSITORY_CONFIG

_LOGGER: logging.Logger = logging.getLogger(__name__)
UNKNOWN = "unknown"


class Repository(CoreSysAttributes):
    """Add-on store repository in Supervisor."""

    def __init__(self, coresys: CoreSys, repository: str):
        """Initialize add-on store repository object."""
        self.coresys: CoreSys = coresys
        self.git: GitRepo | None = None

        self.source: str = repository
        if repository == StoreType.LOCAL:
            self._slug = repository
            self._type = StoreType.LOCAL
            self._latest_mtime: float | None = None
        elif repository == StoreType.CORE:
            self.git = GitRepoHassIO(coresys)
            self._slug = repository
            self._type = StoreType.CORE
        else:
            self.git = GitRepoCustom(coresys, repository)
            self._slug = get_hash_from_repository(repository)
            self._type = StoreType.GIT

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

    def validate(self) -> bool:
        """Check if store is valid.

        Must be run in executor.
        """
        if self.type != StoreType.GIT:
            return True

        # If exists?
        for filetype in FILE_SUFFIX_CONFIGURATION:
            repository_file = Path(self.git.path / f"repository{filetype}")
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

    async def load(self) -> None:
        """Load addon repository."""
        if not self.git:
            self._latest_mtime, _ = await self.sys_run_in_executor(
                get_latest_mtime, self.sys_config.path_addons_local
            )
            return
        await self.git.load()

    async def update(self) -> bool:
        """Update add-on repository.

        Returns True if the repository was updated.
        """
        if not await self.sys_run_in_executor(self.validate):
            return False

        if self.type != StoreType.LOCAL:
            return await self.git.pull()

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

    async def remove(self) -> None:
        """Remove add-on repository."""
        if self.type != StoreType.GIT:
            raise StoreError("Can't remove built-in repositories!", _LOGGER.error)

        await self.git.remove()
