"""Init file for HassIO addons git."""
import asyncio
import logging
import functools as ft
from pathlib import Path
import shutil

import git

from .util import get_hash_from_repository
from ..const import URL_HASSIO_ADDONS

_LOGGER = logging.getLogger(__name__)


class GitRepo(object):
    """Manage addons git repo."""

    def __init__(self, config, loop, path, url):
        """Initialize git base wrapper."""
        self.config = config
        self.loop = loop
        self.repo = None
        self.path = path
        self.url = url
        self._lock = asyncio.Lock(loop=loop)

    async def load(self):
        """Init git addon repo."""
        if not self.path.is_dir():
            return await self.clone()

        async with self._lock:
            try:
                _LOGGER.info("Load addon %s repository", self.path)
                self.repo = await self.loop.run_in_executor(
                    None, git.Repo, str(self.path))

            except (git.InvalidGitRepositoryError, git.NoSuchPathError,
                    git.GitCommandError) as err:
                _LOGGER.error("Can't load %s repo: %s.", self.path, err)
                return False

            return True

    async def clone(self):
        """Clone git addon repo."""
        async with self._lock:
            try:
                _LOGGER.info("Clone addon %s repository", self.url)
                self.repo = await self.loop.run_in_executor(
                    None, ft.partial(
                        git.Repo.clone_from, self.url, str(self.path),
                        recursive=True))

            except (git.InvalidGitRepositoryError, git.NoSuchPathError,
                    git.GitCommandError) as err:
                _LOGGER.error("Can't clone %s repo: %s.", self.url, err)
                return False

            return True

    async def pull(self):
        """Pull git addon repo."""
        if self._lock.locked():
            _LOGGER.warning("It is already a task in progress.")
            return False

        async with self._lock:
            try:
                _LOGGER.info("Pull addon %s repository", self.url)
                await self.loop.run_in_executor(
                    None, self.repo.remotes.origin.pull)

            except (git.InvalidGitRepositoryError, git.NoSuchPathError,
                    git.GitCommandError) as err:
                _LOGGER.error("Can't pull %s repo: %s.", self.url, err)
                return False

            return True


class GitRepoHassIO(GitRepo):
    """HassIO addons repository."""

    def __init__(self, config, loop):
        """Initialize git hassio addon repository."""
        super().__init__(
            config, loop, config.path_addons_core, URL_HASSIO_ADDONS)


class GitRepoCustom(GitRepo):
    """Custom addons repository."""

    def __init__(self, config, loop, url):
        """Initialize git hassio addon repository."""
        path = Path(config.path_addons_git, get_hash_from_repository(url))

        super().__init__(config, loop, path, url)

    def remove(self):
        """Remove a custom addon."""
        if self.path.is_dir():
            _LOGGER.info("Remove custom addon repository %s", self.url)

            def log_err(funct, path, _):
                """Log error."""
                _LOGGER.warning("Can't remove %s", path)

            shutil.rmtree(str(self.path), onerror=log_err)
