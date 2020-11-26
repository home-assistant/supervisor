"""Init file for Supervisor add-on Git."""
import asyncio
import functools as ft
import logging
from pathlib import Path
from typing import Dict, Optional

import git

from ..const import ATTR_BRANCH, ATTR_URL, URL_HASSIO_ADDONS
from ..coresys import CoreSys, CoreSysAttributes
from ..exceptions import StoreGitError
from ..jobs.decorator import Job, JobCondition
from ..resolution.const import ContextType, IssueType, SuggestionType
from ..utils import remove_folder
from ..validate import RE_REPOSITORY
from .utils import get_hash_from_repository

_LOGGER: logging.Logger = logging.getLogger(__name__)


class GitRepo(CoreSysAttributes):
    """Manage Add-on Git repository."""

    def __init__(self, coresys: CoreSys, path: Path, url: str):
        """Initialize Git base wrapper."""
        self.coresys: CoreSys = coresys
        self.repo: Optional[git.Repo] = None
        self.path: Path = path
        self.lock: asyncio.Lock = asyncio.Lock()

        self.data: Dict[str, str] = RE_REPOSITORY.match(url).groupdict()

    @property
    def url(self) -> str:
        """Return repository URL."""
        return self.data[ATTR_URL]

    @property
    def branch(self) -> str:
        """Return repository branch."""
        return self.data[ATTR_BRANCH]

    async def load(self) -> None:
        """Init Git add-on repository."""
        if not self.path.is_dir():
            await self.clone()
            return

        # Load repository
        async with self.lock:
            try:
                _LOGGER.info("Loading add-on %s repository", self.path)
                self.repo = await self.sys_run_in_executor(git.Repo, str(self.path))

            except (
                git.InvalidGitRepositoryError,
                git.NoSuchPathError,
                git.GitCommandError,
            ) as err:
                _LOGGER.error("Can't load %s repo: %s.", self.path, err)
                self.sys_resolution.create_issue(
                    IssueType.FATAL_ERROR,
                    ContextType.STORE,
                    reference=self.path.stem,
                )
                raise StoreGitError() from err

        # Fix possible corruption
        async with self.lock:
            try:
                _LOGGER.debug("Integrity check add-on %s repository", self.path)
                await self.sys_run_in_executor(self.repo.git.execute, ["git", "fsck"])
            except git.GitCommandError as err:
                _LOGGER.error("Integrity check on %s failed: %s.", self.path, err)
                self.sys_resolution.create_issue(
                    IssueType.CORRUPT_REPOSITORY,
                    ContextType.STORE,
                    reference=self.path.stem,
                    suggestions=[SuggestionType.EXECUTE_RESET],
                )
                raise StoreGitError() from err

    @Job(conditions=[JobCondition.FREE_SPACE, JobCondition.INTERNET_SYSTEM])
    async def clone(self) -> None:
        """Clone git add-on repository."""
        async with self.lock:
            git_args = {
                attribute: value
                for attribute, value in (
                    ("recursive", True),
                    ("branch", self.branch),
                    ("depth", 1),
                    ("shallow-submodules", True),
                )
                if value is not None
            }

            try:
                _LOGGER.info("Cloning add-on %s repository", self.url)
                self.repo = await self.sys_run_in_executor(
                    ft.partial(
                        git.Repo.clone_from, self.url, str(self.path), **git_args
                    )
                )

            except (
                git.InvalidGitRepositoryError,
                git.NoSuchPathError,
                git.GitCommandError,
            ) as err:
                _LOGGER.error("Can't clone %s repository: %s.", self.url, err)
                self.sys_resolution.create_issue(
                    IssueType.FATAL_ERROR,
                    ContextType.STORE,
                    reference=self.path.stem,
                    suggestions=[SuggestionType.EXECUTE_RELOAD],
                )
                raise StoreGitError() from err

    @Job(conditions=[JobCondition.FREE_SPACE, JobCondition.INTERNET_SYSTEM])
    async def pull(self):
        """Pull Git add-on repo."""
        if self.lock.locked():
            _LOGGER.warning("There is already a task in progress")
            return

        async with self.lock:
            _LOGGER.info("Update add-on %s repository", self.url)
            branch = self.repo.active_branch.name

            try:
                # Download data
                await self.sys_run_in_executor(
                    ft.partial(
                        self.repo.remotes.origin.fetch,
                        **{"update-shallow": True, "depth": 1},
                    )
                )

                # Jump on top of that
                await self.sys_run_in_executor(
                    ft.partial(self.repo.git.reset, f"origin/{branch}", hard=True)
                )

                # Cleanup old data
                await self.sys_run_in_executor(ft.partial(self.repo.git.clean, "-xdf"))

            except (
                git.InvalidGitRepositoryError,
                git.NoSuchPathError,
                git.GitCommandError,
            ) as err:
                _LOGGER.error("Can't update %s repo: %s.", self.url, err)
                self.sys_resolution.create_issue(
                    IssueType.CORRUPT_REPOSITORY,
                    ContextType.STORE,
                    reference=self.path.stem,
                    suggestions=[SuggestionType.EXECUTE_RELOAD],
                )
                raise StoreGitError() from err

    async def _remove(self):
        """Remove a repository."""
        if self.lock.locked():
            _LOGGER.warning("There is already a task in progress")
            return

        if not self.path.is_dir():
            return
        await remove_folder(self.path)


class GitRepoHassIO(GitRepo):
    """Supervisor add-ons repository."""

    def __init__(self, coresys):
        """Initialize Git Supervisor add-on repository."""
        super().__init__(coresys, coresys.config.path_addons_core, URL_HASSIO_ADDONS)


class GitRepoCustom(GitRepo):
    """Custom add-ons repository."""

    def __init__(self, coresys, url):
        """Initialize custom Git Supervisor addo-n repository."""
        path = Path(coresys.config.path_addons_git, get_hash_from_repository(url))

        super().__init__(coresys, path, url)

    async def remove(self):
        """Remove a custom repository."""
        _LOGGER.info("Removing custom add-on repository %s", self.url)
        await self._remove()
