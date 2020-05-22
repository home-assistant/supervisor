"""Represent a Supervisor repository."""
from ..const import (
    ATTR_MAINTAINER,
    ATTR_NAME,
    ATTR_URL,
    REPOSITORY_CORE,
    REPOSITORY_LOCAL,
)
from ..coresys import CoreSysAttributes
from ..exceptions import APIError
from .git import GitRepoCustom, GitRepoHassIO
from .utils import get_hash_from_repository

UNKNOWN = "unknown"


class Repository(CoreSysAttributes):
    """Repository in Supervisor."""

    slug: str = None

    def __init__(self, coresys, repository):
        """Initialize repository object."""
        self.coresys = coresys
        self.source = None
        self.git = None

        if repository == REPOSITORY_LOCAL:
            self.slug = repository
        elif repository == REPOSITORY_CORE:
            self.slug = repository
            self.git = GitRepoHassIO(coresys)
        else:
            self.slug = get_hash_from_repository(repository)
            self.git = GitRepoCustom(coresys, repository)
            self.source = repository

    @property
    def data(self):
        """Return data struct repository."""
        return self.sys_store.data.repositories.get(self.slug, {})

    @property
    def name(self):
        """Return name of repository."""
        return self.data.get(ATTR_NAME, UNKNOWN)

    @property
    def url(self):
        """Return URL of repository."""
        return self.data.get(ATTR_URL, self.source)

    @property
    def maintainer(self):
        """Return url of repository."""
        return self.data.get(ATTR_MAINTAINER, UNKNOWN)

    async def load(self):
        """Load addon repository."""
        if self.git:
            return await self.git.load()
        return True

    async def update(self):
        """Update add-on repository."""
        if self.git:
            return await self.git.pull()
        return True

    def remove(self):
        """Remove add-on repository."""
        if self.slug in (REPOSITORY_CORE, REPOSITORY_LOCAL):
            raise APIError("Can't remove built-in repositories!")

        self.git.remove()
