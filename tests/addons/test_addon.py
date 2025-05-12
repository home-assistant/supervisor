"""Test Home Assistant Add-ons."""

import asyncio
from datetime import timedelta
import errno
from pathlib import Path
from unittest.mock import MagicMock, PropertyMock, patch

from awesomeversion import AwesomeVersion
from docker.errors import DockerException, ImageNotFound, NotFound
import pytest
from securetar import SecureTarFile

from supervisor.addons.addon import Addon
from supervisor.addons.const import AddonBackupMode
from supervisor.addons.model import AddonModel
from supervisor.const import AddonBoot, AddonState, BusEvent
from supervisor.coresys import CoreSys
from supervisor.docker.addon import DockerAddon
from supervisor.docker.const import ContainerState
from supervisor.docker.monitor import DockerContainerStateEvent
from supervisor.exceptions import AddonsError, AddonsJobError, AudioUpdateError
from supervisor.hardware.helper import HwHelper
from supervisor.ingress import Ingress
from supervisor.store.repository import Repository
from supervisor.utils.dt import utcnow

from .test_manager import BOOT_FAIL_ISSUE, BOOT_FAIL_SUGGESTIONS

from tests.common import get_fixture_path
from tests.const import TEST_ADDON_SLUG


def _fire_test_event(coresys: CoreSys, name: str, state: ContainerState):
    """Fire a test event."""
    coresys.bus.fire_event(
        BusEvent.DOCKER_CONTAINER_STATE_CHANGE,
        DockerContainerStateEvent(
            name=name,
            state=state,
            id="abc123",
            time=1,
        ),
    )


def test_options_merge(coresys: CoreSys, install_addon_ssh: Addon) -> None:
    """Test options merge."""
    addon = coresys.addons.get(TEST_ADDON_SLUG)

    assert addon.options == {
        "apks": [],
        "authorized_keys": [],
        "password": "",
        "server": {"tcp_forwarding": False},
    }

    addon.options = {"password": "test"}
    assert addon.persist["options"] == {"password": "test"}
    assert addon.options == {
        "apks": [],
        "authorized_keys": [],
        "password": "test",
        "server": {"tcp_forwarding": False},
    }

    addon.options = {"password": "test", "apks": ["gcc"]}
    assert addon.persist["options"] == {"password": "test", "apks": ["gcc"]}
    assert addon.options == {
        "apks": ["gcc"],
        "authorized_keys": [],
        "password": "test",
        "server": {"tcp_forwarding": False},
    }

    addon.options = {"password": "test", "server": {"tcp_forwarding": True}}
    assert addon.persist["options"] == {
        "password": "test",
        "server": {"tcp_forwarding": True},
    }
    assert addon.options == {
        "apks": [],
        "authorized_keys": [],
        "password": "test",
        "server": {"tcp_forwarding": True},
    }

    # Test overwrite
    test = addon.options
    test["server"]["test"] = 1
    assert addon.options == {
        "apks": [],
        "authorized_keys": [],
        "password": "test",
        "server": {"tcp_forwarding": True},
    }
    addon.options = {"password": "test", "server": {"tcp_forwarding": True}}


async def test_addon_state_listener(coresys: CoreSys, install_addon_ssh: Addon) -> None:
    """Test addon is setting state from docker events."""
    with patch.object(DockerAddon, "attach"):
        await install_addon_ssh.load()

    assert install_addon_ssh.state == AddonState.UNKNOWN

    with patch.object(Addon, "watchdog_container"):
        _fire_test_event(coresys, f"addon_{TEST_ADDON_SLUG}", ContainerState.RUNNING)
        await asyncio.sleep(0)
        assert install_addon_ssh.state == AddonState.STARTED

        _fire_test_event(coresys, f"addon_{TEST_ADDON_SLUG}", ContainerState.STOPPED)
        await asyncio.sleep(0)
        assert install_addon_ssh.state == AddonState.STOPPED

        _fire_test_event(coresys, f"addon_{TEST_ADDON_SLUG}", ContainerState.HEALTHY)
        await asyncio.sleep(0)
        assert install_addon_ssh.state == AddonState.STARTED

        _fire_test_event(coresys, f"addon_{TEST_ADDON_SLUG}", ContainerState.FAILED)
        await asyncio.sleep(0)
        assert install_addon_ssh.state == AddonState.ERROR

        # Test other addons are ignored
        _fire_test_event(coresys, "addon_local_non_installed", ContainerState.RUNNING)
        await asyncio.sleep(0)
        assert install_addon_ssh.state == AddonState.ERROR


