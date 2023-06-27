"""Test Home Assistant Add-ons."""

import asyncio
from datetime import timedelta
from unittest.mock import MagicMock, PropertyMock, patch

from docker.errors import DockerException
import pytest
from securetar import SecureTarFile

from supervisor.addons.addon import Addon
from supervisor.addons.const import AddonBackupMode
from supervisor.addons.model import AddonModel
from supervisor.arch import CpuArch
from supervisor.const import AddonState, BusEvent
from supervisor.coresys import CoreSys
from supervisor.docker.addon import DockerAddon
from supervisor.docker.const import ContainerState
from supervisor.docker.monitor import DockerContainerStateEvent
from supervisor.exceptions import AddonsJobError, AudioUpdateError
from supervisor.store.repository import Repository
from supervisor.utils.dt import utcnow

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


async def mock_current_state(state: ContainerState) -> ContainerState:
    """Mock for current state method."""
    return state


async def mock_stop() -> None:
    """Mock for stop method."""


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

    with patch.object(Addon, "restart") as restart, patch.object(
        Addon, "start"
    ) as start, patch.object(DockerAddon, "current_state") as current_state:
        # Restart if it becomes unhealthy
        current_state.return_value = mock_current_state(ContainerState.UNHEALTHY)
        _fire_test_event(coresys, f"addon_{TEST_ADDON_SLUG}", ContainerState.UNHEALTHY)
        await asyncio.sleep(0)
        restart.assert_called_once()
        start.assert_not_called()

        restart.reset_mock()

        # Rebuild if it failed
        current_state.return_value = mock_current_state(ContainerState.FAILED)
        with patch.object(DockerAddon, "stop", return_value=mock_stop()) as stop:
            _fire_test_event(coresys, f"addon_{TEST_ADDON_SLUG}", ContainerState.FAILED)
            await asyncio.sleep(0)
            stop.assert_called_once_with(remove_container=True)
            restart.assert_not_called()
            start.assert_called_once()

        start.reset_mock()

        # Do not process event if container state has changed since fired
        current_state.return_value = mock_current_state(ContainerState.HEALTHY)
        _fire_test_event(coresys, f"addon_{TEST_ADDON_SLUG}", ContainerState.FAILED)
        await asyncio.sleep(0)
        restart.assert_not_called()
        start.assert_not_called()

        # Other addons ignored
        current_state.return_value = mock_current_state(ContainerState.UNHEALTHY)
        _fire_test_event(coresys, "addon_local_non_installed", ContainerState.UNHEALTHY)
        await asyncio.sleep(0)
        restart.assert_not_called()
        start.assert_not_called()


async def test_watchdog_on_stop(coresys: CoreSys, install_addon_ssh: Addon) -> None:
    """Test addon watchdog restarts addon on stop if not manual."""
    with patch.object(DockerAddon, "attach"):
        await install_addon_ssh.load()

    install_addon_ssh.watchdog = True

    with patch.object(Addon, "restart") as restart, patch.object(
        DockerAddon,
        "current_state",
        return_value=mock_current_state(ContainerState.STOPPED),
    ), patch.object(DockerAddon, "stop", return_value=mock_stop()):
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


async def test_listener_attached_on_install(coresys: CoreSys, repository):
    """Test events listener attached on addon install."""
    container_collection = MagicMock()
    container_collection.get.side_effect = DockerException()
    with patch(
        "supervisor.arch.CpuArch.supported", new=PropertyMock(return_value=["amd64"])
    ), patch(
        "supervisor.docker.manager.DockerAPI.containers",
        new=PropertyMock(return_value=container_collection),
    ), patch(
        "pathlib.Path.is_dir", return_value=True
    ), patch(
        "supervisor.addons.addon.Addon.need_build", new=PropertyMock(return_value=False)
    ), patch(
        "supervisor.addons.model.AddonModel.with_ingress",
        new=PropertyMock(return_value=False),
    ):
        await coresys.addons.install.__wrapped__(coresys.addons, TEST_ADDON_SLUG)

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
    coresys.addons.data.install(store)

    with patch.object(Addon, "restart") as restart, patch.object(
        type(coresys.hardware.helper),
        "last_boot",
        new=PropertyMock(return_value=utcnow()),
    ), patch.object(DockerAddon, "attach"), patch.object(
        DockerAddon,
        "current_state",
        return_value=mock_current_state(ContainerState.STOPPED),
    ):
        coresys.config.last_boot = coresys.hardware.helper.last_boot + boot_timedelta
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
            await install_addon_ssh.update()

    with patch.object(
        type(coresys.plugins.audio), "need_update", new=PropertyMock(return_value=True)
    ), patch.object(
        type(coresys.plugins.audio), "update", side_effect=AudioUpdateError
    ):
        with pytest.raises(AddonsJobError):
            await coresys.addons.install(TEST_ADDON_SLUG)
        with pytest.raises(AddonsJobError):
            await install_addon_ssh.update()


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
    assert install_addon_ssh.state == AddonState.STOPPED

    start_task = asyncio.create_task(await install_addon_ssh.start())
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
    with patch.object(
        AddonModel, "backup_mode", new=PropertyMock(return_value=AddonBackupMode.COLD)
    ), patch.object(
        DockerAddon, "_is_running", side_effect=[status == "running", False, False]
    ):
        start_task = await install_addon_ssh.backup(tarfile)

    assert bool(start_task) is (status == "running")


@pytest.mark.parametrize("status", ["running", "stopped"])
async def test_restore(
    coresys: CoreSys,
    install_addon_ssh: Addon,
    container: MagicMock,
    status: str,
    tmp_supervisor_data,
    path_extern,
) -> None:
    """Test restoring an addon."""
    install_addon_ssh.path_data.mkdir()
    await install_addon_ssh.load()

    tarfile = SecureTarFile(get_fixture_path(f"backup_local_ssh_{status}.tar.gz"), "r")
    with patch.object(DockerAddon, "_is_running", return_value=False), patch.object(
        CpuArch, "supported", new=PropertyMock(return_value=["aarch64"])
    ):
        start_task = await coresys.addons.restore(TEST_ADDON_SLUG, tarfile)

    assert bool(start_task) is (status == "running")


async def test_start_when_running(
    coresys: CoreSys,
    install_addon_ssh: Addon,
    container: MagicMock,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test starting an addon without healthcheck."""
    container.status = "running"
    await install_addon_ssh.load()
    assert install_addon_ssh.state == AddonState.STARTED

    caplog.clear()
    start_task = await install_addon_ssh.start()
    assert start_task
    await start_task

    assert "local_ssh is already running" in caplog.text
