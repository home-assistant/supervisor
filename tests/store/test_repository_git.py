"""Test git repository."""
from __future__ import annotations

from pathlib import Path
from unittest.mock import AsyncMock, patch

from git import GitCommandError, GitError, InvalidGitRepositoryError, NoSuchPathError
import pytest

from supervisor.coresys import CoreSys
from supervisor.exceptions import StoreGitCloneError, StoreGitError
from supervisor.store.git import GitRepo

REPO_URL = "https://github.com/awesome-developer/awesome-repo"


@pytest.fixture(name="clone_from")
async def fixture_clone_from():
    """Mock git clone_from."""
    with patch("git.Repo.clone_from") as clone_from:
        yield clone_from


@pytest.mark.parametrize("branch", [None, "dev"])
async def test_git_clone(
    coresys: CoreSys, tmp_path: Path, clone_from: AsyncMock, branch: str | None
):
    """Test git clone."""
    fragment = f"#{branch}" if branch else ""
    repo = GitRepo(coresys, tmp_path, f"{REPO_URL}{fragment}")

    await repo.clone.__wrapped__(repo)

    kwargs = {"recursive": True, "depth": 1, "shallow-submodules": True}
    if branch:
        kwargs["branch"] = branch

    clone_from.assert_called_once_with(
        REPO_URL,
        str(tmp_path),
        **kwargs,
    )


@pytest.mark.parametrize(
    "git_error",
    [InvalidGitRepositoryError(), NoSuchPathError(), GitCommandError("clone")],
)
async def test_git_clone_error(
    coresys: CoreSys, tmp_path: Path, clone_from: AsyncMock, git_error: GitError
):
    """Test git clone error."""
    repo = GitRepo(coresys, tmp_path, REPO_URL)

    clone_from.side_effect = git_error
    with pytest.raises(StoreGitCloneError):
        await repo.clone.__wrapped__(repo)

    assert len(coresys.resolution.suggestions) == 0


async def test_git_load(coresys: CoreSys, tmp_path: Path):
    """Test git load."""
    repo = GitRepo(coresys, tmp_path, REPO_URL)

    with patch("pathlib.Path.is_dir", return_value=True), patch.object(
        GitRepo, "sys_run_in_executor", new_callable=AsyncMock
    ) as run_in_executor:
        await repo.load()

        assert run_in_executor.call_count == 2


@pytest.mark.parametrize(
    "git_errors",
    [
        InvalidGitRepositoryError(),
        NoSuchPathError(),
        GitCommandError("init"),
        [AsyncMock(), GitCommandError("fsck")],
    ],
)
async def test_git_load_error(
    coresys: CoreSys, tmp_path: Path, git_errors: GitError | list[GitError | None]
):
    """Test git load error."""
    repo = GitRepo(coresys, tmp_path, REPO_URL)

    with patch("pathlib.Path.is_dir", return_value=True), patch.object(
        GitRepo, "sys_run_in_executor", new_callable=AsyncMock
    ) as run_in_executor, pytest.raises(StoreGitError):
        run_in_executor.side_effect = git_errors
        await repo.load()

    assert len(coresys.resolution.suggestions) == 0