async def test_addon_watchdog(coresys: CoreSys, install_addon_ssh: Addon) -> None:
    """Test addon watchdog works correctly."""
    with patch.object(DockerAddon, "attach"):
        await install_addon_ssh.load()

    install_addon_ssh.watchdog = True
    install_addon_ssh._manual_stop = False  # pylint: disable=protected-access

    with (
        patch.object(Addon, "restart") as restart,
        patch.object(Addon, "start") as start,
        patch.object(DockerAddon, "current_state") as current_state,
    ):
        # Restart if it becomes unhealthy
        current_state.return_value = ContainerState.UNHEALTHY
        _fire_test_event(coresys, f"addon_{TEST_ADDON_SLUG}", ContainerState.UNHEALTHY)
        await asyncio.sleep(0)
        restart.assert_called_once()
        start.assert_not_called()

        restart.reset_mock()

        # Rebuild if it failed
        current_state.return_value = ContainerState.FAILED
        with patch.object(DockerAddon, "stop") as stop:
            _fire_test_event(coresys, f"addon_{TEST_ADDON_SLUG}", ContainerState.FAILED)
            await asyncio.sleep(0)
            stop.assert_called_once_with(remove_container=True)
            restart.assert_not_called()
            start.assert_called_once()

        start.reset_mock()

        # Do not process event if container state has changed since fired
        current_state.return_value = ContainerState.HEALTHY
        _fire_test_event(coresys, f"addon_{TEST_ADDON_SLUG}", ContainerState.FAILED)
        await asyncio.sleep(0)
        restart.assert_not_called()
        start.assert_not_called()

        # Other addons ignored
        current_state.return_value = ContainerState.UNHEALTHY
        _fire_test_event(coresys, "addon_local_non_installed", ContainerState.UNHEALTHY)
        await asyncio.sleep(0)
        restart.assert_not_called()
        start.assert_not_called()


async def test_watchdog_on_stop(coresys: CoreSys, install_addon_ssh: Addon) -> None:
    """Test addon watchdog restarts addon on stop if not manual."""
    with patch.object(DockerAddon, "attach"):
        await install_addon_ssh.load()

    install_addon_ssh.watchdog = True

    with (
        patch.object(Addon, "restart") as restart,
        patch.object(
            DockerAddon,
            "current_state",
            return_value=ContainerState.STOPPED,
        ),
        patch.object(DockerAddon, "stop"),
    ):
        # Do not restart when addon stopped by user
        _fire_test_event(coresys, f"addon_{TEST_ADDON_SLUG}", ContainerState.RUNNING)
        await asyncio.sleep(0)
        await install_addon_ssh.stop()
        _fire_test_event(coresys, f"addon_{TEST_ADDON_SLUG}", ContainerState.STOPPED)
        await asyncio.sleep(0)
        restart.assert_not_called()

        # Do restart addon if it stops and user didn't do it
        _fire_test_event(coresys, f"addon_{TEST_ADDON_SLUG}", ContainerState.RUNNING)
        await asyncio.sleep(0)
        _fire_test_event(coresys, f"addon_{TEST_ADDON_SLUG}", ContainerState.STOPPED)
        await asyncio.sleep(0)
        restart.assert_called_once()


