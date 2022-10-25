"""Test addon manager."""

from unittest.mock import PropertyMock, patch

from awesomeversion import AwesomeVersion
import pytest

from supervisor.addons.addon import Addon
from supervisor.arch import CpuArch
from supervisor.coresys import CoreSys
from supervisor.docker.addon import DockerAddon
from supervisor.docker.interface import DockerInterface

from tests.common import load_json_fixture
from tests.const import TEST_ADDON_SLUG


@pytest.fixture(autouse=True)
async def fixture_mock_arch_disk() -> None:
    """Mock supported arch and disk space."""
    with patch(
        "shutil.disk_usage", return_value=(42, 42, 2 * (1024.0**3))
    ), patch.object(CpuArch, "supported", new=PropertyMock(return_value=["amd64"])):
        yield


async def test_image_added_removed_on_update(
    coresys: CoreSys, install_addon_ssh: Addon
):
    """Test image added or removed from addon config on update."""
    assert install_addon_ssh.need_update is False
    with patch(
        "supervisor.store.data.read_json_or_yaml_file",
        return_value=load_json_fixture("addon-config-add-image.json"),
    ):
        await coresys.store.data.update()

    assert install_addon_ssh.need_update is True
    assert install_addon_ssh.image == "local/amd64-addon-ssh"
    assert coresys.addons.store.get(TEST_ADDON_SLUG).image == "test/amd64-my-ssh-addon"

    with patch.object(DockerInterface, "_install") as install, patch.object(
        DockerAddon, "_build"
    ) as build:
        await install_addon_ssh.update()
        build.assert_not_called()
        install.assert_called_once_with(
            AwesomeVersion("10.0.0"), "test/amd64-my-ssh-addon", False, None
        )

    assert install_addon_ssh.need_update is False
    with patch(
        "supervisor.store.data.read_json_or_yaml_file",
        return_value=load_json_fixture("addon-config-remove-image.json"),
    ):
        await coresys.store.data.update()

    assert install_addon_ssh.need_update is True
    assert install_addon_ssh.image == "test/amd64-my-ssh-addon"
    assert coresys.addons.store.get(TEST_ADDON_SLUG).image == "local/amd64-addon-ssh"

    with patch.object(DockerInterface, "_install") as install, patch.object(
        DockerAddon, "_build"
    ) as build:
        await install_addon_ssh.update()
        build.assert_called_once_with(AwesomeVersion("11.0.0"))
        install.assert_not_called()
