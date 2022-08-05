"""Test Home Assistant Add-ons."""

import asyncio
from unittest.mock import MagicMock, PropertyMock, patch

from docker.errors import DockerException

from supervisor.addons.addon import Addon
from supervisor.const import AddonState, BusEvent
from supervisor.coresys import CoreSys
from supervisor.docker.const import ContainerState
from supervisor.docker.monitor import DockerContainerStateEvent

from ..const import TEST_ADDON_SLUG


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
    with patch.object(type(install_addon_ssh.instance), "attach"):
        await install_addon_ssh.load()

    assert install_addon_ssh.state == AddonState.UNKNOWN

    with patch.object(type(install_addon_ssh), "watchdog_container"):
        coresys.bus.fire_event(
            BusEvent.DOCKER_CONTAINER_STATE_CHANGE,
            DockerContainerStateEvent(
                name=f"addon_{TEST_ADDON_SLUG}",
                state=ContainerState.RUNNING,
                id="abc123",
                time=1,
            ),
        )
        await asyncio.sleep(0)
        assert install_addon_ssh.state == AddonState.STARTED

        coresys.bus.fire_event(
            BusEvent.DOCKER_CONTAINER_STATE_CHANGE,
            DockerContainerStateEvent(
                name=f"addon_{TEST_ADDON_SLUG}",
                state=ContainerState.STOPPED,
                id="abc123",
                time=1,
            ),
        )
        await asyncio.sleep(0)
        assert install_addon_ssh.state == AddonState.STOPPED

        coresys.bus.fire_event(
            BusEvent.DOCKER_CONTAINER_STATE_CHANGE,
            DockerContainerStateEvent(
                name=f"addon_{TEST_ADDON_SLUG}",
                state=ContainerState.HEALTHY,
                id="abc123",
                time=1,
            ),
        )
        await asyncio.sleep(0)
        assert install_addon_ssh.state == AddonState.STARTED

        coresys.bus.fire_event(
            BusEvent.DOCKER_CONTAINER_STATE_CHANGE,
            DockerContainerStateEvent(
                name=f"addon_{TEST_ADDON_SLUG}",
                state=ContainerState.FAILED,
                id="abc123",
                time=1,
            ),
        )
        await asyncio.sleep(0)
        assert install_addon_ssh.state == AddonState.ERROR

        # Test other addons are ignored
        coresys.bus.fire_event(
            BusEvent.DOCKER_CONTAINER_STATE_CHANGE,
            DockerContainerStateEvent(
                name="addon_local_non_installed",
                state=ContainerState.RUNNING,
                id="abc123",
                time=1,
            ),
        )
        await asyncio.sleep(0)
        assert install_addon_ssh.state == AddonState.ERROR


async def mock_current_state(state: ContainerState) -> ContainerState:
    """Mock for current state method."""
    return state


async def mock_stop() -> None:
    """Mock for stop method."""


async def test_addon_watchdog(coresys: CoreSys, install_addon_ssh: Addon) -> None:
    """Test addon watchdog works correctly."""
    with patch.object(type(install_addon_ssh.instance), "attach"):
        await install_addon_ssh.load()

    install_addon_ssh.watchdog = True

    with patch.object(Addon, "restart") as restart, patch.object(
        Addon, "start"
    ) as start, patch.object(
        type(install_addon_ssh.instance), "current_state"
    ) as current_state:
        current_state.return_value = mock_current_state(ContainerState.UNHEALTHY)
        coresys.bus.fire_event(
            BusEvent.DOCKER_CONTAINER_STATE_CHANGE,
            DockerContainerStateEvent(
                name=f"addon_{TEST_ADDON_SLUG}",
                state=ContainerState.UNHEALTHY,
                id="abc123",
                time=1,
            ),
        )
        await asyncio.sleep(0)
        restart.assert_called_once()
        start.assert_not_called()

        restart.reset_mock()
        current_state.return_value = mock_current_state(ContainerState.FAILED)

        with patch.object(
            type(install_addon_ssh.instance), "stop", return_value=mock_stop()
        ) as stop:
            coresys.bus.fire_event(
                BusEvent.DOCKER_CONTAINER_STATE_CHANGE,
                DockerContainerStateEvent(
                    name=f"addon_{TEST_ADDON_SLUG}",
                    state=ContainerState.FAILED,
                    id="abc123",
                    time=1,
                ),
            )
            await asyncio.sleep(0)
            stop.assert_called_once_with(remove_container=True)
            restart.assert_not_called()
            start.assert_called_once()

        start.reset_mock()
        # Do not process event if container state has changed since fired
        current_state.return_value = mock_current_state(ContainerState.HEALTHY)
        coresys.bus.fire_event(
            BusEvent.DOCKER_CONTAINER_STATE_CHANGE,
            DockerContainerStateEvent(
                name=f"addon_{TEST_ADDON_SLUG}",
                state=ContainerState.FAILED,
                id="abc123",
                time=1,
            ),
        )
        await asyncio.sleep(0)
        restart.assert_not_called()
        start.assert_not_called()

        # Do not restart when addon stopped normally
        coresys.bus.fire_event(
            BusEvent.DOCKER_CONTAINER_STATE_CHANGE,
            DockerContainerStateEvent(
                name=f"addon_{TEST_ADDON_SLUG}",
                state=ContainerState.STOPPED,
                id="abc123",
                time=1,
            ),
        )
        await asyncio.sleep(0)
        restart.assert_not_called()
        start.assert_not_called()

        # Other addons ignored
        coresys.bus.fire_event(
            BusEvent.DOCKER_CONTAINER_STATE_CHANGE,
            DockerContainerStateEvent(
                name="addon_local_non_installed",
                state=ContainerState.UNHEALTHY,
                id="abc123",
                time=1,
            ),
        )
        await asyncio.sleep(0)
        restart.assert_not_called()
        start.assert_not_called()


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

    coresys.bus.fire_event(
        BusEvent.DOCKER_CONTAINER_STATE_CHANGE,
        DockerContainerStateEvent(
            name=f"addon_{TEST_ADDON_SLUG}",
            state=ContainerState.RUNNING,
            id="abc123",
            time=1,
        ),
    )
    await asyncio.sleep(0)
    assert coresys.addons.get(TEST_ADDON_SLUG).state == AddonState.STARTED
