"""Test fixup plugin execute rebuild."""

from unittest.mock import MagicMock, patch

import pytest

from supervisor.coresys import CoreSys
from supervisor.docker.manager import DockerAPI
from supervisor.plugins.audio import PluginAudio
from supervisor.resolution.const import ContextType, IssueType, SuggestionType
from supervisor.resolution.fixups.plugin_execute_rebuild import (
    FixupPluginExecuteRebuild,
)


def make_mock_container_get(status: str):
    """Make mock of container get."""
    out = MagicMock()
    out.status = status
    out.attrs = {"State": {"ExitCode": 0}, "Mounts": []}

    def mock_container_get(name):
        return out

    return mock_container_get


@pytest.mark.parametrize("status", ["running", "stopped"])
async def test_fixup(docker: DockerAPI, coresys: CoreSys, status: str):
    """Test fixup rebuilds plugin's container regardless of current state."""
    docker.containers.get = make_mock_container_get(status)

    plugin_execute_rebuild = FixupPluginExecuteRebuild(coresys)

    assert plugin_execute_rebuild.auto is True

    coresys.resolution.create_issue(
        IssueType.DOCKER_CONFIG,
        ContextType.PLUGIN,
        reference="audio",
        suggestions=[SuggestionType.EXECUTE_REBUILD],
    )
    with patch.object(PluginAudio, "rebuild") as rebuild:
        await plugin_execute_rebuild()
        rebuild.assert_called_once()

    assert not coresys.resolution.issues
    assert not coresys.resolution.suggestions