async def test_listener_attached_on_install(
    coresys: CoreSys, mock_amd64_arch_supported: None, repository
):
    """Test events listener attached on addon install."""
    coresys.hardware.disk.get_disk_free_space = lambda x: 5000
    container_collection = MagicMock()
    container_collection.get.side_effect = DockerException()
    with (
        patch(
            "supervisor.docker.manager.DockerAPI.containers",
            new=PropertyMock(return_value=container_collection),
        ),
        patch("pathlib.Path.is_dir", return_value=True),
        patch(
            "supervisor.addons.addon.Addon.need_build",
            new=PropertyMock(return_value=False),
        ),
        patch(
            "supervisor.addons.model.AddonModel.with_ingress",
            new=PropertyMock(return_value=False),
        ),
    ):
        await coresys.addons.install(TEST_ADDON_SLUG)

    _fire_test_event(coresys, f"addon_{TEST_ADDON_SLUG}", ContainerState.RUNNING)
    await asyncio.sleep(0)
    assert coresys.addons.get(TEST_ADDON_SLUG).state == AddonState.STARTUP


@pytest.mark.parametrize(
    "boot_timedelta,restart_count", [(timedelta(), 1), (timedelta(days=1), 0)]
)
async def test_watchdog_during_attach(
    coresys: CoreSys,
    repository: Repository,
    boot_timedelta: timedelta,
    restart_count: int,
):
    """Test host reboot treated as manual stop but not supervisor restart."""
    store = coresys.addons.store[TEST_ADDON_SLUG]
    await coresys.addons.data.install(store)

    with (
        patch.object(Addon, "restart") as restart,
        patch.object(HwHelper, "last_boot", return_value=utcnow()),
        patch.object(DockerAddon, "attach"),
        patch.object(
            DockerAddon,
            "current_state",
            return_value=ContainerState.STOPPED,
        ),
    ):
        coresys.config.last_boot = (
            await coresys.hardware.helper.last_boot() + boot_timedelta
        )
        addon = Addon(coresys, store.slug)
        coresys.addons.local[addon.slug] = addon
        addon.watchdog = True

        await addon.load()
        _fire_test_event(coresys, f"addon_{TEST_ADDON_SLUG}", ContainerState.STOPPED)
        await asyncio.sleep(0)

        assert restart.call_count == restart_count


async def test_install_update_fails_if_out_of_date(
    coresys: CoreSys, install_addon_ssh: Addon
):
    """Test install or update of addon fails when supervisor or plugin is out of date."""
    coresys.hardware.disk.get_disk_free_space = lambda x: 5000

    with patch.object(
        type(coresys.supervisor), "need_update", new=PropertyMock(return_value=True)
    ):
        with pytest.raises(AddonsJobError):
            await coresys.addons.install(TEST_ADDON_SLUG)
        with pytest.raises(AddonsJobError):
            await coresys.addons.update(TEST_ADDON_SLUG)

    with (
        patch.object(
            type(coresys.plugins.audio),
            "need_update",
            new=PropertyMock(return_value=True),
        ),
        patch.object(
            type(coresys.plugins.audio), "update", side_effect=AudioUpdateError
        ),
    ):
        with pytest.raises(AddonsJobError):
            await coresys.addons.install(TEST_ADDON_SLUG)
        with pytest.raises(AddonsJobError):
            await coresys.addons.update(TEST_ADDON_SLUG)


async def test_listeners_removed_on_uninstall(
    coresys: CoreSys, install_addon_ssh: Addon
) -> None:
    """Test addon listeners are removed on uninstall."""
    with patch.object(DockerAddon, "attach"):
        await install_addon_ssh.load()

    assert install_addon_ssh.loaded is True
    # pylint: disable=protected-access
    listeners = install_addon_ssh._listeners
    for listener in listeners:
        assert (
            listener in coresys.bus._listeners[BusEvent.DOCKER_CONTAINER_STATE_CHANGE]
        )

    with patch.object(Addon, "persist", new=PropertyMock(return_value=MagicMock())):
        await coresys.addons.uninstall(TEST_ADDON_SLUG)

    for listener in listeners:
        assert (
            listener
            not in coresys.bus._listeners[BusEvent.DOCKER_CONTAINER_STATE_CHANGE]
        )


async def test_start(
    coresys: CoreSys,
    install_addon_ssh: Addon,
    container,
    tmp_supervisor_data,
    path_extern,
) -> None:
    """Test starting an addon without healthcheck."""
    install_addon_ssh.path_data.mkdir()
    await install_addon_ssh.load()
    await asyncio.sleep(0)
    assert install_addon_ssh.state == AddonState.STOPPED

    start_task = await install_addon_ssh.start()
    assert start_task

    _fire_test_event(coresys, f"addon_{TEST_ADDON_SLUG}", ContainerState.RUNNING)
    await start_task
    assert install_addon_ssh.state == AddonState.STARTED


