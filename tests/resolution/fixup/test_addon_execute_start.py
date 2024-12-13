"""Test fixup addon execute start."""

from unittest.mock import patch

import pytest

from supervisor.addons.addon import Addon
from supervisor.const import AddonState
from supervisor.coresys import CoreSys
from supervisor.docker.addon import DockerAddon
from supervisor.exceptions import DockerError
from supervisor.resolution.const import ContextType, SuggestionType
from supervisor.resolution.data import Suggestion
from supervisor.resolution.fixups.addon_execute_start import FixupAddonExecuteStart

from tests.addons.test_manager import BOOT_FAIL_ISSUE

EXECUTE_START_SUGGESTION = Suggestion(
    SuggestionType.EXECUTE_START, ContextType.ADDON, reference="local_ssh"
)


@pytest.mark.parametrize(
    "state", [AddonState.STARTED, AddonState.STARTUP, AddonState.STOPPED]
)
@pytest.mark.usefixtures("path_extern")
async def test_fixup(coresys: CoreSys, install_addon_ssh: Addon, state: AddonState):
    """Test fixup starts addon."""
    install_addon_ssh.state = AddonState.UNKNOWN
    addon_execute_start = FixupAddonExecuteStart(coresys)
    assert addon_execute_start.auto is False

    async def mock_start(*args, **kwargs):
        install_addon_ssh.state = state

    coresys.resolution.add_issue(
        BOOT_FAIL_ISSUE,
        suggestions=[SuggestionType.EXECUTE_START],
    )
    with (
        patch.object(DockerAddon, "run") as run,
        patch.object(Addon, "_wait_for_startup", new=mock_start),
        patch.object(Addon, "write_options"),
    ):
        await addon_execute_start()
        run.assert_called_once()

    assert not coresys.resolution.issues
    assert not coresys.resolution.suggestions


@pytest.mark.usefixtures("path_extern")
async def test_fixup_start_error(coresys: CoreSys, install_addon_ssh: Addon):
    """Test fixup fails on start addon failure."""
    install_addon_ssh.state = AddonState.UNKNOWN
    addon_execute_start = FixupAddonExecuteStart(coresys)

    coresys.resolution.add_issue(
        BOOT_FAIL_ISSUE,
        suggestions=[SuggestionType.EXECUTE_START],
    )
    with (
        patch.object(DockerAddon, "run", side_effect=DockerError) as run,
        patch.object(Addon, "write_options"),
    ):
        await addon_execute_start()
        run.assert_called_once()

    assert BOOT_FAIL_ISSUE in coresys.resolution.issues
    assert EXECUTE_START_SUGGESTION in coresys.resolution.suggestions


@pytest.mark.parametrize("state", [AddonState.ERROR, AddonState.UNKNOWN])
@pytest.mark.usefixtures("path_extern")
async def test_fixup_wait_start_failure(
    coresys: CoreSys, install_addon_ssh: Addon, state: AddonState
):
    """Test fixup fails if addon does not complete startup."""
    install_addon_ssh.state = AddonState.UNKNOWN
    addon_execute_start = FixupAddonExecuteStart(coresys)

    async def mock_start(*args, **kwargs):
        install_addon_ssh.state = state

    coresys.resolution.add_issue(
        BOOT_FAIL_ISSUE,
        suggestions=[SuggestionType.EXECUTE_START],
    )
    with (
        patch.object(DockerAddon, "run") as run,
        patch.object(Addon, "_wait_for_startup", new=mock_start),
        patch.object(Addon, "write_options"),
    ):
        await addon_execute_start()
        run.assert_called_once()

    assert BOOT_FAIL_ISSUE in coresys.resolution.issues
    assert EXECUTE_START_SUGGESTION in coresys.resolution.suggestions


async def test_fixup_no_addon(coresys: CoreSys):
    """Test fixup dismisses if addon is missing."""
    addon_execute_start = FixupAddonExecuteStart(coresys)

    coresys.resolution.add_issue(
        BOOT_FAIL_ISSUE,
        suggestions=[SuggestionType.EXECUTE_START],
    )
    with (
        patch.object(DockerAddon, "run") as run,
        patch.object(Addon, "write_options"),
    ):
        await addon_execute_start()
        run.assert_not_called()

    assert not coresys.resolution.issues
    assert not coresys.resolution.suggestions
