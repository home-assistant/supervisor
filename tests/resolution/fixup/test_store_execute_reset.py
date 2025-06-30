"""Test evaluation base."""

# pylint: disable=import-error,protected-access
from pathlib import Path
from unittest.mock import PropertyMock, patch

import pytest

from supervisor.config import CoreConfig
from supervisor.coresys import CoreSys
from supervisor.exceptions import StoreGitCloneError
from supervisor.resolution.const import ContextType, IssueType, SuggestionType
from supervisor.resolution.data import Issue, Suggestion
from supervisor.resolution.fixups.store_execute_reset import FixupStoreExecuteReset
from supervisor.store.git import GitRepo
from supervisor.store.repository import Repository


@pytest.fixture(name="mock_addons_git", autouse=True)
async def fixture_mock_addons_git(tmp_supervisor_data: Path) -> None:
    """Mock addons git path."""
    with patch.object(
        CoreConfig,
        "path_addons_git",
        new=PropertyMock(return_value=tmp_supervisor_data / "addons" / "git"),
    ):
        yield


@pytest.mark.usefixtures("supervisor_internet")
async def test_fixup(coresys: CoreSys):
    """Test fixup."""
    store_execute_reset = FixupStoreExecuteReset(coresys)
    test_repo = coresys.config.path_addons_git / "94cfad5a"

    assert store_execute_reset.auto

    coresys.resolution.add_suggestion(
        Suggestion(
            SuggestionType.EXECUTE_RESET, ContextType.STORE, reference="94cfad5a"
        )
    )
    coresys.resolution.add_issue(
        Issue(IssueType.CORRUPT_REPOSITORY, ContextType.STORE, reference="94cfad5a")
    )

    test_repo.mkdir(parents=True)
    good_marker = test_repo / ".git"
    (corrupt_marker := (test_repo / "corrupt")).touch()
    assert test_repo.exists()
    assert not good_marker.exists()
    assert corrupt_marker.exists()

    async def mock_clone(obj: GitRepo, path: Path | None = None):
        """Mock of clone method."""
        path = path or obj.path
        await coresys.run_in_executor((path / ".git").mkdir)

    coresys.store.repositories["94cfad5a"] = Repository(
        coresys, "https://github.com/home-assistant/addons-example"
    )
    with (
        patch.object(GitRepo, "load"),
        patch.object(GitRepo, "_clone", new=mock_clone),
        patch("shutil.disk_usage", return_value=(42, 42, 2 * (1024.0**3))),
    ):
        await store_execute_reset()

    assert test_repo.exists()
    assert good_marker.exists()
    assert not corrupt_marker.exists()
    assert len(coresys.resolution.suggestions) == 0
    assert len(coresys.resolution.issues) == 0


@pytest.mark.usefixtures("supervisor_internet")
async def test_fixup_clone_fail(coresys: CoreSys):
    """Test fixup does not delete cache when clone fails."""
    store_execute_reset = FixupStoreExecuteReset(coresys)
    test_repo = coresys.config.path_addons_git / "94cfad5a"

    assert store_execute_reset.auto

    coresys.resolution.add_suggestion(
        Suggestion(
            SuggestionType.EXECUTE_RESET, ContextType.STORE, reference="94cfad5a"
        )
    )
    coresys.resolution.add_issue(
        Issue(IssueType.CORRUPT_REPOSITORY, ContextType.STORE, reference="94cfad5a")
    )

    test_repo.mkdir(parents=True)
    (corrupt_marker := (test_repo / "corrupt")).touch()
    assert test_repo.exists()
    assert corrupt_marker.exists()

    coresys.store.repositories["94cfad5a"] = Repository(
        coresys, "https://github.com/home-assistant/addons-example"
    )
    with (
        patch.object(GitRepo, "load"),
        patch.object(GitRepo, "_clone", side_effect=StoreGitCloneError),
        patch("shutil.disk_usage", return_value=(42, 42, 2 * (1024.0**3))),
    ):
        await store_execute_reset()

    assert test_repo.exists()
    assert corrupt_marker.exists()
    assert len(coresys.resolution.suggestions) == 1
    assert len(coresys.resolution.issues) == 1