@pytest.mark.parametrize("state", [ContainerState.HEALTHY, ContainerState.UNHEALTHY])
async def test_start_wait_healthcheck(
    coresys: CoreSys,
    install_addon_ssh: Addon,
    container: MagicMock,
    state: ContainerState,
    tmp_supervisor_data,
    path_extern,
) -> None:
    """Test starting an addon with a healthcheck waits for health status."""
    install_addon_ssh.path_data.mkdir()
    container.attrs["Config"] = {"Healthcheck": "exists"}
    await install_addon_ssh.load()
    await asyncio.sleep(0)
    assert install_addon_ssh.state == AddonState.STOPPED

    start_task = await install_addon_ssh.start()
    assert start_task

    _fire_test_event(coresys, f"addon_{TEST_ADDON_SLUG}", ContainerState.RUNNING)
    await asyncio.sleep(0.01)

    assert not start_task.done()
    assert install_addon_ssh.state == AddonState.STARTUP

    _fire_test_event(coresys, f"addon_{TEST_ADDON_SLUG}", state)
    await asyncio.sleep(0.01)

    assert start_task.done()
    assert install_addon_ssh.state == AddonState.STARTED


async def test_start_timeout(
    coresys: CoreSys,
    install_addon_ssh: Addon,
    caplog: pytest.LogCaptureFixture,
    container,
    tmp_supervisor_data,
    path_extern,
) -> None:
    """Test starting an addon times out while waiting."""
    install_addon_ssh.path_data.mkdir()
    await install_addon_ssh.load()
    await asyncio.sleep(0)
    assert install_addon_ssh.state == AddonState.STOPPED

    start_task = await install_addon_ssh.start()
    assert start_task

    caplog.clear()
    with patch(
        "supervisor.addons.addon.asyncio.wait_for", side_effect=asyncio.TimeoutError
    ):
        await start_task

    assert "Timeout while waiting for addon Terminal & SSH to start" in caplog.text


async def test_restart(
    coresys: CoreSys,
    install_addon_ssh: Addon,
    container,
    tmp_supervisor_data,
    path_extern,
) -> None:
    """Test restarting an addon."""
    install_addon_ssh.path_data.mkdir()
    await install_addon_ssh.load()
    await asyncio.sleep(0)
    assert install_addon_ssh.state == AddonState.STOPPED

    start_task = await install_addon_ssh.restart()
    assert start_task

    _fire_test_event(coresys, f"addon_{TEST_ADDON_SLUG}", ContainerState.RUNNING)
    await start_task
    assert install_addon_ssh.state == AddonState.STARTED


@pytest.mark.parametrize("status", ["running", "stopped"])
async def test_backup(
    coresys: CoreSys,
    install_addon_ssh: Addon,
    container: MagicMock,
    status: str,
    tmp_supervisor_data,
    path_extern,
) -> None:
    """Test backing up an addon."""
    container.status = status
    install_addon_ssh.path_data.mkdir()
    await install_addon_ssh.load()

    tarfile = SecureTarFile(coresys.config.path_tmp / "test.tar.gz", "w")
    assert await install_addon_ssh.backup(tarfile) is None


@pytest.mark.parametrize("status", ["running", "stopped"])
async def test_backup_no_config(
    coresys: CoreSys,
    install_addon_ssh: Addon,
    container: MagicMock,
    status: str,
    tmp_supervisor_data,
    path_extern,
) -> None:
    """Test backing up an addon with deleted config directory."""
    container.status = status

    install_addon_ssh.data["map"].append({"type": "addon_config", "read_only": False})
    assert not install_addon_ssh.path_config.exists()
    install_addon_ssh.path_data.mkdir()
    await install_addon_ssh.load()

    tarfile = SecureTarFile(coresys.config.path_tmp / "test.tar.gz", "w")
    assert await install_addon_ssh.backup(tarfile) is None


