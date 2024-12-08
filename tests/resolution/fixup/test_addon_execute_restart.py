"""Test fixup addon execute restart."""

from unittest.mock import patch

import pytest

from supervisor.addons.addon import Addon
from supervisor.const import AddonState
from supervisor.coresys import CoreSys
from supervisor.docker.addon import DockerAddon
from supervisor.docker.interface import DockerInterface
from supervisor.exceptions import DockerError
from supervisor.resolution.const import ContextType, IssueType, SuggestionType
from supervisor.resolution.data import Issue, Suggestion
from supervisor.resolution.fixups.addon_execute_restart import FixupAddonExecuteRestart

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
async def test_fixup(coresys: CoreSys, install_addon_ssh: Addon):
    """Test fixup restarts addon."""
    install_addon_ssh.state = AddonState.STARTED
    addon_execute_restart = FixupAddonExecuteRestart(coresys)
    assert addon_execute_restart.auto is False

    async def mock_stop(*args, **kwargs):
        install_addon_ssh.state = AddonState.STOPPED

    coresys.resolution.add_issue(
        DEVICE_ACCESS_MISSING_ISSUE,
        suggestions=[SuggestionType.EXECUTE_RESTART],
    )
    with (
        patch.object(DockerInterface, "stop") as stop,
        patch.object(DockerAddon, "run") as run,
        patch.object(Addon, "_wait_for_startup"),
        patch.object(Addon, "write_options"),
    ):
        await addon_execute_restart()
        stop.assert_called_once()
        run.assert_called_once()

    assert not coresys.resolution.issues
    assert not coresys.resolution.suggestions


@pytest.mark.usefixtures("path_extern")
async def test_fixup_stop_error(
    coresys: CoreSys, install_addon_ssh: Addon, caplog: pytest.LogCaptureFixture
):
    """Test fixup fails on stop addon failure."""
    install_addon_ssh.state = AddonState.STARTED
    addon_execute_start = FixupAddonExecuteRestart(coresys)

    coresys.resolution.add_issue(
        DEVICE_ACCESS_MISSING_ISSUE,
        suggestions=[SuggestionType.EXECUTE_RESTART],
    )
    with (
        patch.object(DockerInterface, "stop", side_effect=DockerError),
        patch.object(DockerAddon, "run") as run,
    ):
        await addon_execute_start()
        run.assert_not_called()

    assert DEVICE_ACCESS_MISSING_ISSUE in coresys.resolution.issues
    assert EXECUTE_RESTART_SUGGESTION in coresys.resolution.suggestions
    assert "Could not stop local_ssh" in caplog.text


@pytest.mark.usefixtures("path_extern")
async def test_fixup_start_error(
    coresys: CoreSys, install_addon_ssh: Addon, caplog: pytest.LogCaptureFixture
):
    """Test fixup logs a start addon failure."""
    install_addon_ssh.state = AddonState.STARTED
    addon_execute_start = FixupAddonExecuteRestart(coresys)

    coresys.resolution.add_issue(
        DEVICE_ACCESS_MISSING_ISSUE,
        suggestions=[SuggestionType.EXECUTE_RESTART],
    )
    with (
        patch.object(DockerInterface, "stop") as stop,
        patch.object(DockerAddon, "run", side_effect=DockerError),
        patch.object(Addon, "write_options"),
    ):
        await addon_execute_start()
        stop.assert_called_once()

    assert DEVICE_ACCESS_MISSING_ISSUE not in coresys.resolution.issues
    assert EXECUTE_RESTART_SUGGESTION not in coresys.resolution.suggestions
    assert "Could not restart local_ssh" in caplog.text


async def test_fixup_no_addon(coresys: CoreSys, caplog: pytest.LogCaptureFixture):
    """Test fixup dismisses if addon is missing."""
    addon_execute_start = FixupAddonExecuteRestart(coresys)

    coresys.resolution.add_issue(
        DEVICE_ACCESS_MISSING_ISSUE,
        suggestions=[SuggestionType.EXECUTE_RESTART],
    )
    with patch.object(DockerAddon, "stop") as stop:
        await addon_execute_start()
        stop.assert_not_called()

    assert not coresys.resolution.issues
    assert not coresys.resolution.suggestions
    assert "Cannot restart addon local_ssh as it does not exist" in caplog.text
