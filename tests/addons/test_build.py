"""Test addon build."""

import base64
import json
import logging
from pathlib import Path, PurePath
from unittest.mock import PropertyMock, patch

from awesomeversion import AwesomeVersion
import pytest

from supervisor.addons.addon import Addon
from supervisor.addons.build import AddonBuild
from supervisor.coresys import CoreSys
from supervisor.docker.const import DOCKER_HUB, MountType
from supervisor.exceptions import AddonBuildDockerfileMissingError

from tests.common import is_in_list


def _is_build_arg_in_command(command: list[str], arg_name: str) -> bool:
    """Check if a build arg is in docker command."""
    return f"--build-arg {arg_name}=" in " ".join(command)


def _is_label_in_command(
    command: list[str], label_name: str, label_value: str = ""
) -> bool:
    """Check if a label is in docker command."""
    return f"--label {label_name}={label_value}" in " ".join(command)


async def test_platform_set(coresys: CoreSys, install_addon_ssh: Addon):
    """Test platform set in container build args."""
    build = await AddonBuild.create(coresys, install_addon_ssh)

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
            return_value=PurePath("/addon/path/on/host"),
        ),
    ):
        args = await coresys.run_in_executor(
            build.get_docker_args, AwesomeVersion("latest"), "test-image:latest", None
        )

    assert is_in_list(["--platform", "linux/amd64"], args["command"])


async def test_dockerfile_evaluation(coresys: CoreSys, install_addon_ssh: Addon):
    """Test dockerfile path in container build args."""
    build = await AddonBuild.create(coresys, install_addon_ssh)

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
            return_value=PurePath("/addon/path/on/host"),
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
    build = await AddonBuild.create(coresys, install_addon_ssh)

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
            return_value=PurePath("/addon/path/on/host"),
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
    build = await AddonBuild.create(coresys, install_addon_ssh)
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
    build = await AddonBuild.create(coresys, install_addon_ssh)
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
    build = await AddonBuild.create(coresys, install_addon_ssh)

    # No registries configured by default
    assert build.get_docker_config_json() is None


async def test_docker_config_all_registries(coresys: CoreSys, install_addon_ssh: Addon):
    """Test docker config includes all configured registries."""
    build = await AddonBuild.create(coresys, install_addon_ssh)

    # pylint: disable-next=protected-access
    coresys.docker.config._data["registries"] = {
        "ghcr.io": {"username": "testuser", "password": "testpass"},
        "some.other.registry": {"username": "user", "password": "pass"},
    }

    config_json = build.get_docker_config_json()
    assert config_json is not None

    config = json.loads(config_json)
    assert "ghcr.io" in config["auths"]
    assert "some.other.registry" in config["auths"]

    expected_ghcr = base64.b64encode(b"testuser:testpass").decode()
    assert config["auths"]["ghcr.io"]["auth"] == expected_ghcr

    expected_other = base64.b64encode(b"user:pass").decode()
    assert config["auths"]["some.other.registry"]["auth"] == expected_other


async def test_docker_config_docker_hub(coresys: CoreSys, install_addon_ssh: Addon):
    """Test docker config uses special URL key for Docker Hub."""
    build = await AddonBuild.create(coresys, install_addon_ssh)

    # pylint: disable-next=protected-access
    coresys.docker.config._data["registries"] = {
        DOCKER_HUB: {"username": "hubuser", "password": "hubpass"}
    }

    config_json = build.get_docker_config_json()
    assert config_json is not None

    config = json.loads(config_json)
    assert "https://index.docker.io/v1/" in config["auths"]

    expected_auth = base64.b64encode(b"hubuser:hubpass").decode()
    assert config["auths"]["https://index.docker.io/v1/"]["auth"] == expected_auth


