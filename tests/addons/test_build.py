"""Test addon build."""

import base64
import json
from pathlib import Path
from unittest.mock import PropertyMock, patch

from awesomeversion import AwesomeVersion
import pytest

from supervisor.addons.addon import Addon
from supervisor.addons.build import AddonBuild
from supervisor.coresys import CoreSys
from supervisor.docker.const import DOCKER_HUB
from supervisor.exceptions import AddonBuildDockerfileMissingError

from tests.common import is_in_list


async def test_platform_set(coresys: CoreSys, install_addon_ssh: Addon):
    """Test platform set in container build args."""
    build = await AddonBuild(coresys, install_addon_ssh).load_config()

    with (
        patch.object(
            type(coresys.arch), "supported", new=PropertyMock(return_value=["amd64"])
        ),
        patch.object(
            type(coresys.arch), "default", new=PropertyMock(return_value="amd64")
        ),
        patch.object(
            type(coresys.config),
            "local_to_extern_path",
            return_value="/addon/path/on/host",
        ),
    ):
        args = await coresys.run_in_executor(
            build.get_docker_args, AwesomeVersion("latest"), "test-image:latest", None
        )

    assert is_in_list(["--platform", "linux/amd64"], args["command"])


async def test_dockerfile_evaluation(coresys: CoreSys, install_addon_ssh: Addon):
    """Test dockerfile path in container build args."""
    build = await AddonBuild(coresys, install_addon_ssh).load_config()

    with (
        patch.object(
            type(coresys.arch), "supported", new=PropertyMock(return_value=["amd64"])
        ),
        patch.object(
            type(coresys.arch), "default", new=PropertyMock(return_value="amd64")
        ),
        patch.object(
            type(coresys.config),
            "local_to_extern_path",
            return_value="/addon/path/on/host",
        ),
    ):
        args = await coresys.run_in_executor(
            build.get_docker_args, AwesomeVersion("latest"), "test-image:latest", None
        )

    assert is_in_list(["--file", "Dockerfile"], args["command"])
    assert str(await coresys.run_in_executor(build.get_dockerfile)).endswith(
        "fixtures/addons/local/ssh/Dockerfile"
    )
    assert build.arch == "amd64"


async def test_dockerfile_evaluation_arch(coresys: CoreSys, install_addon_ssh: Addon):
    """Test dockerfile arch evaluation in container build args."""
    build = await AddonBuild(coresys, install_addon_ssh).load_config()

    with (
        patch.object(
            type(coresys.arch), "supported", new=PropertyMock(return_value=["aarch64"])
        ),
        patch.object(
            type(coresys.arch), "default", new=PropertyMock(return_value="aarch64")
        ),
        patch.object(
            type(coresys.config),
            "local_to_extern_path",
            return_value="/addon/path/on/host",
        ),
    ):
        args = await coresys.run_in_executor(
            build.get_docker_args, AwesomeVersion("latest"), "test-image:latest", None
        )

    assert is_in_list(["--file", "Dockerfile.aarch64"], args["command"])
    assert str(await coresys.run_in_executor(build.get_dockerfile)).endswith(
        "fixtures/addons/local/ssh/Dockerfile.aarch64"
    )
    assert build.arch == "aarch64"


async def test_build_valid(coresys: CoreSys, install_addon_ssh: Addon):
    """Test platform set in docker args."""
    build = await AddonBuild(coresys, install_addon_ssh).load_config()
    with (
        patch.object(
            type(coresys.arch), "supported", new=PropertyMock(return_value=["aarch64"])
        ),
        patch.object(
            type(coresys.arch), "default", new=PropertyMock(return_value="aarch64")
        ),
    ):
        assert (await build.is_valid()) is None


async def test_build_invalid(coresys: CoreSys, install_addon_ssh: Addon):
    """Test build not supported because Dockerfile missing for specified architecture."""
    build = await AddonBuild(coresys, install_addon_ssh).load_config()
    with (
        patch.object(
            type(coresys.arch), "supported", new=PropertyMock(return_value=["amd64"])
        ),
        patch.object(
            type(coresys.arch), "default", new=PropertyMock(return_value="amd64")
        ),
        pytest.raises(AddonBuildDockerfileMissingError),
    ):
        await build.is_valid()


async def test_docker_config_no_registries(coresys: CoreSys, install_addon_ssh: Addon):
    """Test docker config generation when no registries configured."""
    build = await AddonBuild(coresys, install_addon_ssh).load_config()

    # No registries configured by default
    assert build.get_docker_config_json() is None


