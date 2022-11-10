"""Test base plugin functionality."""
import asyncio
from unittest.mock import Mock, PropertyMock, patch

from awesomeversion import AwesomeVersion
import pytest

from supervisor.const import BusEvent, CpuArch
from supervisor.coresys import CoreSys
from supervisor.docker.const import ContainerState
from supervisor.docker.interface import DockerInterface
from supervisor.docker.monitor import DockerContainerStateEvent
from supervisor.exceptions import (
    AudioError,
    AudioJobError,
    CliError,
    CliJobError,
    CodeNotaryUntrusted,
    CoreDNSError,
    CoreDNSJobError,
    DockerError,
    MulticastError,
    MulticastJobError,
    ObserverError,
    ObserverJobError,
    PluginError,
    PluginJobError,
)
from supervisor.plugins.audio import PluginAudio
from supervisor.plugins.base import PluginBase
from supervisor.plugins.cli import PluginCli
from supervisor.plugins.dns import PluginDns
from supervisor.plugins.multicast import PluginMulticast
from supervisor.plugins.observer import PluginObserver
from supervisor.utils import check_exception_chain


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


async def mock_is_running(running: bool) -> bool:
    """Mock for is running method."""
    return running


async def mock_get_latest_version(version: AwesomeVersion) -> AwesomeVersion:
    """Mock for get latest version method."""
    return version


@pytest.mark.parametrize(
    "plugin",
    [PluginAudio, PluginCli, PluginDns, PluginMulticast, PluginObserver],
    indirect=True,
)
async def test_plugin_watchdog(coresys: CoreSys, plugin: PluginBase) -> None:
    """Test plugin watchdog works correctly."""
    with patch.object(type(plugin.instance), "attach"), patch.object(
        type(plugin.instance), "is_running", return_value=mock_is_running(True)
    ):
        await plugin.load()

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
        (PluginAudio, AudioError()),
        (PluginCli, CliError()),
        (PluginDns, CoreDNSError()),
        (PluginMulticast, MulticastError()),
        (PluginObserver, ObserverError()),
    ],
    indirect=["plugin"],
)
async def test_plugin_watchdog_rebuild_on_failure(
    coresys: CoreSys, capture_exception: Mock, plugin: PluginBase, error: PluginError
) -> None:
    """Test plugin watchdog rebuilds if start fails."""
    with patch.object(type(plugin.instance), "attach"), patch.object(
        type(plugin.instance), "is_running", return_value=mock_is_running(True)
    ):
        await plugin.load()

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

    capture_exception.assert_called_once_with(error)


@pytest.mark.parametrize(
    "plugin",
    [PluginAudio, PluginCli, PluginDns, PluginMulticast, PluginObserver],
    indirect=True,
)
async def test_plugin_load_running_container(
    coresys: CoreSys, plugin: PluginBase
) -> None:
    """Test plugins load and attach to a running container."""
    test_version = AwesomeVersion("2022.7.3")
    with patch.object(
        type(coresys.bus), "register_event"
    ) as register_event, patch.object(
        type(plugin.instance), "attach"
    ) as attach, patch.object(
        type(plugin), "install"
    ) as install, patch.object(
        type(plugin), "start"
    ) as start, patch.object(
        type(plugin.instance),
        "get_latest_version",
        return_value=mock_get_latest_version(test_version),
    ), patch.object(
        type(plugin.instance), "is_running", return_value=mock_is_running(True)
    ):
        await plugin.load()
        register_event.assert_any_call(
            BusEvent.DOCKER_CONTAINER_STATE_CHANGE, plugin.watchdog_container
        )
        attach.assert_called_once_with(
            version=test_version, skip_state_event_if_down=True
        )
        install.assert_not_called()
        start.assert_not_called()


@pytest.mark.parametrize(
    "plugin",
    [PluginAudio, PluginCli, PluginDns, PluginMulticast, PluginObserver],
    indirect=True,
)
async def test_plugin_load_stopped_container(
    coresys: CoreSys, plugin: PluginBase
) -> None:
    """Test plugins load and start existing container."""
    test_version = AwesomeVersion("2022.7.3")
    with patch.object(
        type(coresys.bus), "register_event"
    ) as register_event, patch.object(
        type(plugin.instance), "attach"
    ) as attach, patch.object(
        type(plugin), "install"
    ) as install, patch.object(
        type(plugin), "start"
    ) as start, patch.object(
        type(plugin.instance),
        "get_latest_version",
        return_value=mock_get_latest_version(test_version),
    ), patch.object(
        type(plugin.instance), "is_running", return_value=mock_is_running(False)
    ):
        await plugin.load()
        register_event.assert_any_call(
            BusEvent.DOCKER_CONTAINER_STATE_CHANGE, plugin.watchdog_container
        )
        attach.assert_called_once_with(
            version=test_version, skip_state_event_if_down=True
        )
        install.assert_not_called()
        start.assert_called_once()


@pytest.mark.parametrize(
    "plugin",
    [PluginAudio, PluginCli, PluginDns, PluginMulticast, PluginObserver],
    indirect=True,
)
async def test_plugin_load_missing_container(
    coresys: CoreSys, plugin: PluginBase
) -> None:
    """Test plugins load and create and start container."""
    test_version = AwesomeVersion("2022.7.3")
    with patch.object(
        type(coresys.bus), "register_event"
    ) as register_event, patch.object(
        type(plugin.instance), "attach", side_effect=DockerError()
    ) as attach, patch.object(
        type(plugin), "install"
    ) as install, patch.object(
        type(plugin), "start"
    ) as start, patch.object(
        type(plugin.instance),
        "get_latest_version",
        return_value=mock_get_latest_version(test_version),
    ), patch.object(
        type(plugin.instance), "is_running", return_value=mock_is_running(False)
    ):
        await plugin.load()
        register_event.assert_any_call(
            BusEvent.DOCKER_CONTAINER_STATE_CHANGE, plugin.watchdog_container
        )
        attach.assert_called_once_with(
            version=test_version, skip_state_event_if_down=True
        )
        install.assert_called_once()
        start.assert_called_once()


@pytest.mark.parametrize(
    "plugin,error",
    [
        (PluginAudio, AudioJobError),
        (PluginCli, CliJobError),
        (PluginDns, CoreDNSJobError),
        (PluginMulticast, MulticastJobError),
        (PluginObserver, ObserverJobError),
    ],
    indirect=["plugin"],
)
async def test_update_fails_if_out_of_date(
    coresys: CoreSys, plugin: PluginBase, error: PluginJobError
):
    """Test update of plugins fail when supervisor is out of date."""
    coresys.hardware.disk.get_disk_free_space = lambda x: 5000

    with patch.object(
        type(coresys.supervisor), "need_update", new=PropertyMock(return_value=True)
    ), pytest.raises(error):
        await plugin.update()


@pytest.mark.parametrize(
    "plugin",
    [PluginAudio, PluginCli, PluginDns, PluginMulticast, PluginObserver],
    indirect=True,
)
async def test_repair_failed(
    coresys: CoreSys, capture_exception: Mock, plugin: PluginBase
):
    """Test repair failed."""
    with patch.object(
        DockerInterface, "exists", return_value=mock_is_running(False)
    ), patch.object(
        DockerInterface, "arch", new=PropertyMock(return_value=CpuArch.AMD64)
    ), patch(
        "supervisor.security.module.cas_validate", side_effect=CodeNotaryUntrusted
    ):
        await plugin.repair()

    capture_exception.assert_called_once()
    assert check_exception_chain(capture_exception.call_args[0][0], CodeNotaryUntrusted)