async def test_backup_with_pre_post_command(
    coresys: CoreSys,
    install_addon_ssh: Addon,
    container: MagicMock,
    tmp_supervisor_data,
    path_extern,
) -> None:
    """Test backing up an addon with pre and post command."""
    container.status = "running"
    container.exec_run.return_value = (0, None)
    install_addon_ssh.path_data.mkdir()
    await install_addon_ssh.load()

    tarfile = SecureTarFile(coresys.config.path_tmp / "test.tar.gz", "w")
    with (
        patch.object(Addon, "backup_pre", new=PropertyMock(return_value="backup_pre")),
        patch.object(
            Addon, "backup_post", new=PropertyMock(return_value="backup_post")
        ),
    ):
        assert await install_addon_ssh.backup(tarfile) is None

    assert container.exec_run.call_count == 2
    assert container.exec_run.call_args_list[0].args[0] == "backup_pre"
    assert container.exec_run.call_args_list[1].args[0] == "backup_post"


@pytest.mark.parametrize(
    "get_error,exception_on_exec",
    [
        (NotFound("missing"), False),
        (DockerException(), False),
        (None, True),
        (None, False),
    ],
)
async def test_backup_with_pre_command_error(
    coresys: CoreSys,
    install_addon_ssh: Addon,
    container: MagicMock,
    get_error: DockerException | None,
    exception_on_exec: bool,
    tmp_supervisor_data,
    path_extern,
) -> None:
    """Test backing up an addon with error running pre command."""
    if get_error:
        coresys.docker.containers.get.side_effect = get_error

    if exception_on_exec:
        container.exec_run.side_effect = DockerException()
    else:
        container.exec_run.return_value = (1, None)

    install_addon_ssh.path_data.mkdir()
    await install_addon_ssh.load()

    tarfile = SecureTarFile(coresys.config.path_tmp / "test.tar.gz", "w")
    with (
        patch.object(DockerAddon, "is_running", return_value=True),
        patch.object(Addon, "backup_pre", new=PropertyMock(return_value="backup_pre")),
        pytest.raises(AddonsError),
    ):
        assert await install_addon_ssh.backup(tarfile) is None

    assert not tarfile.path.exists()


@pytest.mark.parametrize("status", ["running", "stopped"])
async def test_backup_cold_mode(
    coresys: CoreSys,
    install_addon_ssh: Addon,
    container: MagicMock,
    status: str,
    tmp_supervisor_data,
    path_extern,
) -> None:
    """Test backing up an addon in cold mode."""
    container.status = status
    install_addon_ssh.path_data.mkdir()
    await install_addon_ssh.load()

    tarfile = SecureTarFile(coresys.config.path_tmp / "test.tar.gz", "w")
    with (
        patch.object(
            AddonModel,
            "backup_mode",
            new=PropertyMock(return_value=AddonBackupMode.COLD),
        ),
        patch.object(
            DockerAddon, "is_running", side_effect=[status == "running", False, False]
        ),
    ):
        start_task = await install_addon_ssh.backup(tarfile)

    assert bool(start_task) is (status == "running")


async def test_backup_cold_mode_with_watchdog(
    coresys: CoreSys,
    install_addon_ssh: Addon,
    container: MagicMock,
    tmp_supervisor_data,
    path_extern,
):
    """Test backing up an addon in cold mode with watchdog active."""
    container.status = "running"
    install_addon_ssh.watchdog = True
    install_addon_ssh.path_data.mkdir()
    await install_addon_ssh.load()

    # Simulate stop firing the docker event for stopped container like it normally would
    async def mock_stop(*args, **kwargs):
        container.status = "stopped"
        _fire_test_event(coresys, f"addon_{TEST_ADDON_SLUG}", ContainerState.STOPPED)

    # Patching out the normal end of backup process leaves the container in a stopped state
    # Watchdog should still not try to restart it though, it should remain this way
    tarfile = SecureTarFile(coresys.config.path_tmp / "test.tar.gz", "w")
    with (
        patch.object(Addon, "start") as start,
        patch.object(Addon, "restart") as restart,
        patch.object(Addon, "end_backup"),
        patch.object(DockerAddon, "stop", new=mock_stop),
        patch.object(
            AddonModel,
            "backup_mode",
            new=PropertyMock(return_value=AddonBackupMode.COLD),
        ),
    ):
        await install_addon_ssh.backup(tarfile)
        await asyncio.sleep(0)
        start.assert_not_called()
        restart.assert_not_called()


