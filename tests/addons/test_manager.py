"""Test addon manager."""

import asyncio
from unittest.mock import AsyncMock, MagicMock, Mock, PropertyMock, patch

from awesomeversion import AwesomeVersion
import pytest

from supervisor.addons.addon import Addon
from supervisor.arch import CpuArch
from supervisor.const import AddonBoot, AddonStartup, AddonState, BusEvent
from supervisor.coresys import CoreSys
from supervisor.docker.addon import DockerAddon
from supervisor.docker.const import ContainerState
from supervisor.docker.interface import DockerInterface
from supervisor.docker.monitor import DockerContainerStateEvent
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


@pytest.fixture(autouse=True)
async def fixture_remove_wait_boot(coresys: CoreSys) -> None:
    """Remove default wait boot time for tests."""
    coresys.config.wait_boot = 0


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

    with patch.object(DockerInterface, "install") as install, patch.object(
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

    with patch.object(DockerInterface, "install") as install, patch.object(
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


async def test_boot_waits_for_addons(
    coresys: CoreSys,
    install_addon_ssh: Addon,
    container,
    tmp_supervisor_data,
    path_extern,
):
    """Test addon manager boot waits for addons."""
    install_addon_ssh.path_data.mkdir()
    await install_addon_ssh.load()
    await asyncio.sleep(0)
    assert install_addon_ssh.state == AddonState.STOPPED

    addon_state: AddonState | None = None

    async def fire_container_event(*args, **kwargs):
        nonlocal addon_state

        addon_state = install_addon_ssh.state
        coresys.bus.fire_event(
            BusEvent.DOCKER_CONTAINER_STATE_CHANGE,
            DockerContainerStateEvent(
                name=f"addon_{TEST_ADDON_SLUG}",
                state=ContainerState.RUNNING,
                id="abc123",
                time=1,
            ),
        )

    with patch.object(DockerAddon, "run", new=fire_container_event):
        await coresys.addons.boot(AddonStartup.APPLICATION)

    assert addon_state == AddonState.STOPPED
    assert install_addon_ssh.state == AddonState.STARTED


@pytest.mark.parametrize("status", ["running", "stopped"])
async def test_update(
    coresys: CoreSys,
    install_addon_ssh: Addon,
    container: MagicMock,
    status: str,
    tmp_supervisor_data,
    path_extern,
):
    """Test addon update."""
    container.status = status
    install_addon_ssh.path_data.mkdir()
    await install_addon_ssh.load()
    with patch(
        "supervisor.store.data.read_json_or_yaml_file",
        return_value=load_json_fixture("addon-config-add-image.json"),
    ):
        await coresys.store.data.update()

    assert install_addon_ssh.need_update is True

    with patch.object(DockerInterface, "install"), patch.object(
        DockerAddon, "is_running", return_value=False
    ):
        start_task = await coresys.addons.update(TEST_ADDON_SLUG)

    assert bool(start_task) is (status == "running")


@pytest.mark.parametrize("status", ["running", "stopped"])
async def test_rebuild(
    coresys: CoreSys,
    install_addon_ssh: Addon,
    container: MagicMock,
    status: str,
    tmp_supervisor_data,
    path_extern,
):
    """Test addon rebuild."""
    container.status = status
    install_addon_ssh.path_data.mkdir()
    await install_addon_ssh.load()

    with patch.object(DockerAddon, "_build"), patch.object(
        DockerAddon, "is_running", return_value=False
    ), patch.object(Addon, "need_build", new=PropertyMock(return_value=True)):
        start_task = await coresys.addons.rebuild(TEST_ADDON_SLUG)

    assert bool(start_task) is (status == "running")


async def test_start_wait_cancel_on_uninstall(
    coresys: CoreSys,
    install_addon_ssh: Addon,
    container: MagicMock,
    caplog: pytest.LogCaptureFixture,
    tmp_supervisor_data,
    path_extern,
) -> None:
    """Test the addon wait task is cancelled when addon is uninstalled."""
    install_addon_ssh.path_data.mkdir()
    container.attrs["Config"] = {"Healthcheck": "exists"}
    await install_addon_ssh.load()
    await asyncio.sleep(0)
    assert install_addon_ssh.state == AddonState.STOPPED

    start_task = asyncio.create_task(await install_addon_ssh.start())
    assert start_task

    coresys.bus.fire_event(
        BusEvent.DOCKER_CONTAINER_STATE_CHANGE,
        DockerContainerStateEvent(
            name=f"addon_{TEST_ADDON_SLUG}",
            state=ContainerState.RUNNING,
            id="abc123",
            time=1,
        ),
    )
    await asyncio.sleep(0.01)

    assert not start_task.done()
    assert install_addon_ssh.state == AddonState.STARTUP

    caplog.clear()
    await coresys.addons.uninstall(TEST_ADDON_SLUG)
    await asyncio.sleep(0.01)
    assert start_task.done()
    assert "Wait for addon startup task cancelled" in caplog.text
