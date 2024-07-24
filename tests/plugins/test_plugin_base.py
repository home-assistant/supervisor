"""Test base plugin functionality."""

import asyncio
from unittest.mock import MagicMock, Mock, PropertyMock, patch

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


@pytest.mark.parametrize(
    "plugin",
    [PluginAudio, PluginCli, PluginDns, PluginMulticast, PluginObserver],
    indirect=True,
)
async def test_plugin_watchdog(coresys: CoreSys, plugin: PluginBase) -> None:
    """Test plugin watchdog works correctly."""
    with (
        patch.object(type(plugin.instance), "attach"),
        patch.object(type(plugin.instance), "is_running", return_value=True),
    ):
        await plugin.load()

    with (
        patch.object(type(plugin), "rebuild") as rebuild,
        patch.object(type(plugin), "start") as start,
        patch.object(type(plugin.instance), "current_state") as current_state,
    ):
        current_state.return_value = ContainerState.UNHEALTHY
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
        current_state.return_value = ContainerState.FAILED
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
        # Stop should be ignored as it means an update or system shutdown, plugins don't stop otherwise
        current_state.return_value = ContainerState.STOPPED
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
        start.assert_not_called()

        # Do not process event if container state has changed since fired
        current_state.return_value = ContainerState.HEALTHY
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
async def test_plugin_watchdog_max_failed_attempts(
    coresys: CoreSys,
    capture_exception: Mock,
    plugin: PluginBase,
    error: PluginError,
    container: MagicMock,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test plugin watchdog gives up after max failed attempts."""
    with patch.object(type(plugin.instance), "attach"):
        await plugin.load()

    container.status = "stopped"
    container.attrs = {"State": {"ExitCode": 1}}
    with (
        patch("supervisor.plugins.base.WATCHDOG_RETRY_SECONDS", 0),
        patch.object(type(plugin), "start", side_effect=error) as start,
    ):
        await plugin.watchdog_container(
            DockerContainerStateEvent(
                name=plugin.instance.name,
                state=ContainerState.FAILED,
                id="abc123",
                time=1,
            )
        )
        assert start.call_count == 5

    capture_exception.assert_called_with(error)
    assert (
        f"Watchdog cannot restart {plugin.slug} plugin, failed all 5 attempts"
        in caplog.text
    )


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
    with (
        patch.object(type(coresys.bus), "register_event") as register_event,
        patch.object(type(plugin.instance), "attach") as attach,
        patch.object(type(plugin), "install") as install,
        patch.object(type(plugin), "start") as start,
        patch.object(
            type(plugin.instance),
            "get_latest_version",
            return_value=test_version,
        ),
        patch.object(type(plugin.instance), "is_running", return_value=True),
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
    with (
        patch.object(type(coresys.bus), "register_event") as register_event,
        patch.object(type(plugin.instance), "attach") as attach,
        patch.object(type(plugin), "install") as install,
        patch.object(type(plugin), "start") as start,
        patch.object(
            type(plugin.instance),
            "get_latest_version",
            return_value=test_version,
        ),
        patch.object(type(plugin.instance), "is_running", return_value=False),
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
    with (
        patch.object(type(coresys.bus), "register_event") as register_event,
        patch.object(
            type(plugin.instance), "attach", side_effect=DockerError()
        ) as attach,
        patch.object(type(plugin), "install") as install,
        patch.object(type(plugin), "start") as start,
        patch.object(
            type(plugin.instance),
            "get_latest_version",
            return_value=test_version,
        ),
        patch.object(type(plugin.instance), "is_running", return_value=False),
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

    with (
        patch.object(
            type(coresys.supervisor), "need_update", new=PropertyMock(return_value=True)
        ),
        pytest.raises(error),
    ):
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
    with (
        patch.object(DockerInterface, "exists", return_value=False),
        patch.object(
            DockerInterface, "arch", new=PropertyMock(return_value=CpuArch.AMD64)
        ),
        patch(
            "supervisor.security.module.cas_validate", side_effect=CodeNotaryUntrusted
        ),
    ):
        await plugin.repair()

    capture_exception.assert_called_once()
    assert check_exception_chain(capture_exception.call_args[0][0], CodeNotaryUntrusted)


@pytest.mark.parametrize(
    "plugin",
    [PluginAudio, PluginCli, PluginDns, PluginMulticast, PluginObserver],
    indirect=True,
)
async def test_load_with_incorrect_image(
    coresys: CoreSys, container: MagicMock, plugin: PluginBase
):
    """Test plugin loads with the incorrect image."""
    plugin.image = old_image = f"ghcr.io/home-assistant/aarch64-hassio-{plugin.slug}"
    correct_image = f"ghcr.io/home-assistant/amd64-hassio-{plugin.slug}"
    coresys.updater._data["image"][plugin.slug] = correct_image  # pylint: disable=protected-access
    plugin.version = AwesomeVersion("2024.4.0")

    container.status = "running"
    container.attrs["Config"] = {"Labels": {"io.hass.version": "2024.4.0"}}

    await plugin.load()

    container.remove.assert_called_once_with(force=True)
    assert coresys.docker.images.remove.call_args_list[0].kwargs == {
        "image": f"{old_image}:latest",
        "force": True,
    }
    assert coresys.docker.images.remove.call_args_list[1].kwargs == {
        "image": f"{old_image}:2024.4.0",
        "force": True,
    }
    coresys.docker.images.pull.assert_called_once_with(
        f"{correct_image}:2024.4.0",
        platform="linux/amd64",
    )
    assert plugin.image == correct_image


@pytest.mark.parametrize(
    "plugin",
    [PluginAudio, PluginCli, PluginDns, PluginMulticast, PluginObserver],
    indirect=True,
)
async def test_default_image_fallback(
    coresys: CoreSys, container: MagicMock, plugin: PluginBase
):
    """Test default image falls back to hard-coded constant if we fail to fetch version file."""
    assert getattr(coresys.updater, f"image_{plugin.slug}") is None
    assert plugin.default_image == f"ghcr.io/home-assistant/amd64-hassio-{plugin.slug}"