@pytest.mark.parametrize("status", ["running", "stopped"])
async def test_restore(
    coresys: CoreSys,
    install_addon_ssh: Addon,
    container: MagicMock,
    status: str,
    tmp_supervisor_data,
    path_extern,
    mock_aarch64_arch_supported: None,
) -> None:
    """Test restoring an addon."""
    coresys.hardware.disk.get_disk_free_space = lambda x: 5000
    install_addon_ssh.path_data.mkdir()
    await install_addon_ssh.load()

    tarfile = SecureTarFile(get_fixture_path(f"backup_local_ssh_{status}.tar.gz"), "r")
    with patch.object(DockerAddon, "is_running", return_value=False):
        start_task = await coresys.addons.restore(TEST_ADDON_SLUG, tarfile)

    assert bool(start_task) is (status == "running")


async def test_restore_while_running(
    coresys: CoreSys,
    install_addon_ssh: Addon,
    container: MagicMock,
    tmp_supervisor_data,
    path_extern,
    mock_aarch64_arch_supported: None,
):
    """Test restore of a running addon."""
    container.status = "running"
    coresys.hardware.disk.get_disk_free_space = lambda x: 5000
    install_addon_ssh.path_data.mkdir()
    await install_addon_ssh.load()

    tarfile = SecureTarFile(get_fixture_path("backup_local_ssh_stopped.tar.gz"), "r")
    with (
        patch.object(DockerAddon, "is_running", return_value=True),
        patch.object(Ingress, "update_hass_panel"),
    ):
        start_task = await coresys.addons.restore(TEST_ADDON_SLUG, tarfile)

    assert bool(start_task) is False
    container.stop.assert_called_once()


async def test_restore_while_running_with_watchdog(
    coresys: CoreSys,
    install_addon_ssh: Addon,
    container: MagicMock,
    tmp_supervisor_data,
    path_extern,
    mock_aarch64_arch_supported: None,
):
    """Test restore of a running addon with watchdog interference."""
    container.status = "running"
    coresys.hardware.disk.get_disk_free_space = lambda x: 5000
    install_addon_ssh.path_data.mkdir()
    install_addon_ssh.watchdog = True
    await install_addon_ssh.load()

    # Simulate stop firing the docker event for stopped container like it normally would
    async def mock_stop(*args, **kwargs):
        container.status = "stopped"
        _fire_test_event(coresys, f"addon_{TEST_ADDON_SLUG}", ContainerState.STOPPED)

    # We restore a stopped backup so restore will not restart it
    # Watchdog will see it stop and should not attempt reanimation either
    tarfile = SecureTarFile(get_fixture_path("backup_local_ssh_stopped.tar.gz"), "r")
    with (
        patch.object(Addon, "start") as start,
        patch.object(Addon, "restart") as restart,
        patch.object(DockerAddon, "stop", new=mock_stop),
        patch.object(Ingress, "update_hass_panel"),
    ):
        await coresys.addons.restore(TEST_ADDON_SLUG, tarfile)
        await asyncio.sleep(0)
        start.assert_not_called()
        restart.assert_not_called()


