"""Test fixup core execute rebuild."""

from unittest.mock import MagicMock, patch

from docker.errors import NotFound
import pytest

from supervisor.addons.addon import Addon
from supervisor.coresys import CoreSys
from supervisor.docker.interface import DockerInterface
from supervisor.docker.manager import DockerAPI
from supervisor.resolution.const import ContextType, IssueType, SuggestionType
from supervisor.resolution.fixups.addon_execute_rebuild import FixupAddonExecuteRebuild


def make_mock_container_get(status: str):
    """Make mock of container get."""
    out = MagicMock()
    out.status = status
    out.attrs = {"State": {"ExitCode": 0}, "Mounts": []}

    def mock_container_get(name):
        return out

    return mock_container_get


async def _mock_wait_for_container() -> None:
    """Mock of wait for container."""


async def test_fixup(docker: DockerAPI, coresys: CoreSys, install_addon_ssh: Addon):
    """Test fixup rebuilds addon's container."""
    docker.containers.get = make_mock_container_get("running")

    addon_execute_rebuild = FixupAddonExecuteRebuild(coresys)

    assert addon_execute_rebuild.auto is False

    coresys.resolution.create_issue(
        IssueType.DOCKER_CONFIG,
        ContextType.ADDON,
        reference="local_ssh",
        suggestions=[SuggestionType.EXECUTE_REBUILD],
    )
    with patch.object(
        Addon, "restart", return_value=_mock_wait_for_container()
    ) as restart:
        await addon_execute_rebuild()
        restart.assert_called_once()

    assert not coresys.resolution.issues
    assert not coresys.resolution.suggestions


async def test_fixup_stopped_core(
    docker: DockerAPI,
    coresys: CoreSys,
    install_addon_ssh: Addon,
    caplog: pytest.LogCaptureFixture,
):
    """Test fixup just removes addon's container when it is stopped."""
    caplog.clear()
    docker.containers.get = make_mock_container_get("stopped")
    addon_execute_rebuild = FixupAddonExecuteRebuild(coresys)

    coresys.resolution.create_issue(
        IssueType.DOCKER_CONFIG,
        ContextType.ADDON,
        reference="local_ssh",
        suggestions=[SuggestionType.EXECUTE_REBUILD],
    )
    with patch.object(Addon, "restart") as restart:
        await addon_execute_rebuild()
        restart.assert_not_called()

    assert not coresys.resolution.issues
    assert not coresys.resolution.suggestions
    docker.containers.get("addon_local_ssh").remove.assert_called_once_with(force=True)
    assert "Addon local_ssh is stopped" in caplog.text


async def test_fixup_unknown_core(
    docker: DockerAPI,
    coresys: CoreSys,
    install_addon_ssh: Addon,
    caplog: pytest.LogCaptureFixture,
):
    """Test fixup does nothing if addon's container has already been removed."""
    caplog.clear()
    docker.containers.get.side_effect = NotFound("")
    addon_execute_rebuild = FixupAddonExecuteRebuild(coresys)

    coresys.resolution.create_issue(
        IssueType.DOCKER_CONFIG,
        ContextType.ADDON,
        reference="local_ssh",
        suggestions=[SuggestionType.EXECUTE_REBUILD],
    )
    with (
        patch.object(Addon, "restart") as restart,
        patch.object(DockerInterface, "stop") as stop,
    ):
        await addon_execute_rebuild()
        restart.assert_not_called()
        stop.assert_not_called()

    assert not coresys.resolution.issues
    assert not coresys.resolution.suggestions
    assert "Container for addon local_ssh does not exist" in caplog.text


async def test_fixup_addon_removed(coresys: CoreSys, caplog: pytest.LogCaptureFixture):
    """Test fixup does nothing if addon has been removed."""
    caplog.clear()
    addon_execute_rebuild = FixupAddonExecuteRebuild(coresys)

    coresys.resolution.create_issue(
        IssueType.DOCKER_CONFIG,
        ContextType.ADDON,
        reference="local_ssh",
        suggestions=[SuggestionType.EXECUTE_REBUILD],
    )
    await addon_execute_rebuild()
    assert "Cannot rebuild addon local_ssh as it is not installed" in caplog.text
