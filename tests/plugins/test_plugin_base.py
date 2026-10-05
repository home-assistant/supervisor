"""Test base plugin functionality."""

import asyncio
from unittest.mock import ANY, Mock, PropertyMock, call, patch

from aiodocker.containers import DockerContainer
from awesomeversion import AwesomeVersion
import pytest

from supervisor.const import BusEvent, CpuArch
from supervisor.coresys import CoreSys
from supervisor.docker.const import ContainerState
from supervisor.docker.interface import DockerInterface
from supervisor.docker.manager import DockerAPI
from supervisor.docker.monitor import DockerContainerStateEvent
from supervisor.exceptions import (
    AudioError,
    AudioJobError,
    AudioUpdateError,
    CliError,
    CliJobError,
    CliUpdateError,
    CoreDNSError,
    CoreDNSJobError,
    CoreDNSUpdateError,
    DockerError,
    MulticastDisabledError,
    MulticastError,
    MulticastJobError,
    ObserverError,
    ObserverJobError,
    ObserverUpdateError,
    PluginDisabledError,
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

from tests.common import fire_bus_event


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
        await fire_bus_event(
            coresys,
            BusEvent.DOCKER_CONTAINER_STATE_CHANGE,
            DockerContainerStateEvent(
                name=plugin.instance.name,
                state=ContainerState.UNHEALTHY,
                id="abc123",
                time=1,
            ),
        )
        rebuild.assert_called_once()
        start.assert_not_called()

        rebuild.reset_mock()
        current_state.return_value = ContainerState.FAILED
        await fire_bus_event(
            coresys,
            BusEvent.DOCKER_CONTAINER_STATE_CHANGE,
            DockerContainerStateEvent(
                name=plugin.instance.name,
                state=ContainerState.FAILED,
                id="abc123",
                time=1,
                exit_code=1,
            ),
        )
        rebuild.assert_called_once()
        start.assert_not_called()

        rebuild.reset_mock()
        # Stop should be ignored as it means an update or system shutdown, plugins don't stop otherwise
        current_state.return_value = ContainerState.STOPPED
        await fire_bus_event(
            coresys,
            BusEvent.DOCKER_CONTAINER_STATE_CHANGE,
            DockerContainerStateEvent(
                name=plugin.instance.name,
                state=ContainerState.STOPPED,
                id="abc123",
                time=1,
            ),
        )
        rebuild.assert_not_called()
        start.assert_not_called()

        # Do not process event if container state has changed since fired
        current_state.return_value = ContainerState.HEALTHY
        await fire_bus_event(
            coresys,
            BusEvent.DOCKER_CONTAINER_STATE_CHANGE,
            DockerContainerStateEvent(
                name=plugin.instance.name,
                state=ContainerState.FAILED,
                id="abc123",
                time=1,
                exit_code=1,
            ),
        )
        rebuild.assert_not_called()
        start.assert_not_called()

        # Other containers ignored
        await fire_bus_event(
            coresys,
            BusEvent.DOCKER_CONTAINER_STATE_CHANGE,
            DockerContainerStateEvent(
                name="app_local_other",
                state=ContainerState.UNHEALTHY,
                id="abc123",
                time=1,
            ),
        )
        rebuild.assert_not_called()
        start.assert_not_called()


@pytest.mark.parametrize(
    ("plugin", "error"),
    [
        (PluginAudio, AudioError()),
        (PluginCli, CliError()),
        (PluginDns, CoreDNSError()),
        (PluginMulticast, MulticastError()),
        (PluginObserver, ObserverError()),
    ],
    indirect=["plugin"],
)
@pytest.mark.usefixtures("coresys", "tmp_supervisor_data", "path_extern")
async def test_plugin_watchdog_max_failed_attempts(
    capture_exception: Mock,
    plugin: PluginBase,
    error: PluginError,
    container: DockerContainer,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test plugin watchdog gives up after max failed attempts."""
    with patch.object(type(plugin.instance), "attach"):
        await plugin.load()

    container.show.return_value["State"]["Status"] = "stopped"
    container.show.return_value["State"]["Running"] = False
    container.show.return_value["State"]["ExitCode"] = 1
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
                exit_code=1,
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
    ("plugin", "error"),
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
@pytest.mark.usefixtures("coresys")
async def test_repair_failed(capture_exception: Mock, plugin: PluginBase):
    """Test repair failed."""
    with (
        patch.object(DockerInterface, "exists", return_value=False),
        patch.object(
            DockerInterface, "arch", new=PropertyMock(return_value=CpuArch.AMD64)
        ),
        patch.object(DockerInterface, "install", side_effect=DockerError),
    ):
        await plugin.repair()

    capture_exception.assert_called_once()
    assert check_exception_chain(capture_exception.call_args[0][0], DockerError)


@pytest.mark.parametrize(
    "plugin",
    [PluginAudio, PluginCli, PluginDns, PluginMulticast, PluginObserver],
    indirect=True,
)
async def test_load_with_incorrect_image(
    coresys: CoreSys, container: DockerContainer, plugin: PluginBase
):
    """Test plugin loads with the incorrect image."""
    plugin.image = old_image = f"ghcr.io/home-assistant/aarch64-hassio-{plugin.slug}"
    correct_image = f"ghcr.io/home-assistant/amd64-hassio-{plugin.slug}"
    coresys.updater._data["image"][plugin.slug] = correct_image  # pylint: disable=protected-access
    plugin.version = AwesomeVersion("2024.4.0")

    container.show.return_value["State"]["Status"] = "running"
    container.show.return_value["State"]["Running"] = True
    coresys.docker.images.inspect.return_value = img_data = (
        coresys.docker.images.inspect.return_value
        | {"Config": {"Labels": {"io.hass.version": "2024.4.0"}}}
    )
    container.show.return_value |= img_data

    with patch.object(DockerAPI, "pull_image", return_value=img_data) as pull_image:
        await plugin.load()
        pull_image.assert_called_once_with(
            ANY, correct_image, "2024.4.0", platform="linux/amd64", auth=None
        )

    container.delete.assert_called_once_with(force=True, v=True)
    assert coresys.docker.images.delete.call_args_list[0] == call(
        f"{old_image}:latest",
        force=True,
    )
    assert coresys.docker.images.delete.call_args_list[1] == call(
        f"{old_image}:2024.4.0",
        force=True,
    )
    assert plugin.image == correct_image


@pytest.mark.parametrize(
    "plugin",
    [PluginAudio, PluginCli, PluginDns, PluginMulticast, PluginObserver],
    indirect=True,
)
async def test_default_image_fallback(coresys: CoreSys, plugin: PluginBase):
    """Test default image falls back to hard-coded constant if we fail to fetch version file."""
    assert getattr(coresys.updater, f"image_{plugin.slug}") is None
    assert plugin.default_image == f"ghcr.io/home-assistant/amd64-hassio-{plugin.slug}"


ALL_PLUGINS = [PluginAudio, PluginCli, PluginDns, PluginMulticast, PluginObserver]


@pytest.mark.parametrize("plugin", ALL_PLUGINS, indirect=True)
async def test_plugin_enabled_default(plugin: PluginBase) -> None:
    """Test plugins are enabled by default."""
    assert plugin.enabled is True


@pytest.mark.parametrize("plugin", ALL_PLUGINS, indirect=True)
async def test_plugin_load_disabled(coresys: CoreSys, plugin: PluginBase) -> None:
    """Test load skips install and start but cleans up leftovers when disabled."""
    plugin._data["enabled"] = False  # pylint: disable=protected-access
    plugin.version = AwesomeVersion("2024.01.0")

    with (
        patch.object(type(coresys.bus), "register_event") as register_event,
        patch.object(type(plugin.instance), "attach") as attach,
        patch.object(type(plugin.instance), "stop") as stop,
        patch.object(DockerAPI, "remove_image") as remove_image,
        patch.object(type(plugin), "install") as install,
        patch.object(type(plugin), "start") as start,
        patch.object(type(plugin), "save_data"),
    ):
        await plugin.load()

    register_event.assert_any_call(
        BusEvent.DOCKER_CONTAINER_STATE_CHANGE, plugin.watchdog_container
    )
    attach.assert_not_called()
    install.assert_not_called()
    start.assert_not_called()
    stop.assert_called_once()
    remove_image.assert_called_once_with(plugin.image, AwesomeVersion("2024.01.0"))
    assert plugin.version is None


@pytest.mark.parametrize("plugin", ALL_PLUGINS, indirect=True)
async def test_plugin_load_disabled_cleanup_failure(plugin: PluginBase) -> None:
    """Test load tolerates a failing leftover cleanup when disabled."""
    plugin._data["enabled"] = False  # pylint: disable=protected-access
    plugin.version = AwesomeVersion("2024.01.0")

    with (
        patch.object(type(plugin.instance), "stop", side_effect=DockerError("boom")),
        patch.object(DockerAPI, "remove_image") as remove_image,
    ):
        await plugin.load()

    remove_image.assert_not_called()
    assert plugin.version == AwesomeVersion("2024.01.0")


@pytest.mark.parametrize("plugin", ALL_PLUGINS, indirect=True)
async def test_plugin_watchdog_ignored_when_disabled(plugin: PluginBase) -> None:
    """Test the watchdog does not restart the plugin while disabled."""
    plugin._data["enabled"] = False  # pylint: disable=protected-access

    with patch.object(type(plugin), "_restart_after_problem") as restart_after_problem:
        await plugin.watchdog_container(
            DockerContainerStateEvent(
                name=plugin.instance.name,
                state=ContainerState.FAILED,
                id="abc123",
                time=1,
            )
        )

    restart_after_problem.assert_not_called()


@pytest.mark.parametrize("plugin", ALL_PLUGINS, indirect=True)
async def test_plugin_disable(plugin: PluginBase) -> None:
    """Test disabling removes container and image and forgets the version."""
    plugin.version = AwesomeVersion("2024.01.0")

    with (
        patch.object(type(plugin.instance), "stop") as stop,
        patch.object(DockerAPI, "remove_image") as remove_image,
        patch.object(type(plugin), "save_data") as save_data,
    ):
        await plugin.disable()

    stop.assert_called_once()
    remove_image.assert_called_once_with(plugin.image, AwesomeVersion("2024.01.0"))
    assert save_data.called
    assert plugin.enabled is False
    assert plugin.version is None
    assert plugin.need_update is False

    # Disabling again only makes sure the container is gone
    with (
        patch.object(type(plugin.instance), "stop") as stop,
        patch.object(DockerAPI, "remove_image") as remove_image,
    ):
        await plugin.disable()

    stop.assert_called_once()
    remove_image.assert_not_called()


@pytest.mark.parametrize("plugin", ALL_PLUGINS, indirect=True)
async def test_plugin_disable_remove_failure_retried(plugin: PluginBase) -> None:
    """Test a failed removal persists the disabled state and is retried."""
    plugin.version = AwesomeVersion("2024.01.0")

    with (
        patch.object(type(plugin.instance), "stop"),
        patch.object(DockerAPI, "remove_image", side_effect=DockerError("boom")),
        patch.object(type(plugin), "save_data"),
        pytest.raises(PluginError),
    ):
        await plugin.disable()

    assert plugin.enabled is False
    # Version is kept so the leftover image can be cleaned up on retry
    assert plugin.version == AwesomeVersion("2024.01.0")

    with (
        patch.object(type(plugin.instance), "stop"),
        patch.object(DockerAPI, "remove_image") as remove_image,
        patch.object(type(plugin), "save_data"),
    ):
        await plugin.disable()

    remove_image.assert_called_once()
    assert plugin.version is None


@pytest.mark.usefixtures("supervisor_internet")
@pytest.mark.parametrize("plugin", ALL_PLUGINS, indirect=True)
async def test_plugin_enable(coresys: CoreSys, plugin: PluginBase) -> None:
    """Test enabling installs and starts the plugin."""
    coresys.hardware.disk.get_disk_free_space = lambda x: 5000
    plugin._data["enabled"] = False  # pylint: disable=protected-access
    plugin._data.pop("version", None)  # pylint: disable=protected-access

    with (
        patch.object(
            type(plugin),
            "latest_version",
            new=PropertyMock(return_value=AwesomeVersion("2024.01.0")),
        ),
        patch.object(type(plugin.instance), "install") as install,
        patch.object(type(plugin), "start") as start,
        patch.object(type(plugin), "save_data") as save_data,
    ):
        await plugin.enable()

    install.assert_called_once()
    start.assert_called_once()
    assert save_data.called
    assert plugin.enabled is True
    assert plugin.version == AwesomeVersion("2024.01.0")

    # Enabling a running plugin again is a no-op
    with (
        patch.object(type(plugin.instance), "is_running", return_value=True),
        patch.object(type(plugin.instance), "install") as install,
        patch.object(type(plugin), "start") as start,
    ):
        await plugin.enable()

    install.assert_not_called()
    start.assert_not_called()


@pytest.mark.usefixtures("supervisor_internet")
@pytest.mark.parametrize("plugin", ALL_PLUGINS, indirect=True)
async def test_plugin_enable_leftover_version_reinstalls(
    coresys: CoreSys, plugin: PluginBase
) -> None:
    """Test enabling a disabled plugin with a leftover version cleans it up first."""
    coresys.hardware.disk.get_disk_free_space = lambda x: 5000
    plugin._data["enabled"] = False  # pylint: disable=protected-access
    plugin.version = AwesomeVersion("2023.01.0")

    with (
        patch.object(
            type(plugin),
            "latest_version",
            new=PropertyMock(return_value=AwesomeVersion("2024.01.0")),
        ),
        patch.object(type(plugin.instance), "stop") as stop,
        patch.object(DockerAPI, "remove_image") as remove_image,
        patch.object(type(plugin.instance), "install") as install,
        patch.object(type(plugin), "start") as start,
        patch.object(type(plugin), "save_data"),
    ):
        await plugin.enable()

    stop.assert_called_once()
    remove_image.assert_called_once_with(plugin.image, AwesomeVersion("2023.01.0"))
    install.assert_called_once()
    start.assert_called_once()
    assert plugin.version == AwesomeVersion("2024.01.0")

    # A failing cleanup keeps the plugin disabled so enable can be retried
    plugin._data["enabled"] = False  # pylint: disable=protected-access
    plugin.version = AwesomeVersion("2023.01.0")
    with (
        patch.object(type(plugin.instance), "stop", side_effect=DockerError("boom")),
        patch.object(type(plugin.instance), "install") as install,
        pytest.raises(PluginError),
    ):
        await plugin.enable()

    install.assert_not_called()
    assert plugin.enabled is False
    assert plugin.version == AwesomeVersion("2023.01.0")


@pytest.mark.usefixtures("supervisor_internet")
@pytest.mark.parametrize("plugin", ALL_PLUGINS, indirect=True)
async def test_plugin_enable_start_failure_retried(
    coresys: CoreSys, plugin: PluginBase
) -> None:
    """Test a failed start after enabling is retried on the next enable."""
    coresys.hardware.disk.get_disk_free_space = lambda x: 5000
    plugin._data["enabled"] = False  # pylint: disable=protected-access
    plugin._data.pop("version", None)  # pylint: disable=protected-access

    with (
        patch.object(
            type(plugin),
            "latest_version",
            new=PropertyMock(return_value=AwesomeVersion("2024.01.0")),
        ),
        patch.object(type(plugin.instance), "install"),
        patch.object(type(plugin), "start", side_effect=PluginError("boom")),
        patch.object(type(plugin), "save_data"),
        pytest.raises(PluginError),
    ):
        await plugin.enable()

    assert plugin.enabled is True
    assert plugin.version == AwesomeVersion("2024.01.0")

    with (
        patch.object(type(plugin.instance), "is_running", return_value=False),
        patch.object(type(plugin.instance), "install") as install,
        patch.object(type(plugin), "start") as start,
    ):
        await plugin.enable()

    install.assert_not_called()
    start.assert_called_once()


@pytest.mark.usefixtures("supervisor_internet")
@pytest.mark.parametrize("plugin", ALL_PLUGINS, indirect=True)
async def test_plugin_enable_install_failure(
    coresys: CoreSys, plugin: PluginBase
) -> None:
    """Test an install failure while enabling is raised instead of retried."""
    coresys.hardware.disk.get_disk_free_space = lambda x: 5000
    plugin._data["enabled"] = False  # pylint: disable=protected-access
    plugin._data.pop("version", None)  # pylint: disable=protected-access

    with (
        patch.object(
            type(plugin),
            "latest_version",
            new=PropertyMock(return_value=AwesomeVersion("2024.01.0")),
        ),
        patch.object(
            type(plugin.instance), "install", side_effect=DockerError("boom")
        ) as install,
        patch.object(type(plugin), "start") as start,
        patch.object(type(plugin), "save_data"),
        pytest.raises(PluginError),
    ):
        await plugin.enable()

    install.assert_called_once()
    start.assert_not_called()
    assert plugin.version is None


@pytest.mark.usefixtures("supervisor_internet")
@pytest.mark.parametrize("plugin", ALL_PLUGINS, indirect=True)
async def test_plugin_enable_disable_serialized(
    coresys: CoreSys, plugin: PluginBase
) -> None:
    """Test a disable waits for an in-progress enable to finish."""
    coresys.hardware.disk.get_disk_free_space = lambda x: 5000
    plugin._data["enabled"] = False  # pylint: disable=protected-access
    plugin._data.pop("version", None)  # pylint: disable=protected-access
    install_started = asyncio.Event()
    finish_install = asyncio.Event()

    async def _install(*args, **kwargs) -> None:
        install_started.set()
        await finish_install.wait()

    with (
        patch.object(
            type(plugin),
            "latest_version",
            new=PropertyMock(return_value=AwesomeVersion("2024.01.0")),
        ),
        patch.object(type(plugin.instance), "install", new=_install),
        patch.object(type(plugin), "start") as start,
        patch.object(type(plugin.instance), "stop") as stop,
        patch.object(DockerAPI, "remove_image") as remove_image,
        patch.object(type(plugin), "save_data"),
    ):
        enable_task = asyncio.create_task(plugin.enable())
        await install_started.wait()
        disable_task = asyncio.create_task(plugin.disable())
        await asyncio.sleep(0)

        # Disable is blocked until enable completes
        assert not disable_task.done()
        stop.assert_not_called()
        assert plugin.enabled is True

        finish_install.set()
        await asyncio.gather(enable_task, disable_task)

    start.assert_called_once()
    stop.assert_called_once()
    remove_image.assert_called_once_with(plugin.image, AwesomeVersion("2024.01.0"))
    assert plugin.enabled is False
    assert plugin.version is None


@pytest.mark.parametrize(
    ("plugin", "error"),
    [
        (PluginAudio, AudioUpdateError),
        (PluginCli, CliUpdateError),
        (PluginDns, CoreDNSUpdateError),
        (PluginMulticast, MulticastDisabledError),
        (PluginObserver, ObserverUpdateError),
    ],
    indirect=["plugin"],
)
async def test_plugin_update_rejected_when_disabled(
    coresys: CoreSys, plugin: PluginBase, error: type[PluginError]
) -> None:
    """Test update refuses to run while disabled."""
    coresys.hardware.disk.get_disk_free_space = lambda x: 5000
    plugin._data["enabled"] = False  # pylint: disable=protected-access

    with (
        patch.object(
            type(plugin),
            "latest_version",
            new=PropertyMock(return_value=AwesomeVersion("2024.01.0")),
        ),
        patch.object(type(plugin.instance), "update") as update,
        pytest.raises(error) as exc_info,
    ):
        await plugin.update()

    update.assert_not_called()
    assert check_exception_chain(exc_info.value, PluginDisabledError)


@pytest.mark.parametrize("plugin", ALL_PLUGINS, indirect=True)
async def test_plugin_watchdog_stops_when_disabled(plugin: PluginBase) -> None:
    """Test the watchdog restart loop gives up once the plugin is disabled."""
    plugin._data["enabled"] = False  # pylint: disable=protected-access

    with (
        patch.object(
            type(plugin.instance),
            "current_state",
            return_value=ContainerState.FAILED,
        ),
        patch.object(type(plugin), "rebuild") as rebuild,
    ):
        await plugin._restart_after_problem(ContainerState.FAILED, 1)  # pylint: disable=protected-access

    rebuild.assert_not_called()
