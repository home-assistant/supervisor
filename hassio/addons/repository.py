"""Represent a HassIO repository."""
from .git import GitRepoHassIO, GitRepoCustom
from .util import get_hash_from_repository
from ..const import (
    REPOSITORY_CORE, REPOSITORY_LOCAL, ATTR_NAME, ATTR_URL, ATTR_MAINTAINER)


class Repository(object):
    """Repository in HassIO."""

    def __init__(self, config, loop, data, repository):
        """Initialize repository object."""
        self.data = data
        self.source = None
        self.git = None

        if repository == REPOSITORY_LOCAL:
            self._id = repository
        elif repository == REPOSITORY_CORE:
            self._id = repository
            self.git = GitRepoHassIO(config, loop)
        else:
            self._id = get_hash_from_repository(repository)
            self.git = GitRepoCustom(config, loop, repository)
            self.source = repository

    @property
    def _mesh(self):
        """Return data struct repository."""
        return self.data.repositories.get(self._id, {})

    @property
    def slug(self):
        """Return slug of repository."""
        return self._id

    @property
    def name(self):
        """Return name of repository."""
        return self._mesh.get(ATTR_NAME, self.source)

    @property
    def url(self):
        """Return url of repository."""
        return self._mesh.get(ATTR_URL)

    @property
    def maintainer(self):
        """Return url of repository."""
        return self._mesh.get(ATTR_MAINTAINER)

    async def load(self):
        """Load addon repository."""
        if self.git:
            return await self.git.load()
        return True

    async def update(self):
        """Update addon repository."""
        if self.git:
            return await self.git.pull()
        return True

    def remove(self):
        """Remove addon repository."""
        if self._id in (REPOSITORY_CORE, REPOSITORY_LOCAL):
            raise RuntimeError("Can't remove built-in repositories!")

        self.git.remove()