async def test_docker_config_no_matching_registry(
    coresys: CoreSys, install_addon_ssh: Addon
):
    """Test docker config generation when registry doesn't match base image."""
    build = await AddonBuild(coresys, install_addon_ssh).load_config()

    # Configure a registry that doesn't match the base image
    # pylint: disable-next=protected-access
    coresys.docker.config._data["registries"] = {
        "some.other.registry": {"username": "user", "password": "pass"}
    }

    with (
        patch.object(
            type(coresys.arch), "supported", new=PropertyMock(return_value=["amd64"])
        ),
        patch.object(
            type(coresys.arch), "default", new=PropertyMock(return_value="amd64")
        ),
    ):
        # Base image is ghcr.io/home-assistant/... which doesn't match
        assert build.get_docker_config_json() is None


async def test_docker_config_matching_registry(
    coresys: CoreSys, install_addon_ssh: Addon
):
    """Test docker config generation when registry matches base image."""
    build = await AddonBuild(coresys, install_addon_ssh).load_config()

    # Configure ghcr.io registry which matches the default base image
    # pylint: disable-next=protected-access
    coresys.docker.config._data["registries"] = {
        "ghcr.io": {"username": "testuser", "password": "testpass"}
    }

    with (
        patch.object(
            type(coresys.arch), "supported", new=PropertyMock(return_value=["amd64"])
        ),
        patch.object(
            type(coresys.arch), "default", new=PropertyMock(return_value="amd64")
        ),
    ):
        config_json = build.get_docker_config_json()
        assert config_json is not None

        config = json.loads(config_json)
        assert "auths" in config
        assert "ghcr.io" in config["auths"]

        # Verify base64-encoded credentials
        expected_auth = base64.b64encode(b"testuser:testpass").decode()
        assert config["auths"]["ghcr.io"]["auth"] == expected_auth


async def test_docker_config_docker_hub(coresys: CoreSys, install_addon_ssh: Addon):
    """Test docker config generation for Docker Hub registry."""
    build = await AddonBuild(coresys, install_addon_ssh).load_config()

    # Configure Docker Hub registry
    # pylint: disable-next=protected-access
    coresys.docker.config._data["registries"] = {
        DOCKER_HUB: {"username": "hubuser", "password": "hubpass"}
    }

    # Mock base_image to return a Docker Hub image (no registry prefix)
    with patch.object(
        type(build),
        "base_image",
        new=PropertyMock(return_value="library/alpine:latest"),
    ):
        config_json = build.get_docker_config_json()
        assert config_json is not None

        config = json.loads(config_json)
        # Docker Hub uses special URL as key
        assert "https://index.docker.io/v1/" in config["auths"]

        expected_auth = base64.b64encode(b"hubuser:hubpass").decode()
        assert config["auths"]["https://index.docker.io/v1/"]["auth"] == expected_auth


async def test_docker_args_with_config_path(coresys: CoreSys, install_addon_ssh: Addon):
    """Test docker args include config volume when path provided."""
    build = await AddonBuild(coresys, install_addon_ssh).load_config()

    with (
        patch.object(
            type(coresys.arch), "supported", new=PropertyMock(return_value=["amd64"])
        ),
        patch.object(
            type(coresys.arch), "default", new=PropertyMock(return_value="amd64")
        ),
        patch.object(
            type(coresys.config),
            "local_to_extern_path",
            side_effect=lambda p: f"/extern{p}",
        ),
    ):
        config_path = Path("/data/supervisor/tmp/config.json")
        args = await coresys.run_in_executor(
            build.get_docker_args,
            AwesomeVersion("latest"),
            "test-image:latest",
            config_path,
        )

    # Check that config is mounted
    assert "/extern/data/supervisor/tmp/config.json" in args["volumes"]
    assert (
        args["volumes"]["/extern/data/supervisor/tmp/config.json"]["bind"]
        == "/root/.docker/config.json"
    )
    assert args["volumes"]["/extern/data/supervisor/tmp/config.json"]["mode"] == "ro"


async def test_docker_args_without_config_path(
    coresys: CoreSys, install_addon_ssh: Addon
):
    """Test docker args don't include config volume when no path provided."""
    build = await AddonBuild(coresys, install_addon_ssh).load_config()

    with (
        patch.object(
            type(coresys.arch), "supported", new=PropertyMock(return_value=["amd64"])
        ),
        patch.object(
            type(coresys.arch), "default", new=PropertyMock(return_value="amd64")
        ),
        patch.object(
            type(coresys.config),
            "local_to_extern_path",
            return_value="/addon/path/on/host",
        ),
    ):
        args = await coresys.run_in_executor(
            build.get_docker_args, AwesomeVersion("latest"), "test-image:latest", None
        )

    # Only docker socket and addon path should be mounted
    assert len(args["volumes"]) == 2
    # Verify no docker config mount
    for bind in args["volumes"].values():
        assert bind["bind"] != "/root/.docker/config.json"
