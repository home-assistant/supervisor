"""Test fixup core execute rebuild."""

import asyncio
from collections.abc import Callable, Coroutine
from typing import Any
from unittest.mock import MagicMock, patch

import aiodocker
from aiodocker.containers import DockerContainer
import pytest

from supervisor.addons.addon import Addon
from supervisor.coresys import CoreSys
from supervisor.docker.interface import DockerInterface
from supervisor.docker.manager import DockerAPI
from supervisor.resolution.const import ContextType, IssueType, SuggestionType
from supervisor.resolution.fixups.addon_execute_rebuild import FixupAddonExecuteRebuild


def make_mock_container_get(
    status: str,
) -> Callable[[str], Coroutine[Any, Any, DockerContainer]]:
    """Make mock of container get."""
    out = MagicMock(spec=DockerContainer)
    out.status = status
    out.show.return_value = {"State": {"Status": status, "ExitCode": 0}, "Mounts": []}

    async def mock_container_get(name) -> DockerContainer:
        return out

    return mock_container_get


@pytest.mark.usefixtures("install_addon_ssh")
async def test_fixup(docker: DockerAPI, coresys: CoreSys):
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
    with patch.object(Addon, "restart", return_value=asyncio.sleep(0)) as restart:
        await addon_execute_rebuild()
        restart.assert_called_once()

    assert not coresys.resolution.issues
    assert not coresys.resolution.suggestions


@pytest.mark.usefixtures("install_addon_ssh")
async def test_fixup_stopped_core(
    docker: DockerAPI, coresys: CoreSys, caplog: pytest.LogCaptureFixture
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
    (await docker.containers.get("addon_local_ssh")).delete.assert_called_once_with(
        force=True, v=True
    )
    assert "Addon local_ssh is stopped" in caplog.text


@pytest.mark.usefixtures("install_addon_ssh")
async def test_fixup_unknown_core(
    docker: DockerAPI, coresys: CoreSys, caplog: pytest.LogCaptureFixture
):
    """Test fixup does nothing if addon's container has already been removed."""
    caplog.clear()
    docker.containers.get.side_effect = aiodocker.DockerError(
        404, {"message": "missing"}
    )
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
