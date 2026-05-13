"""Test fixup app execute start."""

from unittest.mock import patch

import pytest

from supervisor.apps.app import App
from supervisor.const import AppState
from supervisor.coresys import CoreSys
from supervisor.docker.app import DockerApp
from supervisor.exceptions import DockerError
from supervisor.resolution.const import ContextType, SuggestionType
from supervisor.resolution.data import Suggestion
from supervisor.resolution.fixups.app_execute_start import FixupAppExecuteStart

from tests.apps.test_manager import BOOT_FAIL_ISSUE

EXECUTE_START_SUGGESTION = Suggestion(
    SuggestionType.EXECUTE_START, ContextType.ADDON, reference="local_ssh"
)


@pytest.mark.parametrize(
    "state", [AppState.STARTED, AppState.STARTUP, AppState.STOPPED]
)
@pytest.mark.usefixtures("path_extern")
async def test_fixup(coresys: CoreSys, install_app_ssh: App, state: AppState):
    """Test fixup starts app."""
    install_app_ssh.state = AppState.UNKNOWN
    app_execute_start = FixupAppExecuteStart(coresys)
    assert app_execute_start.auto is False

    async def mock_start(*args, **kwargs):
        install_app_ssh.state = state

    coresys.resolution.add_issue(
        BOOT_FAIL_ISSUE,
        suggestions=[SuggestionType.EXECUTE_START],
    )
    with (
        patch.object(DockerApp, "run") as run,
        patch.object(App, "_wait_for_startup", new=mock_start),
        patch.object(App, "write_options"),
    ):
        await app_execute_start()
        run.assert_called_once()

    assert not coresys.resolution.issues
    assert not coresys.resolution.suggestions


@pytest.mark.usefixtures("path_extern")
async def test_fixup_start_error(coresys: CoreSys, install_app_ssh: App):
    """Test fixup fails on start app failure."""
    install_app_ssh.state = AppState.UNKNOWN
    app_execute_start = FixupAppExecuteStart(coresys)

    coresys.resolution.add_issue(
        BOOT_FAIL_ISSUE,
        suggestions=[SuggestionType.EXECUTE_START],
    )
    with (
        patch.object(DockerApp, "run", side_effect=DockerError) as run,
        patch.object(App, "write_options"),
    ):
        await app_execute_start()
        run.assert_called_once()

    assert BOOT_FAIL_ISSUE in coresys.resolution.issues
    assert EXECUTE_START_SUGGESTION in coresys.resolution.suggestions


@pytest.mark.parametrize("state", [AppState.ERROR, AppState.UNKNOWN])
@pytest.mark.usefixtures("path_extern")
async def test_fixup_wait_start_failure(
    coresys: CoreSys, install_app_ssh: App, state: AppState
):
    """Test fixup fails if app does not complete startup."""
    install_app_ssh.state = AppState.UNKNOWN
    app_execute_start = FixupAppExecuteStart(coresys)

    async def mock_start(*args, **kwargs):
        install_app_ssh.state = state

    coresys.resolution.add_issue(
        BOOT_FAIL_ISSUE,
        suggestions=[SuggestionType.EXECUTE_START],
    )
    with (
        patch.object(DockerApp, "run") as run,
        patch.object(App, "_wait_for_startup", new=mock_start),
        patch.object(App, "write_options"),
    ):
        await app_execute_start()
        run.assert_called_once()

    assert BOOT_FAIL_ISSUE in coresys.resolution.issues
    assert EXECUTE_START_SUGGESTION in coresys.resolution.suggestions


async def test_fixup_no_app(coresys: CoreSys):
    """Test fixup dismisses if app is missing."""
    app_execute_start = FixupAppExecuteStart(coresys)

    coresys.resolution.add_issue(
        BOOT_FAIL_ISSUE,
        suggestions=[SuggestionType.EXECUTE_START],
    )
    with (
        patch.object(DockerApp, "run") as run,
        patch.object(App, "write_options"),
    ):
        await app_execute_start()
        run.assert_not_called()

    assert not coresys.resolution.issues
    assert not coresys.resolution.suggestions
