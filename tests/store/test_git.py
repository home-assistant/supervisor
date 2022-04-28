"""Test Supervisor add-on git."""
from unittest.mock import patch

from git import GitCommandError, InvalidGitRepositoryError, NoSuchPathError
import pytest

from supervisor.addons.addon import Addon
from supervisor.const import ATTR_REPOSITORY
from supervisor.coresys import CoreSys
from supervisor.exceptions import StoreGitError
from supervisor.resolution.const import ContextType, IssueType, SuggestionType
from supervisor.store.git import GitRepoCustom, GitRepoHassIO


@pytest.mark.parametrize(
    "error",
    [
        GitCommandError("clone"),
        InvalidGitRepositoryError(),
        NoSuchPathError(),
    ],
)
async def test_clone_core(coresys: CoreSys, error: Exception):
    """Test cloning core add-on repo."""
    core = GitRepoHassIO(coresys)

    with patch("supervisor.store.git.git.Repo.clone_from") as clone_from:
        assert len(coresys.resolution.issues) == 0
        assert len(coresys.resolution.suggestions) == 0

        await core.clone.__wrapped__(core)

        clone_from.assert_called_once_with(
            "https://github.com/home-assistant/addons",
            str(coresys.config.path_addons_core),
            **{"recursive": True, "depth": 1, "shallow-submodules": True},
        )
        assert len(coresys.resolution.issues) == 0
        assert len(coresys.resolution.suggestions) == 0

        clone_from.side_effect = error
        with pytest.raises(StoreGitError):
            await core.clone.__wrapped__(core)

        assert len(coresys.resolution.issues) == 1
        assert coresys.resolution.issues[0].type == IssueType.FATAL_ERROR
        assert coresys.resolution.issues[0].context == ContextType.STORE
        assert coresys.resolution.issues[0].reference == "core"

        assert len(coresys.resolution.suggestions) == 1
        assert coresys.resolution.suggestions[0].type == SuggestionType.EXECUTE_RELOAD
        assert coresys.resolution.suggestions[0].context == ContextType.STORE
        assert coresys.resolution.suggestions[0].reference == "core"


async def test_clone_custom_issue(coresys: CoreSys):
    """Test issue cloning custom add-on repo."""
    repo = GitRepoCustom(coresys, "https://github.com/example/addons")

    with patch("supervisor.store.git.git.Repo.clone_from") as clone_from:
        assert len(coresys.resolution.issues) == 0
        assert len(coresys.resolution.suggestions) == 0

        clone_from.side_effect = GitCommandError("clone")
        with pytest.raises(StoreGitError):
            await repo.clone.__wrapped__(repo)

        clone_from.assert_called_once_with(
            "https://github.com/example/addons",
            f"{coresys.config.path_addons_git}/25d47127",
            **{"recursive": True, "depth": 1, "shallow-submodules": True},
        )

        assert len(coresys.resolution.issues) == 1
        assert coresys.resolution.issues[0].type == IssueType.FATAL_ERROR
        assert coresys.resolution.issues[0].context == ContextType.STORE
        assert coresys.resolution.issues[0].reference == "25d47127"

        assert len(coresys.resolution.suggestions) == 1
        assert coresys.resolution.suggestions[0].type == SuggestionType.EXECUTE_REMOVE
        assert coresys.resolution.suggestions[0].context == ContextType.STORE
        assert coresys.resolution.suggestions[0].reference == "25d47127"


async def test_clone_custom_issue_with_addon_installed(coresys: CoreSys):
    """Test issue cloning custom add-on repo with addon installed."""
    repo = GitRepoCustom(coresys, "https://github.com/example/addons")
    fake = Addon(coresys, "25d47127_test")
    coresys.addons.data.system["25d47127_test"] = {ATTR_REPOSITORY: "25d47127"}
    coresys.addons.local = {"25d47127_test": fake}

    with patch("supervisor.store.git.git.Repo.clone_from") as clone_from:
        assert len(coresys.resolution.suggestions) == 0

        clone_from.side_effect = GitCommandError("clone")
        with pytest.raises(StoreGitError):
            await repo.clone.__wrapped__(repo)

        clone_from.assert_called_once_with(
            "https://github.com/example/addons",
            f"{coresys.config.path_addons_git}/25d47127",
            **{"recursive": True, "depth": 1, "shallow-submodules": True},
        )

        assert len(coresys.resolution.suggestions) == 1
        assert coresys.resolution.suggestions[0].type == SuggestionType.EXECUTE_RELOAD
        assert coresys.resolution.suggestions[0].context == ContextType.STORE
        assert coresys.resolution.suggestions[0].reference == "25d47127"
