"""Test git repository."""

from __future__ import annotations

import configparser
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, PropertyMock, call, patch

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


async def test_git_load_updates_origin_remote_url(coresys: CoreSys, tmp_path: Path):
    """Test git load updates an existing origin remote URL."""

    class MockRemotes(list):
        """Minimal remote container with GitPython-style origin attribute."""

        @property
        def origin(self):
            """Return origin remote."""
            return self[0]

    repo = GitRepo(coresys, tmp_path, REPO_URL)

    # Pretend we have a repo
    (tmp_path / ".git").mkdir()

    origin = MagicMock()
    origin.name = "origin"
    origin.url = "https://github.com/awesome-developer/old-repo"

    mock_repo = MagicMock()
    mock_repo.remotes = MockRemotes([origin])

    with patch("git.Repo", return_value=mock_repo):
        await repo.load()

    origin.set_url.assert_called_once_with(REPO_URL)


async def test_git_load_corrupted_remotes_config(coresys: CoreSys, tmp_path: Path):
    """Test git load raises StoreGitError when remotes config is corrupted."""
    repo = GitRepo(coresys, tmp_path, REPO_URL)

    # Pretend we have a repo
    (tmp_path / ".git").mkdir()

    mock_repo = MagicMock()
    type(mock_repo).remotes = PropertyMock(
        side_effect=configparser.MissingSectionHeaderError("config", 1, "garbage line")
    )

    with (
        patch("git.Repo", return_value=mock_repo),
        pytest.raises(StoreGitError, match="Cannot access remotes"),
    ):
        await repo.load()


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

    with patch("git.Repo") as mock_repo:
        mock_repo.side_effect = git_errors
        with pytest.raises(StoreGitError):
            await repo.load()

    assert len(coresys.resolution.suggestions) == 0


@pytest.mark.parametrize(
    ("remote_commit", "changed"),
    [
        pytest.param("abcdef0", False, id="unchanged"),
        pytest.param("fedcba0", True, id="changed"),
    ],
)
async def test_git_pull_checks_remote_with_repository_config(
    coresys: CoreSys, tmp_path: Path, remote_commit: str, changed: bool
):
    """Test pull can check a remote that requires repository-local configuration."""
    repo = GitRepo(coresys, tmp_path, REPO_URL)
    mock_repo = MagicMock()
    origin = mock_repo.remotes.origin
    origin.name = "origin"
    origin.url = REPO_URL
    mock_repo.remotes.__iter__.return_value = [origin]
    mock_repo.active_branch.name = "main"
    mock_repo.commit.side_effect = {
        "main": "abcdef0",
        "origin/main": remote_commit,
    }.__getitem__
    mock_repo.git.ls_remote.return_value = ""
    repo.repo = mock_repo

    with patch("git.Git") as unbound_git:
        unbound_git.return_value.ls_remote.side_effect = GitCommandError(
            "ls-remote", 128, stderr="Authentication failed"
        )
        assert await repo.pull.__wrapped__(repo) is changed

    mock_repo.git.ls_remote.assert_called_once_with("--heads", REPO_URL)
    origin.fetch.assert_called_once_with(**{"update-shallow": True, "depth": 1})
    reset_call = call("origin/main", hard=True)
    assert mock_repo.git.reset.call_args_list == [reset_call] * int(changed)


async def test_git_pull_remote_check_failure(coresys: CoreSys, tmp_path: Path):
    """Test a remote check failure stops the update without marking corruption."""
    repo = GitRepo(coresys, tmp_path, REPO_URL)
    mock_repo = MagicMock()
    repo.repo = mock_repo
    error = GitCommandError("ls-remote", 128, stderr="Authentication failed")
    mock_repo.git.ls_remote.side_effect = error
    unbound_git = MagicMock()
    unbound_git.ls_remote.side_effect = error

    with (
        patch("git.Git", return_value=unbound_git),
        pytest.raises(StoreGitError) as raised,
    ):
        await repo.pull.__wrapped__(repo)

    assert raised.value.__cause__ is error
    mock_repo.git.ls_remote.assert_called_once_with("--heads", REPO_URL)
    mock_repo.remotes.origin.fetch.assert_not_called()
    mock_repo.git.reset.assert_not_called()
    mock_repo.git.submodule.assert_not_called()
    mock_repo.git.clean.assert_not_called()
    assert not coresys.resolution.issues


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

    with patch("git.Git") as mock_git:
        mock_git.return_value.ls_remote = MagicMock()
        with pytest.raises(StoreGitError):
            await repo.pull.__wrapped__(repo)

    # Verify resolution issue was created
    assert len(coresys.resolution.issues) == 1
    assert coresys.resolution.issues[0].type == IssueType.CORRUPT_REPOSITORY
    assert coresys.resolution.issues[0].context == ContextType.STORE

    # Verify reset suggestion was created
    assert len(coresys.resolution.suggestions) == 1
    assert coresys.resolution.suggestions[0].type == SuggestionType.EXECUTE_RESET
