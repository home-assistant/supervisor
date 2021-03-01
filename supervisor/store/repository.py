"""Represent a Supervisor repository."""
import logging
from pathlib import Path
from typing import Dict, Optional

import voluptuous as vol

from ..const import ATTR_MAINTAINER, ATTR_NAME, ATTR_URL, FILE_SUFFIX_CONFIGURATION
from ..coresys import CoreSys, CoreSysAttributes
from ..exceptions import ConfigurationFileError, StoreError
from ..utils.common import read_json_or_yaml_file
from .const import StoreType
from .git import GitRepoCustom, GitRepoHassIO
from .utils import get_hash_from_repository
from .validate import SCHEMA_REPOSITORY_CONFIG

_LOGGER: logging.Logger = logging.getLogger(__name__)
UNKNOWN = "unknown"


class Repository(CoreSysAttributes):
    """Repository in Supervisor."""

    def __init__(self, coresys: CoreSys, repository: str):
        """Initialize repository object."""
        self.coresys: CoreSys = coresys
        self.git: Optional[str] = None

        self.source: str = repository
        if repository == StoreType.LOCAL:
            self._slug = repository
            self._type = StoreType.LOCAL
        elif repository == StoreType.CORE:
            self.git = GitRepoHassIO(coresys)
            self._slug = repository
            self._type = StoreType.CORE
        else:
            self.git = GitRepoCustom(coresys, repository)
            self.source = repository
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
    def data(self) -> Dict:
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
        """Check if store is valid."""
        if self.type != StoreType.GIT:
            return True

        # If exists?
        for filetype in FILE_SUFFIX_CONFIGURATION:
            repository_file = Path(self.git.path / f"repository{filetype}")
            if not repository_file.exists():
                continue

        if not repository_file.exists():
            return False

        # If valid?
        try:
            SCHEMA_REPOSITORY_CONFIG(read_json_or_yaml_file(repository_file))
        except (ConfigurationFileError, vol.Invalid):
            return False

        return True

    async def load(self) -> None:
        """Load addon repository."""
        if not self.git:
            return
        await self.git.load()

    async def update(self) -> None:
        """Update add-on repository."""
        if self.type == StoreType.LOCAL or not self.validate():
            return
        await self.git.pull()

    async def remove(self) -> None:
        """Remove add-on repository."""
        if self.type != StoreType.GIT:
            _LOGGER.error("Can't remove built-in repositories!")
            raise StoreError()

        await self.git.remove()
