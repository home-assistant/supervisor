"""Test addon build."""
from unittest.mock import PropertyMock, patch

from awesomeversion import AwesomeVersion

from supervisor.addons.addon import Addon
from supervisor.addons.build import AddonBuild
from supervisor.coresys import CoreSys


async def test_platform_set(coresys: CoreSys, install_addon_ssh: Addon):
    """Test platform set in docker args."""
    build = AddonBuild(coresys, install_addon_ssh)
    with patch.object(
        type(coresys.arch), "supported", new=PropertyMock(return_value=["amd64"])
    ), patch.object(
        type(coresys.arch), "default", new=PropertyMock(return_value="amd64")
    ):
        args = build.get_docker_args(AwesomeVersion("latest"))

    assert args["platform"] == "linux/amd64"


async def test_dockerfile_evaluation(coresys: CoreSys, install_addon_ssh: Addon):
    """Test platform set in docker args."""
    build = AddonBuild(coresys, install_addon_ssh)
    with patch.object(
        type(coresys.arch), "supported", new=PropertyMock(return_value=["amd64"])
    ), patch.object(
        type(coresys.arch), "default", new=PropertyMock(return_value="amd64")
    ):
        args = build.get_docker_args(AwesomeVersion("latest"))

    assert args["dockerfile"].endswith("fixtures/addons/local/ssh/Dockerfile")
    assert str(build.dockerfile).endswith("fixtures/addons/local/ssh/Dockerfile")
    assert build.arch == "amd64"


async def test_dockerfile_evaluation_arch(coresys: CoreSys, install_addon_ssh: Addon):
    """Test platform set in docker args."""
    build = AddonBuild(coresys, install_addon_ssh)
    with patch.object(
        type(coresys.arch), "supported", new=PropertyMock(return_value=["aarch64"])
    ), patch.object(
        type(coresys.arch), "default", new=PropertyMock(return_value="aarch64")
    ):
        args = build.get_docker_args(AwesomeVersion("latest"))

    assert args["dockerfile"].endswith("fixtures/addons/local/ssh/Dockerfile.aarch64")
    assert str(build.dockerfile).endswith(
        "fixtures/addons/local/ssh/Dockerfile.aarch64"
    )
    assert build.arch == "aarch64"


async def test_build_valid(coresys: CoreSys, install_addon_ssh: Addon):
    """Test platform set in docker args."""
    build = AddonBuild(coresys, install_addon_ssh)
    with patch.object(
        type(coresys.arch), "supported", new=PropertyMock(return_value=["aarch64"])
    ), patch.object(
        type(coresys.arch), "default", new=PropertyMock(return_value="aarch64")
    ):
        assert build.is_valid


async def test_build_invalid(coresys: CoreSys, install_addon_ssh: Addon):
    """Test platform set in docker args."""
    build = AddonBuild(coresys, install_addon_ssh)
    with patch.object(
        type(coresys.arch), "supported", new=PropertyMock(return_value=["amd64"])
    ), patch.object(
        type(coresys.arch), "default", new=PropertyMock(return_value="amd64")
    ):
        assert not build.is_valid
