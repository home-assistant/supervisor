"""Test fixup app execute restart."""

from unittest.mock import patch

import pytest

from supervisor.apps.app import App
from supervisor.const import AppState
from supervisor.coresys import CoreSys
from supervisor.docker.app import DockerApp
from supervisor.docker.interface import DockerInterface
from supervisor.exceptions import DockerError
from supervisor.resolution.const import ContextType, IssueType, SuggestionType
from supervisor.resolution.data import Issue, Suggestion
from supervisor.resolution.fixups.app_execute_restart import FixupAppExecuteRestart

from tests.const import TEST_ADDON_SLUG

DEVICE_ACCESS_MISSING_ISSUE = Issue(
    IssueType.DEVICE_ACCESS_MISSING,
    ContextType.ADDON,
    reference=TEST_ADDON_SLUG,
)
EXECUTE_RESTART_SUGGESTION = Suggestion(
    SuggestionType.EXECUTE_RESTART, ContextType.ADDON, reference="local_ssh"
)


@pytest.mark.usefixtures("path_extern")
async def test_fixup(coresys: CoreSys, install_app_ssh: App):
    """Test fixup restarts app."""
    install_app_ssh.state = AppState.STARTED
    app_execute_restart = FixupAppExecuteRestart(coresys)
    assert app_execute_restart.auto is False

    async def mock_stop(*args, **kwargs):
        install_app_ssh.state = AppState.STOPPED

    coresys.resolution.add_issue(
        DEVICE_ACCESS_MISSING_ISSUE,
        suggestions=[SuggestionType.EXECUTE_RESTART],
    )
    with (
        patch.object(DockerInterface, "stop") as stop,
        patch.object(DockerApp, "run") as run,
        patch.object(App, "_wait_for_startup"),
        patch.object(App, "write_options"),
    ):
        await app_execute_restart()
        stop.assert_called_once()
        run.assert_called_once()

    assert not coresys.resolution.issues
    assert not coresys.resolution.suggestions


@pytest.mark.usefixtures("path_extern")
async def test_fixup_stop_error(
    coresys: CoreSys, install_app_ssh: App, caplog: pytest.LogCaptureFixture
):
    """Test fixup fails on stop app failure."""
    install_app_ssh.state = AppState.STARTED
    app_execute_start = FixupAppExecuteRestart(coresys)

    coresys.resolution.add_issue(
        DEVICE_ACCESS_MISSING_ISSUE,
        suggestions=[SuggestionType.EXECUTE_RESTART],
    )
    with (
        patch.object(DockerInterface, "stop", side_effect=DockerError),
        patch.object(DockerApp, "run") as run,
    ):
        await app_execute_start()
        run.assert_not_called()

    assert DEVICE_ACCESS_MISSING_ISSUE in coresys.resolution.issues
    assert EXECUTE_RESTART_SUGGESTION in coresys.resolution.suggestions
    assert "Could not stop local_ssh" in caplog.text


@pytest.mark.usefixtures("path_extern")
async def test_fixup_start_error(
    coresys: CoreSys, install_app_ssh: App, caplog: pytest.LogCaptureFixture
):
    """Test fixup logs a start app failure."""
    install_app_ssh.state = AppState.STARTED
    app_execute_start = FixupAppExecuteRestart(coresys)

    coresys.resolution.add_issue(
        DEVICE_ACCESS_MISSING_ISSUE,
        suggestions=[SuggestionType.EXECUTE_RESTART],
    )
    with (
        patch.object(DockerInterface, "stop") as stop,
        patch.object(DockerApp, "run", side_effect=DockerError),
        patch.object(App, "write_options"),
    ):
        await app_execute_start()
        stop.assert_called_once()

    assert DEVICE_ACCESS_MISSING_ISSUE not in coresys.resolution.issues
    assert EXECUTE_RESTART_SUGGESTION not in coresys.resolution.suggestions
    assert "Could not restart local_ssh" in caplog.text


async def test_fixup_no_app(coresys: CoreSys, caplog: pytest.LogCaptureFixture):
    """Test fixup dismisses if app is missing."""
    app_execute_start = FixupAppExecuteRestart(coresys)

    coresys.resolution.add_issue(
        DEVICE_ACCESS_MISSING_ISSUE,
        suggestions=[SuggestionType.EXECUTE_RESTART],
    )
    with patch.object(DockerApp, "stop") as stop:
        await app_execute_start()
        stop.assert_not_called()

    assert not coresys.resolution.issues
    assert not coresys.resolution.suggestions
    assert "Cannot restart app local_ssh as it does not exist" in caplog.text
