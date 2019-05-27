"""Represent a Hass.io repository."""
from .git import GitRepoHassIO, GitRepoCustom
from .utils import get_hash_from_repository
from ..const import (
    REPOSITORY_CORE,
    REPOSITORY_LOCAL,
    ATTR_NAME,
    ATTR_URL,
    ATTR_MAINTAINER,
)
from ..coresys import CoreSysAttributes
from ..exceptions import APIError

UNKNOWN = "unknown"


class Repository(CoreSysAttributes):
    """Repository in Hass.io."""

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
