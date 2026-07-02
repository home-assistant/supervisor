"""Test evaluation base."""

# pylint: disable=import-error,protected-access
import errno
from pathlib import Path
from unittest.mock import PropertyMock, patch

import pytest

from supervisor.config import CoreConfig
from supervisor.coresys import CoreSys
from supervisor.exceptions import StoreGitCloneError
from supervisor.resolution.const import (
    ContextType,
    IssueType,
    SuggestionType,
    UnhealthyReason,
)
from supervisor.resolution.data import Issue, Suggestion
from supervisor.resolution.fixups.store_execute_reset import FixupStoreExecuteReset
from supervisor.store.git import GitRepo
from supervisor.store.repository import Repository, RepositoryGit


@pytest.fixture(name="mock_addons_git", autouse=True)
async def fixture_mock_apps_git(tmp_supervisor_data: Path) -> None:
    """Mock apps git path."""
    with patch.object(
        CoreConfig,
        "path_apps_git",
        new=PropertyMock(return_value=tmp_supervisor_data / "apps" / "git"),
    ):
        yield


def add_store_reset_suggestion(coresys: CoreSys) -> None:
    """Add suggestion for tests."""
    coresys.resolution.add_suggestion(
        Suggestion(
            SuggestionType.EXECUTE_RESET, ContextType.STORE, reference="94cfad5a"
        )
    )
    coresys.resolution.add_issue(
        Issue(IssueType.CORRUPT_REPOSITORY, ContextType.STORE, reference="94cfad5a")
    )


@pytest.mark.usefixtures("supervisor_internet")
async def test_fixup(coresys: CoreSys):
    """Test fixup."""
    store_execute_reset = FixupStoreExecuteReset(coresys)
    test_repo = coresys.config.path_apps_git / "94cfad5a"

    assert store_execute_reset.auto

    add_store_reset_suggestion(coresys)
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

    coresys.store.repositories["94cfad5a"] = Repository.create(
        coresys, "https://github.com/home-assistant/addons-example"
    )
    with (
        patch.object(GitRepo, "load"),
        patch.object(GitRepo, "_clone", new=mock_clone),
        patch.object(RepositoryGit, "validate", return_value=True),
        patch("shutil.disk_usage", return_value=(42, 42, 2 * (1024.0**3))),
    ):
        await store_execute_reset()

    assert test_repo.exists()
    assert good_marker.exists()
    assert not corrupt_marker.exists()
    assert len(coresys.resolution.suggestions) == 0
    assert len(coresys.resolution.issues) == 0
    assert len(list(coresys.config.path_tmp.iterdir())) == 0


@pytest.mark.usefixtures("supervisor_internet")
async def test_fixup_still_invalid_after_reset(coresys: CoreSys):
    """Test reset suggestion is dropped but issue kept when repo stays invalid."""
    store_execute_reset = FixupStoreExecuteReset(coresys)
    test_repo = coresys.config.path_apps_git / "94cfad5a"

    add_store_reset_suggestion(coresys)
    # A remove suggestion is offered alongside reset for corrupt repositories
    coresys.resolution.add_suggestion(
        Suggestion(
            SuggestionType.EXECUTE_REMOVE, ContextType.STORE, reference="94cfad5a"
        )
    )
    test_repo.mkdir(parents=True)

    async def mock_clone(obj: GitRepo, path: Path | None = None):
        """Mock of clone method."""
        path = path or obj.path
        await coresys.run_in_executor((path / ".git").mkdir)

    coresys.store.repositories["94cfad5a"] = Repository.create(
        coresys, "https://github.com/home-assistant/addons-example"
    )
    with (
        patch.object(GitRepo, "load"),
        patch.object(GitRepo, "_clone", new=mock_clone),
        # Repository re-clones fine but its content is still not valid
        patch.object(RepositoryGit, "validate", return_value=False),
        patch("shutil.disk_usage", return_value=(42, 42, 2 * (1024.0**3))),
    ):
        await store_execute_reset()

    # Retrying the reset won't help, so its suggestion is dropped to stop the
    # hourly auto-retry. The issue and the remove suggestion must remain.
    suggestion_types = {
        suggestion.type for suggestion in coresys.resolution.suggestions
    }
    assert SuggestionType.EXECUTE_RESET not in suggestion_types
    assert SuggestionType.EXECUTE_REMOVE in suggestion_types
    assert len(coresys.resolution.issues) == 1
    assert len(list(coresys.config.path_tmp.iterdir())) == 0


@pytest.mark.usefixtures("supervisor_internet")
async def test_fixup_clone_fail(coresys: CoreSys):
    """Test fixup does not delete cache when clone fails."""
    store_execute_reset = FixupStoreExecuteReset(coresys)
    test_repo = coresys.config.path_apps_git / "94cfad5a"

    add_store_reset_suggestion(coresys)
    test_repo.mkdir(parents=True)
    (corrupt_marker := (test_repo / "corrupt")).touch()
    assert test_repo.exists()
    assert corrupt_marker.exists()

    coresys.store.repositories["94cfad5a"] = Repository.create(
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
    assert len(list(coresys.config.path_tmp.iterdir())) == 0


@pytest.mark.parametrize(
    ("error_num", "unhealthy"), [(errno.EBUSY, False), (errno.EBADMSG, True)]
)
@pytest.mark.usefixtures("supervisor_internet")
async def test_fixup_move_fail(coresys: CoreSys, error_num: int, unhealthy: bool):
    """Test fixup cleans up clone on move fail.

    This scenario shouldn't really happen unless something is pretty wrong with the system.
    It will leave the user in a bind without the git cache but at least we try to clean up tmp.
    """
    store_execute_reset = FixupStoreExecuteReset(coresys)
    test_repo = coresys.config.path_apps_git / "94cfad5a"

    add_store_reset_suggestion(coresys)
    test_repo.mkdir(parents=True)
    coresys.store.repositories["94cfad5a"] = Repository.create(
        coresys, "https://github.com/home-assistant/addons-example"
    )
    with (
        patch.object(GitRepo, "load"),
        patch.object(GitRepo, "_clone"),
        patch("supervisor.store.git.Path.rename", side_effect=(err := OSError())),
        patch("shutil.disk_usage", return_value=(42, 42, 2 * (1024.0**3))),
    ):
        err.errno = error_num
        await store_execute_reset()

    assert len(coresys.resolution.suggestions) == 1
    assert len(coresys.resolution.issues) == 1
    assert len(list(coresys.config.path_tmp.iterdir())) == 0
    assert (
        UnhealthyReason.OSERROR_BAD_MESSAGE in coresys.resolution.unhealthy
    ) is unhealthy
