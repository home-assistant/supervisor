"""Represent a Hass.io repository."""
from .git import GitRepoHassIO, GitRepoCustom
from .utils import get_hash_from_repository
from ..const import (
    REPOSITORY_CORE, REPOSITORY_LOCAL, ATTR_NAME, ATTR_URL, ATTR_MAINTAINER)
from ..coresys import CoreSysAttributes
from ..exceptions import APIError

UNKNOWN = 'unknown'


class Repository(CoreSysAttributes):
    """Repository in Hass.io."""

    def __init__(self, coresys, repository):
        """Initialize repository object."""
        self.coresys = coresys
        self.source = None
        self.git = None

        if repository == REPOSITORY_LOCAL:
            self._id = repository
        elif repository == REPOSITORY_CORE:
            self._id = repository
            self.git = GitRepoHassIO(coresys)
        else:
            self._id = get_hash_from_repository(repository)
            self.git = GitRepoCustom(coresys, repository)
            self.source = repository

    @property
    def _mesh(self):
        """Return data struct repository."""
        return self.sys_addons.data.repositories.get(self._id, {})

    @property
    def slug(self):
        """Return slug of repository."""
        return self._id

    @property
    def name(self):
        """Return name of repository."""
        return self._mesh.get(ATTR_NAME, UNKNOWN)

    @property
    def url(self):
        """Return URL of repository."""
        return self._mesh.get(ATTR_URL, self.source)

    @property
    def maintainer(self):
        """Return url of repository."""
        return self._mesh.get(ATTR_MAINTAINER, UNKNOWN)

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
        if self._id in (REPOSITORY_CORE, REPOSITORY_LOCAL):
            raise APIError("Can't remove built-in repositories!")

        self.git.remove()
