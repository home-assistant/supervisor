"""Test watchdog for plugins."""
import asyncio
from unittest.mock import patch

import pytest

from supervisor.const import BusEvent
from supervisor.coresys import CoreSys
from supervisor.docker.const import ContainerState
from supervisor.docker.monitor import DockerContainerStateEvent
from supervisor.exceptions import (
    AudioError,
    CliError,
    CoreDNSError,
    MulticastError,
    ObserverError,
    PluginError,
)
from supervisor.plugins.audio import PluginAudio
from supervisor.plugins.base import PluginBase
from supervisor.plugins.cli import PluginCli
from supervisor.plugins.dns import PluginDns
from supervisor.plugins.multicast import PluginMulticast
from supervisor.plugins.observer import PluginObserver


@pytest.fixture(name="plugin")
async def fixture_plugin(
    coresys: CoreSys, request: pytest.FixtureRequest
) -> PluginBase:
    """Get plugin from param."""
    if request.param == PluginAudio:
        yield coresys.plugins.audio
    elif request.param == PluginCli:
        yield coresys.plugins.cli
    elif request.param == PluginDns:
        with patch.object(PluginDns, "loop_detection"):
            yield coresys.plugins.dns
    elif request.param == PluginMulticast:
        yield coresys.plugins.multicast
    elif request.param == PluginObserver:
        yield coresys.plugins.observer


async def mock_current_state(state: ContainerState) -> ContainerState:
    """Mock for current state method."""
    return state


@pytest.mark.parametrize(
    "plugin",
    [PluginAudio, PluginCli, PluginDns, PluginMulticast, PluginObserver],
    indirect=True,
)
async def test_plugin_watchdog(coresys: CoreSys, plugin: PluginBase) -> None:
    """Test plugin watchdog works correctly."""
    plugin.start_watchdog()

    with patch.object(type(plugin), "rebuild") as rebuild, patch.object(
        type(plugin), "start"
    ) as start, patch.object(type(plugin.instance), "current_state") as current_state:
        current_state.return_value = mock_current_state(ContainerState.UNHEALTHY)
        coresys.bus.fire_event(
            BusEvent.DOCKER_CONTAINER_STATE_CHANGE,
            DockerContainerStateEvent(
                name=plugin.instance.name,
                state=ContainerState.UNHEALTHY,
                id="abc123",
                time=1,
            ),
        )
        await asyncio.sleep(0)
        rebuild.assert_called_once()
        start.assert_not_called()

        rebuild.reset_mock()
        current_state.return_value = mock_current_state(ContainerState.FAILED)
        coresys.bus.fire_event(
            BusEvent.DOCKER_CONTAINER_STATE_CHANGE,
            DockerContainerStateEvent(
                name=plugin.instance.name,
                state=ContainerState.FAILED,
                id="abc123",
                time=1,
            ),
        )
        await asyncio.sleep(0)
        rebuild.assert_called_once()
        start.assert_not_called()

        rebuild.reset_mock()
        # Plugins are restarted anytime they stop, not just on failure
        current_state.return_value = mock_current_state(ContainerState.STOPPED)
        coresys.bus.fire_event(
            BusEvent.DOCKER_CONTAINER_STATE_CHANGE,
            DockerContainerStateEvent(
                name=plugin.instance.name,
                state=ContainerState.STOPPED,
                id="abc123",
                time=1,
            ),
        )
        await asyncio.sleep(0)
        rebuild.assert_not_called()
        start.assert_called_once()

        start.reset_mock()
        # Do not process event if container state has changed since fired
        current_state.return_value = mock_current_state(ContainerState.HEALTHY)
        coresys.bus.fire_event(
            BusEvent.DOCKER_CONTAINER_STATE_CHANGE,
            DockerContainerStateEvent(
                name=plugin.instance.name,
                state=ContainerState.FAILED,
                id="abc123",
                time=1,
            ),
        )
        await asyncio.sleep(0)
        rebuild.assert_not_called()
        start.assert_not_called()

        # Other containers ignored
        coresys.bus.fire_event(
            BusEvent.DOCKER_CONTAINER_STATE_CHANGE,
            DockerContainerStateEvent(
                name="addon_local_other",
                state=ContainerState.UNHEALTHY,
                id="abc123",
                time=1,
            ),
        )
        await asyncio.sleep(0)
        rebuild.assert_not_called()
        start.assert_not_called()


@pytest.mark.parametrize(
    "plugin,error",
    [
        (PluginAudio, AudioError),
        (PluginCli, CliError),
        (PluginDns, CoreDNSError),
        (PluginMulticast, MulticastError),
        (PluginObserver, ObserverError),
    ],
    indirect=["plugin"],
)
async def test_plugin_watchdog_rebuild_on_failure(
    coresys: CoreSys, plugin: PluginBase, error: PluginError
) -> None:
    """Test plugin watchdog rebuilds if start fails."""
    plugin.start_watchdog()

    with patch("supervisor.plugins.base.WATCHDOG_RETRY_SECONDS", 0), patch.object(
        type(plugin), "rebuild"
    ) as rebuild, patch.object(
        type(plugin), "start", side_effect=error
    ) as start, patch.object(
        type(plugin.instance),
        "current_state",
        side_effect=[
            mock_current_state(ContainerState.STOPPED),
            mock_current_state(ContainerState.STOPPED),
        ],
    ):
        coresys.bus.fire_event(
            BusEvent.DOCKER_CONTAINER_STATE_CHANGE,
            DockerContainerStateEvent(
                name=plugin.instance.name,
                state=ContainerState.STOPPED,
                id="abc123",
                time=1,
            ),
        )
        await asyncio.sleep(0.1)
        start.assert_called_once()
        rebuild.assert_called_once()
