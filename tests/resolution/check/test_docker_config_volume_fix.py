"""Test docker config check fix for VOLUME mounts."""

from unittest.mock import MagicMock, patch

import pytest

from supervisor.addons.addon import Addon
from supervisor.const import CoreState
from supervisor.coresys import CoreSys
from supervisor.docker.interface import DockerInterface
from supervisor.docker.manager import DockerAPI
from supervisor.resolution.checks.docker_config import CheckDockerConfig
from supervisor.resolution.const import ContextType


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

    def mock_container_get(name):
        out = MagicMock()
        out.status = "running"
        out.attrs = {"State": {}, "Mounts": []}
        if name in bad_config_names:
            out.attrs["Mounts"].append(mount)

        return out

    return mock_container_get


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

    # Should only have system issue, not addon issue
    addon_issues = [
        issue
        for issue in coresys.resolution.issues
        if issue.context == ContextType.ADDON and issue.reference == "local_ssh"
    ]
    assert len(addon_issues) == 0, (
        "Add-on should not be flagged for VOLUME mounts not in config"
    )

    # No system issue should be created either if no container has issues
    system_issues = [
        issue
        for issue in coresys.resolution.issues
        if issue.context == ContextType.SYSTEM
    ]
    # Update expectation - if no containers have issues, no system issue should be created
    assert len(system_issues) == 0


@pytest.mark.parametrize("folder", ["media", "share"])
async def test_addon_configured_mount_still_flagged(
    docker: DockerAPI, coresys: CoreSys, install_addon_ssh: Addon, folder: str
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

    def mock_container_get(name):
        out = MagicMock()
        out.status = "running"
        out.attrs = {"State": {}, "Mounts": []}
        if name == "addon_local_ssh":
            out.attrs["Mounts"].append(mount)
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
