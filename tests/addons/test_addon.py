"""Test Home Assistant Add-ons."""

import asyncio
from datetime import timedelta
from unittest.mock import MagicMock, PropertyMock, patch

from docker.errors import DockerException
import pytest

from supervisor.addons.addon import Addon
from supervisor.const import AddonState, BusEvent
from supervisor.coresys import CoreSys
from supervisor.docker.addon import DockerAddon
from supervisor.docker.const import ContainerState
from supervisor.docker.monitor import DockerContainerStateEvent
from supervisor.exceptions import AddonsJobError, AudioUpdateError
from supervisor.store.repository import Repository
from supervisor.utils.dt import utcnow

from ..const import TEST_ADDON_SLUG


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
    assert coresys.addons.get(TEST_ADDON_SLUG).state == AddonState.STARTED


@pytest.mark.parametrize(
    "boot_timedelta,restart_count", [(timedelta(), 0), (timedelta(days=1), 1)]
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
