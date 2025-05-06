"""Test check Docker Config."""

from unittest.mock import MagicMock, patch

import pytest

from supervisor.addons.addon import Addon
from supervisor.const import CoreState
from supervisor.coresys import CoreSys
from supervisor.docker.interface import DockerInterface
from supervisor.docker.manager import DockerAPI
from supervisor.resolution.checks.docker_config import CheckDockerConfig
from supervisor.resolution.const import ContextType, IssueType, SuggestionType
from supervisor.resolution.data import Issue, Suggestion


def _make_mock_container_get(bad_config_names: list[str], folder: str = "media"):
    """Make mock of container get."""
    mount = {
        "Type": "bind",
        "Source": f"/mnt/data/supervisor/{folder}",
        "Destination": f"/{folder}",
        "Mode": "rw",
        "RW": True,
        "Propagation": "rprivate",
    }

    def mock_container_get(name):
        out = MagicMock()
        out.status = "running"
        out.attrs = {"State": {}, "Mounts": []}
        if name in bad_config_names:
            out.attrs["Mounts"].append(mount)

        return out

    return mock_container_get


async def test_base(coresys: CoreSys):
    """Test check basics."""
    docker_config = CheckDockerConfig(coresys)
    assert docker_config.slug == "docker_config"
    assert docker_config.enabled


@pytest.mark.parametrize("folder", ["media", "share"])
async def test_check(
    docker: DockerAPI, coresys: CoreSys, install_addon_ssh: Addon, folder: str
):
    """Test check reports issue when containers have incorrect config."""
    docker.containers.get = _make_mock_container_get(
        ["homeassistant", "hassio_audio", "addon_local_ssh"], folder
    )
    # Use state used in setup()
    await coresys.core.set_state(CoreState.SETUP)
    with patch.object(DockerInterface, "is_running", return_value=True):
        await coresys.plugins.load()
        await coresys.homeassistant.load()
        await coresys.addons.load()

    docker_config = CheckDockerConfig(coresys)
    assert not coresys.resolution.issues
    assert not coresys.resolution.suggestions

    # An issue and suggestion is added per container with a config issue
    await docker_config.run_check()

    assert len(coresys.resolution.issues) == 4
    assert Issue(IssueType.DOCKER_CONFIG, ContextType.CORE) in coresys.resolution.issues
    assert (
        Issue(IssueType.DOCKER_CONFIG, ContextType.ADDON, reference="local_ssh")
        in coresys.resolution.issues
    )
    assert (
        Issue(IssueType.DOCKER_CONFIG, ContextType.PLUGIN, reference="audio")
        in coresys.resolution.issues
    )
    assert (
        Issue(IssueType.DOCKER_CONFIG, ContextType.SYSTEM) in coresys.resolution.issues
    )

    assert len(coresys.resolution.suggestions) == 4
    assert (
        Suggestion(SuggestionType.EXECUTE_REBUILD, ContextType.CORE)
        in coresys.resolution.suggestions
    )
    assert (
        Suggestion(
            SuggestionType.EXECUTE_REBUILD, ContextType.PLUGIN, reference="audio"
        )
        in coresys.resolution.suggestions
    )
    assert (
        Suggestion(
            SuggestionType.EXECUTE_REBUILD, ContextType.ADDON, reference="local_ssh"
        )
        in coresys.resolution.suggestions
    )
    assert (
        Suggestion(SuggestionType.EXECUTE_REBUILD, ContextType.SYSTEM)
        in coresys.resolution.suggestions
    )

    assert await docker_config.approve_check()

    # IF config issue is resolved, all issues are removed except the main one. Which will be removed if check isn't approved
    docker.containers.get = _make_mock_container_get([])
    with patch.object(DockerInterface, "is_running", return_value=True):
        await coresys.plugins.load()
        await coresys.homeassistant.load()
        await coresys.addons.load()

    assert not await docker_config.approve_check()
    assert len(coresys.resolution.issues) == 1
    assert len(coresys.resolution.suggestions) == 1
    assert (
        Issue(IssueType.DOCKER_CONFIG, ContextType.SYSTEM) in coresys.resolution.issues
    )


async def test_did_run(coresys: CoreSys):
    """Test that the check ran as expected."""
    docker_config = CheckDockerConfig(coresys)
    should_run = docker_config.states
    should_not_run = [state for state in CoreState if state not in should_run]
    assert len(should_run) != 0
    assert len(should_not_run) != 0

    with patch(
        "supervisor.resolution.checks.docker_config.CheckDockerConfig.run_check",
        return_value=None,
    ) as check:
        for state in should_run:
            await coresys.core.set_state(state)
            await docker_config()
            check.assert_called_once()
            check.reset_mock()

        for state in should_not_run:
            await coresys.core.set_state(state)
            await docker_config()
            check.assert_not_called()
            check.reset_mock()
