"""Test git repository."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import AsyncMock, patch

from git import GitCommandError, InvalidGitRepositoryError, NoSuchPathError
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
