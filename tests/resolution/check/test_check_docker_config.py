"""Test check Docker Config."""

from unittest.mock import MagicMock, patch

from aiodocker.containers import DockerContainer
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

    async def mock_container_get(name):
        out = MagicMock(spec=DockerContainer)
        out.show.return_value = {
            "State": {
                "Status": "running",
                "Running": True,
            },
            "Mounts": [],
        }
        if name in bad_config_names:
            out.show.return_value["Mounts"].append(mount)

        return out

    return mock_container_get


def _make_mock_container_get_with_volume_mount(
    bad_config_names: list[str], folder: str = "media"
):
    """Make mock of container get with VOLUME mount (not managed by supervisor)."""
    # This simulates a Docker VOLUME mount with wrong propagation
    # but NOT created by supervisor configuration
    mount = {
        "Type": "bind",
        "Source": f"/var/lib/docker/volumes/something_{folder}/_data",  # Docker volume source
        "Destination": f"/{folder}",
        "Mode": "rw",
        "RW": True,
        "Propagation": "rprivate",  # Wrong propagation, but not our mount
    }

    async def mock_container_get(name):
        out = MagicMock(spec=DockerContainer)
        out.show.return_value = {
            "State": {
                "Status": "running",
                "Running": True,
            },
            "Mounts": [],
        }
        if name in bad_config_names:
            out.show.return_value["Mounts"].append(mount)

        return out

    return mock_container_get


async def test_base(coresys: CoreSys):
    """Test check basics."""
    docker_config = CheckDockerConfig(coresys)
    assert docker_config.slug == "docker_config"
    assert docker_config.enabled


@pytest.mark.parametrize("folder", ["media", "share"])
@pytest.mark.usefixtures("install_addon_ssh")
async def test_check(docker: DockerAPI, coresys: CoreSys, folder: str):
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


@pytest.mark.parametrize("folder", ["media", "share"])
async def test_addon_volume_mount_not_flagged(
    docker: DockerAPI, coresys: CoreSys, install_addon_ssh: Addon, folder: str
):
    """Test that add-on with VOLUME mount to media/share but not in config is not flagged."""
    # Create an add-on that doesn't have media/share in its mapping configuration
    # Remove the mapping from the addon configuration
    install_addon_ssh.data["map"] = [
        {"type": "config", "read_only": False},
        {"type": "ssl", "read_only": True},
    ]  # No media/share

    # Mock container that has VOLUME mount to media/share with wrong propagation
    docker.containers.get = _make_mock_container_get_with_volume_mount(
        ["addon_local_ssh"], folder
    )

    await coresys.core.set_state(CoreState.SETUP)
    with patch.object(DockerInterface, "is_running", return_value=True):
        await coresys.plugins.load()
        await coresys.homeassistant.load()
        await coresys.addons.load()

    docker_config = CheckDockerConfig(coresys)
    assert not coresys.resolution.issues
    assert not coresys.resolution.suggestions

    # Run check - should NOT create issue for add-on since mount wasn't requested
    await docker_config.run_check()

    # Should not create addon issue for VOLUME mounts not in config
    addon_issues = [
        issue
        for issue in coresys.resolution.issues
        if issue.context == ContextType.ADDON and issue.reference == "local_ssh"
    ]
    assert len(addon_issues) == 0, (
        "Add-on should not be flagged for VOLUME mounts not in config"
    )

    # No system issue should be created either if no containers have issues
    system_issues = [
        issue
        for issue in coresys.resolution.issues
        if issue.context == ContextType.SYSTEM
    ]
    assert len(system_issues) == 0


@pytest.mark.parametrize("folder", ["media", "share"])
@pytest.mark.usefixtures("install_addon_ssh")
async def test_addon_configured_mount_still_flagged(
    docker: DockerAPI, coresys: CoreSys, folder: str
):
    """Test that add-on with configured media/share mount is still flagged when propagation wrong."""
    # Keep the original configuration which includes media/share
    # SSH addon config already has media:rw and share:rw

    # Mock container that has supervisor-managed mount with wrong propagation
    mount = {
        "Type": "bind",
        "Source": f"/mnt/data/supervisor/{folder}",  # Supervisor-managed source
        "Destination": f"/{folder}",
        "Mode": "rw",
        "RW": True,
        "Propagation": "rprivate",  # Wrong propagation
    }

    async def mock_container_get(name):
        out = MagicMock(spec=DockerContainer)
        out.show.return_value = {
            "State": {
                "Status": "running",
                "Running": True,
            },
            "Mounts": [],
        }
        if name == "addon_local_ssh":
            out.show.return_value["Mounts"].append(mount)
        return out

    docker.containers.get = mock_container_get

    await coresys.core.set_state(CoreState.SETUP)
    with patch.object(DockerInterface, "is_running", return_value=True):
        await coresys.plugins.load()
        await coresys.homeassistant.load()
        await coresys.addons.load()

    docker_config = CheckDockerConfig(coresys)
    assert not coresys.resolution.issues

    # Run check - should create issue for add-on since mount was requested in config
    await docker_config.run_check()

    # Should have addon issue since the mount was configured
    addon_issues = [
        issue
        for issue in coresys.resolution.issues
        if issue.context == ContextType.ADDON and issue.reference == "local_ssh"
    ]
    assert len(addon_issues) == 1, (
        "Add-on should be flagged for configured mounts with wrong propagation"
    )


@pytest.mark.parametrize("folder", ["media", "share"])
async def test_addon_custom_target_path_flagged(
    docker: DockerAPI, coresys: CoreSys, install_addon_ssh: Addon, folder: str
):
    """Test that add-on with custom target path for media/share is properly checked."""
    # Configure add-on with custom target path
    custom_path = f"/custom/{folder}"
    mapping_type = "media" if folder == "media" else "share"
    install_addon_ssh.data["map"] = [
        {"type": mapping_type, "read_only": False, "path": custom_path},
    ]

    async def mock_container_get(name: str) -> MagicMock:
        """Mock container get with custom target path mount."""
        out = MagicMock(spec=DockerContainer)
        out.show.return_value = {
            "State": {
                "Status": "running",
                "Running": True,
            },
            "Mounts": [],
        }

        # Add mount with custom target path and wrong propagation
        mount = {
            "Source": f"/mnt/data/supervisor/{folder}",
            "Destination": custom_path,  # Custom target path
            "Propagation": "rprivate",  # Wrong propagation
        }

        if name == "addon_local_ssh":
            out.show.return_value["Mounts"].append(mount)
        return out

    docker.containers.get = mock_container_get

    await coresys.core.set_state(CoreState.SETUP)
    with patch.object(DockerInterface, "is_running", return_value=True):
        await coresys.plugins.load()
        await coresys.homeassistant.load()
        await coresys.addons.load()

    docker_config = CheckDockerConfig(coresys)
    assert not coresys.resolution.issues

    # Run check - should create issue for add-on with custom target path
    await docker_config.run_check()

    # Should have addon issue since the mount with custom path was configured
    addon_issues = [
        issue
        for issue in coresys.resolution.issues
        if issue.context == ContextType.ADDON and issue.reference == "local_ssh"
    ]
    assert len(addon_issues) == 1, (
        "Add-on should be flagged for configured mounts with custom paths and wrong propagation"
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
