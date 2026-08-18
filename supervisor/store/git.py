"""Init file for Supervisor app Git."""

import asyncio
import configparser
from contextlib import suppress
import functools as ft
import logging
from pathlib import Path
from tempfile import TemporaryDirectory

import git

from ..const import ATTR_BRANCH, ATTR_URL
from ..coresys import CoreSys, CoreSysAttributes
from ..exceptions import (
    StoreGitCloneError,
    StoreGitError,
    StoreGitRemoteURLUpdateError,
    StoreJobError,
)
from ..jobs.decorator import Job, JobCondition
from ..resolution.const import ContextType, IssueType, SuggestionType
from ..utils import directory_missing_or_empty, remove_folder
from .validate import RE_REPOSITORY

_LOGGER: logging.Logger = logging.getLogger(__name__)


class GitRepo(CoreSysAttributes):
    """Manage App Git repository."""

    def __init__(self, coresys: CoreSys, path: Path, url: str):
        """Initialize Git base wrapper."""
        self.coresys: CoreSys = coresys
        self.repo: git.Repo | None = None
        self.path: Path = path
        self.lock: asyncio.Lock = asyncio.Lock()

        if not (repository := RE_REPOSITORY.match(url)):
            raise ValueError(f"Invalid url provided for repository GitRepo: {url}")
        self.data: dict[str, str] = repository.groupdict()

    def __repr__(self) -> str:
        """Return internal representation."""
        return f"<Git: {self.path!s}>"

    @property
    def url(self) -> str:
        """Return repository URL."""
        return self.data[ATTR_URL]

    @property
    def branch(self) -> str:
        """Return repository branch."""
        return self.data[ATTR_BRANCH]

    async def load(self) -> None:
        """Init Git app repository."""
        if await self.sys_run_in_executor(directory_missing_or_empty, self.path):
            await self.clone()
            return

        # Load repository
        async with self.lock:
            try:
                _LOGGER.info("Loading app %s repository", self.path)
                repo: git.Repo = await self.sys_run_in_executor(
                    git.Repo, str(self.path)
                )
                self.repo = repo

            except (
                git.InvalidGitRepositoryError,
                git.NoSuchPathError,
                git.CommandError,
                UnicodeDecodeError,
            ) as err:
                _LOGGER.error("Can't load %s", self.path)
                raise StoreGitError from err

        # Fix possible corruption
        async with self.lock:
            _LOGGER.debug("Integrity check app %s repository", self.path)
            await self.sys_run_in_executor(self._sync_origin_remote_url_and_fsck, repo)

    def _sync_origin_remote_url_and_fsck(self, repo: git.Repo) -> None:
        """Sync origin URL and run fsck in a single executor invocation."""
        self._sync_origin_remote_url(repo)
        try:
            repo.git.execute(["git", "fsck"])
        except (
            git.InvalidGitRepositoryError,
            git.NoSuchPathError,
            git.CommandError,
            UnicodeDecodeError,
        ) as err:
            raise StoreGitError(
                f"Integrity check on {self.path} failed: {err!s}", _LOGGER.error
            ) from err

    def _sync_origin_remote_url(self, repo: git.Repo) -> None:
        """Ensure the clone's origin URL matches the configured repository URL."""
        try:
            origin = next(
                (remote for remote in repo.remotes if remote.name == "origin"), None
            )
            if origin is None:
                return
            origin_url = origin.url
        except (
            git.InvalidGitRepositoryError,
            git.NoSuchPathError,
            git.CommandError,
            configparser.Error,
            UnicodeDecodeError,
        ) as err:
            raise StoreGitError(
                f"Cannot access remotes on {self.path}: {err!s}", _LOGGER.error
            ) from err

        if origin_url != self.url:
            try:
                _LOGGER.info(
                    "Updating app %s repository origin URL from %s to %s",
                    self.path,
                    origin_url,
                    self.url,
                )
                origin.set_url(self.url)
            except (
                git.InvalidGitRepositoryError,
                git.NoSuchPathError,
                git.CommandError,
                UnicodeDecodeError,
            ) as err:
                raise StoreGitRemoteURLUpdateError(
                    f"Failed to update app {self.path} repository origin URL: {err!s}",
                    _LOGGER.warning,
                ) from err

    @Job(
        name="git_repo_clone",
        conditions=[JobCondition.FREE_SPACE, JobCondition.INTERNET_SYSTEM],
        on_condition=StoreJobError,
    )
    async def clone(self) -> None:
        """Clone git app repository."""
        async with self.lock:
            await self._clone()

    @Job(
        name="git_repo_reset",
        conditions=[JobCondition.FREE_SPACE, JobCondition.INTERNET_SYSTEM],
        on_condition=StoreJobError,
    )
    async def reset(self) -> None:
        """Reset repository to fix issue with local copy."""
        # Clone into temporary folder
        temp_dir = await self.sys_run_in_executor(
            TemporaryDirectory, dir=self.sys_config.path_tmp
        )
        temp_path = Path(temp_dir.name)
        try:
            await self._clone(temp_path)

            # Remove corrupted repo and move temp clone to its place
            def move_clone():
                remove_folder(folder=self.path)
                temp_path.rename(self.path)

            async with self.lock:
                try:
                    await self.sys_run_in_executor(move_clone)
                except OSError as err:
                    self.sys_resolution.check_oserror(err)
                    raise StoreGitCloneError(
                        f"Can't move clone due to: {err!s}", _LOGGER.error
                    ) from err
        finally:
            # Clean up temporary directory in case of error
            # If the folder was moved this will do nothing
            await self.sys_run_in_executor(temp_dir.cleanup)

    async def _clone(self, path: Path | None = None) -> None:
        """Clone git app repository to location."""
        path = path or self.path
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
            _LOGGER.info("Cloning app %s repository from %s", path, self.url)
            self.repo = await self.sys_run_in_executor(
                ft.partial(
                    git.Repo.clone_from,
                    self.url,
                    str(path),
                    **git_args,  # type: ignore
                )
            )

        except (
            git.InvalidGitRepositoryError,
            git.NoSuchPathError,
            git.CommandError,
            UnicodeDecodeError,
        ) as err:
            _LOGGER.error("Can't clone %s repository: %s.", self.url, err)
            raise StoreGitCloneError from err

    @Job(
        name="git_repo_pull",
        conditions=[JobCondition.FREE_SPACE, JobCondition.INTERNET_SYSTEM],
        on_condition=StoreJobError,
    )
    async def pull(self) -> bool:
        """Pull Git app repo."""
        if self.lock.locked():
            _LOGGER.warning("There is already a task in progress")
            return False
        if self.repo is None:
            _LOGGER.warning("No valid repository for %s", self.url)
            return False

        repo: git.Repo = self.repo

        async with self.lock:
            _LOGGER.info("Update app %s repository from %s", self.path, self.url)
            with suppress(StoreGitRemoteURLUpdateError):
                await self.sys_run_in_executor(self._sync_origin_remote_url, repo)

            try:
                git_cmd = git.Git()
                await self.sys_run_in_executor(git_cmd.ls_remote, "--heads", self.url)
            except git.CommandError as err:
                _LOGGER.warning("Wasn't able to update %s repo: %s.", self.url, err)
                raise StoreGitError from err

            try:

                def _fetch_and_check() -> tuple[str, bool]:
                    """Fetch from origin and check if changed."""
                    # This property access is I/O bound
                    branch = repo.active_branch.name
                    repo.remotes.origin.fetch(
                        **{"update-shallow": True, "depth": 1}  # type: ignore[arg-type]
                    )
                    changed = repo.commit(branch) != repo.commit(f"origin/{branch}")
                    return branch, changed

                # Download data and check for changes
                branch, changed = await self.sys_run_in_executor(_fetch_and_check)

                if changed:
                    # Jump on top of that
                    await self.sys_run_in_executor(
                        ft.partial(repo.git.reset, f"origin/{branch}", hard=True)
                    )

                # Update submodules
                await self.sys_run_in_executor(
                    ft.partial(
                        repo.git.submodule,
                        "update",
                        "--init",
                        "--recursive",
                        "--depth",
                        "1",
                    )
                )

                # Cleanup old data
                await self.sys_run_in_executor(ft.partial(repo.git.clean, "-xdf"))

                return changed

            except (
                git.InvalidGitRepositoryError,
                git.NoSuchPathError,
                git.CommandError,
                ValueError,
                AssertionError,
                AttributeError,
                UnicodeDecodeError,
            ) as err:
                _LOGGER.error("Can't update %s repo: %s.", self.url, err)
                self.sys_resolution.create_issue(
                    IssueType.CORRUPT_REPOSITORY,
                    ContextType.STORE,
                    reference=self.path.stem,
                    suggestions=[SuggestionType.EXECUTE_RESET],
                )
                raise StoreGitError from err

    async def remove(self) -> None:
        """Remove a repository."""
        if self.lock.locked():
            _LOGGER.warning(
                "Cannot remove app repository %s, there is already a task in progress",
                self.url,
            )
            return

        _LOGGER.info("Removing custom app repository %s", self.url)

        def _remove_git_dir(path: Path) -> None:
            if not path.is_dir():
                return
            remove_folder(path)

        async with self.lock:
            await self.sys_run_in_executor(_remove_git_dir, self.path)
