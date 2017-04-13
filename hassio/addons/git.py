"""Init file for HassIO addons git."""
import asyncio
import logging
import os

import git

from ..const import URL_HASSIO_ADDONS

_LOGGER = logging.getLogger(__name__)


class AddonsRepo(object):
    """Manage addons git repo."""

    def __init__(self, config, loop):
        """Initialize docker base wrapper."""
        self.config = config
        self.loop = loop
        self.repo = None
        self._lock = asyncio.Lock(loop=loop)

    async def load(self):
        """Init git addon repo."""
        if not os.path.isdir(self.config.path_addons_repo):
            return await self.clone()

        async with self._lock:
            try:
                _LOGGER.info("Load addons repository")
                self.repo = await self.loop.run_in_executor(
                    None, git.Repo(self.config.path_addons_repo))

            except (git.InvalidGitRepositoryError, git.NoSuchPathError) as err:
                _LOGGER.error("Can't load addons repo: %s.", err)
                return False

            return True

    async def clone(self):
        """Clone git addon repo."""
        async with self._lock:
            try:
                _LOGGER.info("Clone addons repository")
                self.repo = await self.loop.run_in_executor(
                    None, git.Repo.clone_from, URL_HASSIO_ADDONS,
                    self.config.path_addons_repo)

            except (git.InvalidGitRepositoryError, git.NoSuchPathError) as err:
                _LOGGER.error("Can't clone addons repo: %s.", err)
                return False

            return True

    async def pull(self):
        """Pull git addon repo."""
        if self._lock.locked():
            _LOGGER.warning("It is already a task in progress.")
            return False

        async with self._lock:
            try:
                _LOGGER.info("Pull addons repository")
                await self.loop.run_in_executor(
                    None, self.repo.remotes.origin.pull)

            except (git.InvalidGitRepositoryError, git.NoSuchPathError) as err:
                _LOGGER.error("Can't pull addons repo: %s.", err)
                return False

            return True