async def test_start_when_running(
    coresys: CoreSys,
    install_addon_ssh: Addon,
    container: MagicMock,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test starting an addon without healthcheck."""
    container.status = "running"
    await install_addon_ssh.load()
    await asyncio.sleep(0)
    assert install_addon_ssh.state == AddonState.STARTED

    caplog.clear()
    start_task = await install_addon_ssh.start()
    assert start_task
    await start_task

    assert "local_ssh is already running" in caplog.text


async def test_local_example_install(
    coresys: CoreSys,
    container: MagicMock,
    tmp_supervisor_data: Path,
    repository,
    mock_aarch64_arch_supported: None,
):
    """Test install of an addon."""
    coresys.hardware.disk.get_disk_free_space = lambda x: 5000
    assert not (
        data_dir := tmp_supervisor_data / "addons" / "data" / "local_example"
    ).exists()

    with patch.object(DockerAddon, "install") as install:
        await coresys.addons.install("local_example")
        install.assert_called_once()

    assert data_dir.is_dir()


async def test_local_example_start(
    coresys: CoreSys,
    container: MagicMock,
    tmp_supervisor_data: Path,
    install_addon_example: Addon,
    path_extern,
):
    """Test start of an addon."""
    install_addon_example.path_data.mkdir()
    await install_addon_example.load()
    await asyncio.sleep(0)
    assert install_addon_example.state == AddonState.STOPPED

    assert not (
        addon_config_dir := tmp_supervisor_data / "addon_configs" / "local_example"
    ).exists()

    await install_addon_example.start()

    assert addon_config_dir.is_dir()


async def test_local_example_ingress_port_set(
    coresys: CoreSys,
    container: MagicMock,
    tmp_supervisor_data: Path,
    install_addon_example: Addon,
):
    """Test start of an addon."""
    install_addon_example.path_data.mkdir()
    await install_addon_example.load()

    assert install_addon_example.ingress_port != 0


async def test_addon_pulse_error(
    coresys: CoreSys,
    install_addon_example: Addon,
    caplog: pytest.LogCaptureFixture,
    tmp_supervisor_data,
):
    """Test error writing pulse config for addon."""
    with patch(
        "supervisor.addons.addon.Path.write_text", side_effect=(err := OSError())
    ):
        err.errno = errno.EBUSY
        await install_addon_example.write_pulse()

        assert "can't write pulse/client.config" in caplog.text
        assert coresys.core.healthy is True

        caplog.clear()
        err.errno = errno.EBADMSG
        await install_addon_example.write_pulse()

        assert "can't write pulse/client.config" in caplog.text
        assert coresys.core.healthy is False


def test_auto_update_available(coresys: CoreSys, install_addon_example: Addon):
    """Test auto update availability based on versions."""
    assert install_addon_example.auto_update is False
    assert install_addon_example.need_update is False
    assert install_addon_example.auto_update_available is False

    with patch.object(
        Addon, "version", new=PropertyMock(return_value=AwesomeVersion("1.0"))
    ):
        assert install_addon_example.need_update is True
        assert install_addon_example.auto_update_available is False

        install_addon_example.auto_update = True
        assert install_addon_example.auto_update_available is True

    with patch.object(
        Addon, "version", new=PropertyMock(return_value=AwesomeVersion("0.9"))
    ):
        assert install_addon_example.auto_update_available is False

    with patch.object(
        Addon, "version", new=PropertyMock(return_value=AwesomeVersion("test"))
    ):
        assert install_addon_example.auto_update_available is False


async def test_paths_cache(coresys: CoreSys, install_addon_ssh: Addon):
    """Test cache for key paths that may or may not exist."""
    assert not install_addon_ssh.with_logo
    assert not install_addon_ssh.with_icon
    assert not install_addon_ssh.with_changelog
    assert not install_addon_ssh.with_documentation

    with (
        patch("supervisor.addons.addon.Path.exists", return_value=True),
        patch("supervisor.store.repository.Repository.update", return_value=True),
    ):
        await coresys.store.reload(coresys.store.get("local"))

        assert install_addon_ssh.with_logo
        assert install_addon_ssh.with_icon
        assert install_addon_ssh.with_changelog
        assert install_addon_ssh.with_documentation


async def test_addon_loads_wrong_image(
    coresys: CoreSys,
    install_addon_ssh: Addon,
    container: MagicMock,
    mock_amd64_arch_supported,
):
    """Test addon is loaded with incorrect image for architecture."""
    coresys.addons.data.save_data.reset_mock()
    install_addon_ssh.persist["image"] = "local/aarch64-addon-ssh"
    assert install_addon_ssh.image == "local/aarch64-addon-ssh"

    with patch("pathlib.Path.is_file", return_value=True):
        await install_addon_ssh.load()

    container.remove.assert_called_once_with(force=True)
    assert coresys.docker.images.remove.call_args_list[0].kwargs == {
        "image": "local/aarch64-addon-ssh:latest",
        "force": True,
    }
    assert coresys.docker.images.remove.call_args_list[1].kwargs == {
        "image": "local/aarch64-addon-ssh:9.2.1",
        "force": True,
    }
    coresys.docker.images.build.assert_called_once()
    assert (
        coresys.docker.images.build.call_args.kwargs["tag"]
        == "local/amd64-addon-ssh:9.2.1"
    )
    assert coresys.docker.images.build.call_args.kwargs["platform"] == "linux/amd64"
    assert install_addon_ssh.image == "local/amd64-addon-ssh"
    coresys.addons.data.save_data.assert_called_once()


async def test_addon_loads_missing_image(
    coresys: CoreSys,
    install_addon_ssh: Addon,
    container: MagicMock,
    mock_amd64_arch_supported,
):
    """Test addon corrects a missing image on load."""
    coresys.docker.images.get.side_effect = ImageNotFound("missing")

    with patch("pathlib.Path.is_file", return_value=True):
        await install_addon_ssh.load()

    coresys.docker.images.build.assert_called_once()
    assert (
        coresys.docker.images.build.call_args.kwargs["tag"]
        == "local/amd64-addon-ssh:9.2.1"
    )
    assert coresys.docker.images.build.call_args.kwargs["platform"] == "linux/amd64"
    assert install_addon_ssh.image == "local/amd64-addon-ssh"


async def test_addon_load_succeeds_with_docker_errors(
    coresys: CoreSys,
    install_addon_ssh: Addon,
    container: MagicMock,
    caplog: pytest.LogCaptureFixture,
    mock_amd64_arch_supported,
):
    """Docker errors while building/pulling an image during load should not raise and fail setup."""
    # Build env invalid failure
    coresys.docker.images.get.side_effect = ImageNotFound("missing")
    caplog.clear()
    await install_addon_ssh.load()
    assert "Invalid build environment" in caplog.text

    # Image build failure
    coresys.docker.images.build.side_effect = DockerException()
    caplog.clear()
    with patch("pathlib.Path.is_file", return_value=True):
        await install_addon_ssh.load()
    assert "Can't build local/amd64-addon-ssh:9.2.1" in caplog.text

    # Image pull failure
    install_addon_ssh.data["image"] = "test/amd64-addon-ssh"
    coresys.docker.images.build.reset_mock(side_effect=True)
    coresys.docker.images.pull.side_effect = DockerException()
    caplog.clear()
    await install_addon_ssh.load()
    assert "Unknown error with test/amd64-addon-ssh:9.2.1" in caplog.text


async def test_addon_manual_only_boot(coresys: CoreSys, install_addon_example: Addon):
    """Test an addon with manual only boot mode."""
    assert install_addon_example.boot_config == "manual_only"
    assert install_addon_example.boot == "manual"

    # Users cannot change boot mode of an addon with manual forced so changing boot isn't realistic
    # However boot mode can change on update and user may have set auto before, ensure it is ignored
    install_addon_example.boot = "auto"
    assert install_addon_example.boot == "manual"


async def test_addon_start_dismisses_boot_fail(
    coresys: CoreSys, install_addon_ssh: Addon
):
    """Test a successful start dismisses the boot fail issue."""
    install_addon_ssh.state = AddonState.ERROR
    coresys.resolution.add_issue(
        BOOT_FAIL_ISSUE, [suggestion.type for suggestion in BOOT_FAIL_SUGGESTIONS]
    )

    install_addon_ssh.state = AddonState.STARTED
    assert coresys.resolution.issues == []
    assert coresys.resolution.suggestions == []


async def test_addon_disable_boot_dismisses_boot_fail(
    coresys: CoreSys, install_addon_ssh: Addon
):
    """Test a disabling boot dismisses the boot fail issue."""
    install_addon_ssh.boot = AddonBoot.AUTO
    install_addon_ssh.state = AddonState.ERROR
    coresys.resolution.add_issue(
        BOOT_FAIL_ISSUE, [suggestion.type for suggestion in BOOT_FAIL_SUGGESTIONS]
    )

    install_addon_ssh.boot = AddonBoot.MANUAL
    assert coresys.resolution.issues == []
    assert coresys.resolution.suggestions == []
