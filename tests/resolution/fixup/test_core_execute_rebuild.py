"""Test fixup core execute rebuild."""

from collections.abc import Callable, Coroutine
from typing import Any
from unittest.mock import MagicMock, patch

import aiodocker
from aiodocker.containers import DockerContainer
import pytest

from supervisor.coresys import CoreSys
from supervisor.docker.interface import DockerInterface
from supervisor.docker.manager import DockerAPI
from supervisor.homeassistant.core import HomeAssistantCore
from supervisor.resolution.const import ContextType, IssueType, SuggestionType
from supervisor.resolution.fixups.core_execute_rebuild import FixupCoreExecuteRebuild


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


async def test_fixup(docker: DockerAPI, coresys: CoreSys):
    """Test fixup rebuilds core's container."""
    docker.containers.get = make_mock_container_get("running")

    core_execute_rebuild = FixupCoreExecuteRebuild(coresys)

    assert core_execute_rebuild.auto is False

    coresys.resolution.create_issue(
        IssueType.DOCKER_CONFIG,
        ContextType.CORE,
        suggestions=[SuggestionType.EXECUTE_REBUILD],
    )
    with patch.object(HomeAssistantCore, "rebuild") as rebuild:
        await core_execute_rebuild()
        rebuild.assert_called_once()

    assert not coresys.resolution.issues
    assert not coresys.resolution.suggestions


async def test_fixup_stopped_core(
    docker: DockerAPI, coresys: CoreSys, caplog: pytest.LogCaptureFixture
):
    """Test fixup just removes HA's container when it is stopped."""
    caplog.clear()
    docker.containers.get = make_mock_container_get("stopped")
    core_execute_rebuild = FixupCoreExecuteRebuild(coresys)

    coresys.resolution.create_issue(
        IssueType.DOCKER_CONFIG,
        ContextType.CORE,
        suggestions=[SuggestionType.EXECUTE_REBUILD],
    )
    with patch.object(HomeAssistantCore, "rebuild") as rebuild:
        await core_execute_rebuild()
        rebuild.assert_not_called()

    assert not coresys.resolution.issues
    assert not coresys.resolution.suggestions
    (await docker.containers.get("homeassistant")).delete.assert_called_once_with(
        force=True, v=True
    )
    assert "Home Assistant is stopped" in caplog.text


async def test_fixup_unknown_core(
    docker: DockerAPI, coresys: CoreSys, caplog: pytest.LogCaptureFixture
):
    """Test fixup does nothing if core's container has already been removed."""
    caplog.clear()
    docker.containers.get.side_effect = aiodocker.DockerError(
        404, {"message": "missing"}
    )
    core_execute_rebuild = FixupCoreExecuteRebuild(coresys)

    coresys.resolution.create_issue(
        IssueType.DOCKER_CONFIG,
        ContextType.CORE,
        suggestions=[SuggestionType.EXECUTE_REBUILD],
    )
    with (
        patch.object(HomeAssistantCore, "rebuild") as rebuild,
        patch.object(DockerInterface, "stop") as stop,
    ):
        await core_execute_rebuild()
        rebuild.assert_not_called()
        stop.assert_not_called()

    assert not coresys.resolution.issues
    assert not coresys.resolution.suggestions
    assert "Container for Home Assistant does not exist" in caplog.text
