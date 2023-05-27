"""Test addon manager."""

import asyncio
from unittest.mock import AsyncMock, MagicMock, Mock, PropertyMock, patch

from awesomeversion import AwesomeVersion
import pytest

from supervisor.addons.addon import Addon
from supervisor.arch import CpuArch
from supervisor.const import AddonBoot, AddonStartup, AddonState
from supervisor.coresys import CoreSys
from supervisor.docker.addon import DockerAddon
from supervisor.docker.interface import DockerInterface
from supervisor.exceptions import (
    AddonConfigurationError,
    AddonsError,
    DockerAPIError,
    DockerNotFound,
)
from supervisor.plugins.dns import PluginDns
from supervisor.utils import check_exception_chain

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


@pytest.mark.parametrize("err", [DockerAPIError, DockerNotFound])
async def test_addon_boot_system_error(
    coresys: CoreSys, install_addon_ssh: Addon, capture_exception: Mock, err
):
    """Test system errors during addon boot."""
    install_addon_ssh.boot = AddonBoot.AUTO
    with patch.object(Addon, "write_options"), patch.object(
        DockerAddon, "run", side_effect=err
    ):
        await coresys.addons.boot(AddonStartup.APPLICATION)

    assert install_addon_ssh.boot == AddonBoot.MANUAL
    capture_exception.assert_not_called()


async def test_addon_boot_user_error(
    coresys: CoreSys, install_addon_ssh: Addon, capture_exception: Mock
):
    """Test user error during addon boot."""
    install_addon_ssh.boot = AddonBoot.AUTO
    with patch.object(Addon, "write_options", side_effect=AddonConfigurationError):
        await coresys.addons.boot(AddonStartup.APPLICATION)

    assert install_addon_ssh.boot == AddonBoot.MANUAL
    capture_exception.assert_not_called()


async def test_addon_boot_other_error(
    coresys: CoreSys, install_addon_ssh: Addon, capture_exception: Mock
):
    """Test other errors captured during addon boot."""
    install_addon_ssh.boot = AddonBoot.AUTO
    err = OSError()
    with patch.object(Addon, "write_options"), patch.object(
        DockerAddon, "run", side_effect=err
    ):
        await coresys.addons.boot(AddonStartup.APPLICATION)

    assert install_addon_ssh.boot == AddonBoot.AUTO
    capture_exception.assert_called_once_with(err)


async def test_addon_shutdown_error(
    coresys: CoreSys, install_addon_ssh: Addon, capture_exception: Mock
):
    """Test errors captured during addon shutdown."""
    install_addon_ssh.state = AddonState.STARTED
    with patch.object(DockerAddon, "stop", side_effect=DockerNotFound()):
        await coresys.addons.shutdown(AddonStartup.APPLICATION)

    assert install_addon_ssh.state == AddonState.ERROR
    capture_exception.assert_called_once()
    assert check_exception_chain(
        capture_exception.call_args[0][0], (AddonsError, DockerNotFound)
    )


async def test_addon_uninstall_removes_discovery(
    coresys: CoreSys, install_addon_ssh: Addon
):
    """Test discovery messages removed when addon uninstalled."""
    assert coresys.discovery.list_messages == []

    message = coresys.discovery.send(
        install_addon_ssh, "mqtt", {"host": "localhost", "port": 1883}
    )
    assert message.addon == TEST_ADDON_SLUG
    assert message.service == "mqtt"
    assert coresys.discovery.list_messages == [message]

    coresys.homeassistant.api.ensure_access_token = AsyncMock()
    coresys.websession.delete = MagicMock()

    await coresys.addons.uninstall(TEST_ADDON_SLUG)
    await asyncio.sleep(0)
    coresys.websession.delete.assert_called_once()
    assert (
        coresys.websession.delete.call_args.args[0]
        == f"http://172.30.32.1:8123/api/hassio_push/discovery/{message.uuid}"
    )
    assert coresys.websession.delete.call_args.kwargs["json"] == {
        "addon": TEST_ADDON_SLUG,
        "service": "mqtt",
        "uuid": message.uuid,
    }

    assert coresys.addons.installed == []
    assert coresys.discovery.list_messages == []


async def test_load(
    coresys: CoreSys, install_addon_ssh: Addon, caplog: pytest.LogCaptureFixture
):
    """Test addon manager load."""
    caplog.clear()

    with patch.object(DockerInterface, "attach") as attach, patch.object(
        PluginDns, "write_hosts"
    ) as write_hosts:
        await coresys.addons.load()

        attach.assert_called_once_with(version=AwesomeVersion("9.2.1"))
        write_hosts.assert_called_once()

    assert "Found 1 installed add-ons" in caplog.text
