"""Test git repository."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

from git import GitCommandError, InvalidGitRepositoryError, NoSuchPathError
import pytest

from supervisor.coresys import CoreSys
from supervisor.exceptions import StoreGitCloneError, StoreGitError
from supervisor.resolution.const import ContextType, IssueType, SuggestionType
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
    [
        InvalidGitRepositoryError(),
        NoSuchPathError(),
        GitCommandError("clone"),
        UnicodeDecodeError("decode", b"", 0, 0, ""),
    ],
)
async def test_git_clone_error(
    coresys: CoreSys, tmp_path: Path, clone_from: AsyncMock, git_error: Exception
):
    """Test git clone error."""
    repo = GitRepo(coresys, tmp_path, REPO_URL)

    clone_from.side_effect = git_error
    with pytest.raises(StoreGitCloneError):
        await repo.clone.__wrapped__(repo)

    assert len(coresys.resolution.suggestions) == 0


async def test_git_load(coresys: CoreSys, tmp_path: Path):
    """Test git load."""
    repo_dir = tmp_path / "repo"
    repo = GitRepo(coresys, repo_dir, REPO_URL)
    repo.clone = AsyncMock()

    # Test with non-existing git repo root directory
    await repo.load()
    assert repo.clone.call_count == 1

    repo.clone.reset_mock()

    # Test with existing git repo root directory, but empty
    repo_dir.mkdir()
    await repo.load()
    assert repo.clone.call_count == 1

    repo.clone.reset_mock()

    # Pretend we have a repo
    (repo_dir / ".git").mkdir()

    with patch("git.Repo") as mock_repo:
        await repo.load()
        assert repo.clone.call_count == 0
        assert mock_repo.call_count == 1


@pytest.mark.parametrize(
    "git_errors",
    [
        InvalidGitRepositoryError(),
        NoSuchPathError(),
        GitCommandError("init"),
        UnicodeDecodeError("decode", b"", 0, 0, ""),
        GitCommandError("fsck"),
    ],
)
async def test_git_load_error(coresys: CoreSys, tmp_path: Path, git_errors: Exception):
    """Test git load error."""
    coresys.hardware.disk.get_disk_free_space = lambda x: 5000
    repo = GitRepo(coresys, tmp_path, REPO_URL)

    # Pretend we have a repo
    (tmp_path / ".git").mkdir()

    with (
        patch("git.Repo") as mock_repo,
        pytest.raises(StoreGitError),
    ):
        mock_repo.side_effect = git_errors
        await repo.load()

    assert len(coresys.resolution.suggestions) == 0


@pytest.mark.usefixtures("supervisor_internet")
async def test_git_pull_missing_origin_remote(coresys: CoreSys, tmp_path: Path):
    """Test git pull with missing origin remote creates reset suggestion.

    This tests the scenario where a repository exists but has no 'origin' remote,
    which can happen if the remote was renamed or deleted. The pull operation
    should create a CORRUPT_REPOSITORY issue with EXECUTE_RESET suggestion.

    Fixes: SUPERVISOR-69Z, SUPERVISOR-172C
    """
    repo = GitRepo(coresys, tmp_path, REPO_URL)

    # Create a mock git repo without an origin remote
    mock_repo = MagicMock()
    mock_repo.remotes = []  # Empty remotes list - no 'origin'
    mock_repo.active_branch.name = "main"
    repo.repo = mock_repo

    with (
        patch("git.Git") as mock_git,
        pytest.raises(StoreGitError),
    ):
        mock_git.return_value.ls_remote = MagicMock()
        await repo.pull.__wrapped__(repo)

    # Verify resolution issue was created
    assert len(coresys.resolution.issues) == 1
    assert coresys.resolution.issues[0].type == IssueType.CORRUPT_REPOSITORY
    assert coresys.resolution.issues[0].context == ContextType.STORE

    # Verify reset suggestion was created
    assert len(coresys.resolution.suggestions) == 1
    assert coresys.resolution.suggestions[0].type == SuggestionType.EXECUTE_RESET
