"""Test addon build."""

from unittest.mock import PropertyMock, patch

from awesomeversion import AwesomeVersion

from supervisor.addons.addon import Addon
from supervisor.addons.build import AddonBuild
from supervisor.coresys import CoreSys

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
        patch.object(build, "get_addon_host_path", return_value="/addon/path/on/host"),
    ):
        args = await coresys.run_in_executor(
            build.get_docker_args, AwesomeVersion("latest"), "test-image:latest"
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
        patch.object(build, "get_addon_host_path", return_value="/addon/path/on/host"),
    ):
        args = await coresys.run_in_executor(
            build.get_docker_args, AwesomeVersion("latest"), "test-image:latest"
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
        patch.object(build, "get_addon_host_path", return_value="/addon/path/on/host"),
    ):
        args = await coresys.run_in_executor(
            build.get_docker_args, AwesomeVersion("latest"), "test-image:latest"
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
        assert await build.is_valid()


async def test_build_invalid(coresys: CoreSys, install_addon_ssh: Addon):
    """Test platform set in docker args."""
    build = await AddonBuild(coresys, install_addon_ssh).load_config()
    with (
        patch.object(
            type(coresys.arch), "supported", new=PropertyMock(return_value=["amd64"])
        ),
        patch.object(
            type(coresys.arch), "default", new=PropertyMock(return_value="amd64")
        ),
    ):
        assert not await build.is_valid()