async def test_docker_args_with_config_path(coresys: CoreSys, install_addon_ssh: Addon):
    """Test docker args include config volume when path provided."""
    build = await AddonBuild.create(coresys, install_addon_ssh)

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
            side_effect=lambda p: PurePath(f"/extern{p}"),
        ),
    ):
        config_path = Path("/data/supervisor/tmp/config.json")
        args = await coresys.run_in_executor(
            build.get_docker_args,
            AwesomeVersion("latest"),
            "test-image:latest",
            config_path,
        )

    # Check that config is mounted (3 mounts: docker socket, addon path, config)
    assert len(args["mounts"]) == 3
    config_mount = next(
        m for m in args["mounts"] if m.target == "/root/.docker/config.json"
    )
    assert config_mount.source == "/extern/data/supervisor/tmp/config.json"
    assert config_mount.read_only is True
    assert config_mount.type == MountType.BIND


async def test_docker_args_without_config_path(
    coresys: CoreSys, install_addon_ssh: Addon
):
    """Test docker args don't include config volume when no path provided."""
    build = await AddonBuild.create(coresys, install_addon_ssh)

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
            return_value=PurePath("/addon/path/on/host"),
        ),
    ):
        args = await coresys.run_in_executor(
            build.get_docker_args, AwesomeVersion("latest"), "test-image:latest", None
        )

    # Only docker socket and addon path should be mounted
    assert len(args["mounts"]) == 2
    # Verify no docker config mount
    for mount in args["mounts"]:
        assert mount.target != "/root/.docker/config.json"


async def test_build_file_deprecation_warning(
    coresys: CoreSys, install_addon_ssh: Addon, caplog: pytest.LogCaptureFixture
):
    """Test deprecation warning is logged when build.yaml exists."""
    with caplog.at_level(logging.WARNING):
        await AddonBuild.create(coresys, install_addon_ssh)
    assert "uses build.yaml which is deprecated" in caplog.text


async def test_no_build_file_no_deprecation_warning(
    coresys: CoreSys,
    install_addon_ssh: Addon,
    tmp_path: Path,
    caplog: pytest.LogCaptureFixture,
):
    """Test no deprecation warning when no build file exists."""
    dockerfile = tmp_path / "Dockerfile"
    dockerfile.write_text("ARG BUILD_FROM=ghcr.io/home-assistant/base:latest\n")

    with (
        patch.object(
            type(install_addon_ssh),
            "path_location",
            new=PropertyMock(return_value=tmp_path),
        ),
        caplog.at_level(logging.WARNING),
    ):
        await AddonBuild.create(coresys, install_addon_ssh)
    assert "uses build.yaml which is deprecated" not in caplog.text


async def test_no_build_yaml_base_image_none(
    coresys: CoreSys, install_addon_ssh: Addon, tmp_path: Path
):
    """Test base_image is None when no build file exists."""
    dockerfile = tmp_path / "Dockerfile"
    dockerfile.write_text("ARG BUILD_FROM=ghcr.io/home-assistant/base:latest\n")

    with patch.object(
        type(install_addon_ssh),
        "path_location",
        new=PropertyMock(return_value=tmp_path),
    ):
        build = await AddonBuild.create(coresys, install_addon_ssh)
        assert build.base_image is None


async def test_no_build_yaml_no_build_from_arg(
    coresys: CoreSys, install_addon_ssh: Addon, tmp_path: Path
):
    """Test BUILD_FROM is not in docker args when no build file exists."""
    dockerfile = tmp_path / "Dockerfile"
    dockerfile.write_text("ARG BUILD_FROM=ghcr.io/home-assistant/base:latest\n")

    with (
        patch.object(
            type(install_addon_ssh),
            "path_location",
            new=PropertyMock(return_value=tmp_path),
        ),
        patch.object(
            type(coresys.arch), "supported", new=PropertyMock(return_value=["amd64"])
        ),
        patch.object(
            type(coresys.arch), "default", new=PropertyMock(return_value="amd64")
        ),
        patch.object(
            type(coresys.config),
            "local_to_extern_path",
            return_value=PurePath("/addon/path/on/host"),
        ),
    ):
        build = await AddonBuild.create(coresys, install_addon_ssh)
        args = await coresys.run_in_executor(
            build.get_docker_args, AwesomeVersion("1.0.0"), "test-image:1.0.0", None
        )

    assert not _is_build_arg_in_command(args["command"], "BUILD_FROM")
    assert _is_build_arg_in_command(args["command"], "BUILD_VERSION")
    assert _is_build_arg_in_command(args["command"], "BUILD_ARCH")


