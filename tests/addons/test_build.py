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
