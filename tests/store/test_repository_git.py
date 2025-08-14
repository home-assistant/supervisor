"""Test git repository."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

from git import GitCommandError, InvalidGitRepositoryError, NoSuchPathError
import pytest

from supervisor.coresys import CoreSys
from supervisor.exceptions import StoreGitCloneError, StoreGitError
from supervisor.resolution.const import ContextType, IssueType, SuggestionType
from supervisor.resolution.data import Issue, Suggestion
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


@pytest.mark.usefixtures("tmp_supervisor_data", "supervisor_internet")
async def test_git_load_corrupt(coresys: CoreSys, tmp_path: Path):
    """Test git load with corrupt repo."""
    coresys.hardware.disk.get_disk_free_space = lambda x: 5000
    repo_dir = tmp_path / "repo"
    repo = GitRepo(coresys, repo_dir, REPO_URL)

    # Pretend we have a something but not .git to force a reset
    repo_dir.mkdir()
    marker = repo_dir / "test.txt"
    marker.touch()

    def mock_clone_from(url, path, *args, **kwargs):
        """Mock to just make a .git and return."""
        Path(path, ".git").mkdir()
        return MagicMock()

    with patch("git.Repo") as mock_repo:
        mock_repo.clone_from = mock_clone_from
        await repo.load()
        assert mock_repo.call_count == 1
        assert not marker.exists()
        assert (repo_dir / ".git").is_dir()


@pytest.mark.usefixtures("tmp_supervisor_data", "supervisor_internet")
async def test_git_pull_correct(coresys: CoreSys, tmp_path: Path):
    """Test git pull with corrupt repo."""
    coresys.hardware.disk.get_disk_free_space = lambda x: 5000
    repo_dir = tmp_path / "repo"
    repo = GitRepo(coresys, repo_dir, REPO_URL)

    # Set up a our fake repo
    repo_dir.mkdir()
    git_dir = repo_dir / ".git"
    git_dir.mkdir()
    (repo_dir / "test.txt").touch()

    with patch("git.Repo"):
        await repo.load()

        # Make it corrupt
        git_dir.rmdir()

        # Check that we get an issue on pull
        with pytest.raises(
            StoreGitError,
            match=f"Can't update {REPO_URL} repo because git information is missing",
        ):
            await repo.pull()
        assert (
            Issue(
                IssueType.CORRUPT_REPOSITORY, ContextType.STORE, reference=repo_dir.stem
            )
            in coresys.resolution.issues
        )
        assert (
            Suggestion(
                SuggestionType.EXECUTE_RESET, ContextType.STORE, reference=repo_dir.stem
            )
            in coresys.resolution.suggestions
        )


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