async def test_build_yaml_passes_build_from(coresys: CoreSys, install_addon_ssh: Addon):
    """Test BUILD_FROM is in docker args when build.yaml exists."""
    build = await AddonBuild.create(coresys, install_addon_ssh)

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
            return_value=PurePath("/addon/path/on/host"),
        ),
    ):
        args = await coresys.run_in_executor(
            build.get_docker_args, AwesomeVersion("1.0.0"), "test-image:1.0.0", None
        )

    assert _is_build_arg_in_command(args["command"], "BUILD_FROM")
    assert _is_build_arg_in_command(args["command"], "BUILD_VERSION")
    assert _is_build_arg_in_command(args["command"], "BUILD_ARCH")


async def test_no_build_yaml_docker_config_includes_registries(
    coresys: CoreSys, install_addon_ssh: Addon, tmp_path: Path
):
    """Test registries are included in docker config even without build file."""
    dockerfile = tmp_path / "Dockerfile"
    dockerfile.write_text("ARG BUILD_FROM=ghcr.io/home-assistant/base:latest\n")

    # pylint: disable-next=protected-access
    coresys.docker.config._data["registries"] = {
        "ghcr.io": {"username": "ghcr_user", "password": "ghcr_pass"},
    }

    with patch.object(
        type(install_addon_ssh),
        "path_location",
        new=PropertyMock(return_value=tmp_path),
    ):
        build = await AddonBuild.create(coresys, install_addon_ssh)
        config_json = build.get_docker_config_json()
        assert config_json is not None

        config = json.loads(config_json)
        assert "ghcr.io" in config["auths"]


async def test_labels_include_name_and_description(
    coresys: CoreSys, install_addon_ssh: Addon
):
    """Test name and description labels are included when addon has them set."""
    build = await AddonBuild.create(coresys, install_addon_ssh)

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
            return_value=PurePath("/addon/path/on/host"),
        ),
    ):
        args = await coresys.run_in_executor(
            build.get_docker_args, AwesomeVersion("1.0.0"), "test-image:1.0.0", None
        )

    assert _is_label_in_command(args["command"], "io.hass.name", "Terminal & SSH")
    assert _is_label_in_command(
        args["command"],
        "io.hass.description",
        "Allow logging in remotely to Home Assistant using SSH",
    )


async def test_labels_omit_name_and_description_when_empty(
    coresys: CoreSys, install_addon_ssh: Addon
):
    """Test name and description labels are omitted when addon has empty values."""
    build = await AddonBuild.create(coresys, install_addon_ssh)

    with (
        patch.object(
            type(install_addon_ssh), "name", new=PropertyMock(return_value="")
        ),
        patch.object(
            type(install_addon_ssh),
            "description",
            new=PropertyMock(return_value=""),
        ),
        patch.object(
            type(coresys.arch), "supported", new=PropertyMock(return_value=["amd64"])
        ),
        patch.object(
            type(coresys.arch), "default", new=PropertyMock(return_value="amd64")
        ),
        patch.object(
            type(coresys.config),
            "local_to_extern_path",
            return_value=PurePath("/addon/path/on/host"),
        ),
    ):
        args = await coresys.run_in_executor(
            build.get_docker_args, AwesomeVersion("1.0.0"), "test-image:1.0.0", None
        )

    assert not _is_label_in_command(args["command"], "io.hass.name")
    assert not _is_label_in_command(args["command"], "io.hass.description")
    # Core labels should still be present
    assert _is_label_in_command(args["command"], "io.hass.version", "1.0.0")
    assert _is_label_in_command(args["command"], "io.hass.arch", "amd64")
    assert _is_label_in_command(args["command"], "io.hass.type", "app")
