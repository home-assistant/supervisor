"""Test multicast plugin."""

from unittest.mock import AsyncMock, PropertyMock, patch

from awesomeversion import AwesomeVersion
import pytest

from supervisor.const import BusEvent
from supervisor.coresys import CoreSys
from supervisor.docker.const import ContainerState
from supervisor.docker.monitor import DockerContainerStateEvent
from supervisor.docker.multicast import DockerMulticast
from supervisor.exceptions import (
    DockerContainerNotFoundError,
    DockerContainerNotRunningError,
    DockerError,
    DockerStatsTimeoutError,
    MulticastDisabledError,
    MulticastError,
    MulticastNotRunningError,
    MulticastStatsTimeoutError,
    MulticastUnknownError,
)


async def test_stats_not_running(coresys: CoreSys):
    """Test stats raises MulticastNotRunningError when the container isn't running."""
    with (
        patch.object(
            DockerMulticast,
            "stats",
            AsyncMock(
                side_effect=DockerContainerNotRunningError(name="hassio_multicast")
            ),
        ),
        pytest.raises(MulticastNotRunningError),
    ):
        await coresys.plugins.multicast.stats()

    with (
        patch.object(
            DockerMulticast,
            "stats",
            AsyncMock(
                side_effect=DockerContainerNotFoundError(name="hassio_multicast")
            ),
        ),
        pytest.raises(MulticastNotRunningError),
    ):
        await coresys.plugins.multicast.stats()


async def test_stats_timeout(coresys: CoreSys):
    """Test stats raises MulticastStatsTimeoutError on timeout."""
    with (
        patch.object(
            DockerMulticast,
            "stats",
            AsyncMock(side_effect=DockerStatsTimeoutError(name="hassio_multicast")),
        ),
        pytest.raises(MulticastStatsTimeoutError),
    ):
        await coresys.plugins.multicast.stats()


async def test_stats_unknown_error(coresys: CoreSys):
    """Test stats raises MulticastUnknownError on an unexpected Docker error."""
    with (
        patch.object(
            DockerMulticast, "stats", AsyncMock(side_effect=DockerError("boom"))
        ),
        pytest.raises(MulticastUnknownError),
    ):
        await coresys.plugins.multicast.stats()


async def test_enabled_default(coresys: CoreSys):
    """Test the multicast plugin is enabled by default."""
    assert coresys.plugins.multicast.enabled is True


async def test_load_disabled(coresys: CoreSys):
    """Test load skips install and start but stops leftovers when disabled."""
    coresys.plugins.multicast._data["enabled"] = False  # pylint: disable=protected-access

    with (
        patch.object(type(coresys.bus), "register_event") as register_event,
        patch.object(DockerMulticast, "attach") as attach,
        patch.object(DockerMulticast, "stop") as stop,
        patch.object(type(coresys.plugins.multicast), "install") as install,
        patch.object(DockerMulticast, "run") as run,
    ):
        await coresys.plugins.multicast.load()

        register_event.assert_any_call(
            BusEvent.DOCKER_CONTAINER_STATE_CHANGE,
            coresys.plugins.multicast.watchdog_container,
        )
        attach.assert_not_called()
        install.assert_not_called()
        run.assert_not_called()
        stop.assert_called_once()


async def test_watchdog_ignored_when_disabled(coresys: CoreSys):
    """Test the watchdog does not restart the plugin while disabled."""
    coresys.plugins.multicast._data["enabled"] = False  # pylint: disable=protected-access

    with patch.object(
        type(coresys.plugins.multicast), "_restart_after_problem"
    ) as restart_after_problem:
        await coresys.plugins.multicast.watchdog_container(
            DockerContainerStateEvent(
                name="hassio_multicast",
                state=ContainerState.FAILED,
                id="abc123",
                time=1,
            )
        )
        restart_after_problem.assert_not_called()


async def test_disable(coresys: CoreSys):
    """Test disabling removes container and image and forgets the version."""
    coresys.plugins.multicast.version = AwesomeVersion("2024.01.0")

    with (
        patch.object(DockerMulticast, "remove") as remove,
        patch.object(type(coresys.plugins.multicast), "save_data") as save_data,
    ):
        await coresys.plugins.multicast.disable()

    remove.assert_called_once()
    assert save_data.called
    assert coresys.plugins.multicast.enabled is False
    assert coresys.plugins.multicast.version is None
    assert coresys.plugins.multicast.need_update is False

    # Disabling again is a no-op
    with patch.object(DockerMulticast, "remove") as remove:
        await coresys.plugins.multicast.disable()
    remove.assert_not_called()


async def test_disable_remove_failure(coresys: CoreSys):
    """Test disabling persists the disabled state even if removal fails."""
    coresys.plugins.multicast.version = AwesomeVersion("2024.01.0")

    with (
        patch.object(DockerMulticast, "remove", side_effect=DockerError("boom")),
        patch.object(type(coresys.plugins.multicast), "save_data"),
        pytest.raises(MulticastError),
    ):
        await coresys.plugins.multicast.disable()

    assert coresys.plugins.multicast.enabled is False
    # Version is kept so the leftover image can still be cleaned up later
    assert coresys.plugins.multicast.version == AwesomeVersion("2024.01.0")


@pytest.mark.usefixtures("supervisor_internet")
async def test_enable(coresys: CoreSys):
    """Test enabling installs and starts the plugin."""
    coresys.hardware.disk.get_disk_free_space = lambda x: 5000
    coresys.plugins.multicast._data["enabled"] = False  # pylint: disable=protected-access
    coresys.plugins.multicast._data.pop("version", None)  # pylint: disable=protected-access

    with (
        patch.object(
            type(coresys.plugins.multicast),
            "latest_version",
            new=PropertyMock(return_value=AwesomeVersion("2024.01.0")),
        ),
        patch.object(DockerMulticast, "install") as install,
        patch.object(DockerMulticast, "run") as run,
        patch.object(type(coresys.plugins.multicast), "save_data") as save_data,
    ):
        await coresys.plugins.multicast.enable()

    install.assert_called_once()
    run.assert_called_once()
    assert save_data.called
    assert coresys.plugins.multicast.enabled is True
    assert coresys.plugins.multicast.version == AwesomeVersion("2024.01.0")

    # Enabling again is a no-op
    with patch.object(DockerMulticast, "install") as install:
        await coresys.plugins.multicast.enable()
    install.assert_not_called()


async def test_actions_rejected_when_disabled(coresys: CoreSys):
    """Test start, restart and update refuse to run while disabled."""
    coresys.plugins.multicast._data["enabled"] = False  # pylint: disable=protected-access

    with pytest.raises(MulticastDisabledError):
        await coresys.plugins.multicast.start()
    with pytest.raises(MulticastDisabledError):
        await coresys.plugins.multicast.restart()

    coresys.hardware.disk.get_disk_free_space = lambda x: 5000
    with (
        patch.object(
            type(coresys.plugins.multicast),
            "latest_version",
            new=PropertyMock(return_value=AwesomeVersion("2024.01.0")),
        ),
        pytest.raises(MulticastDisabledError),
    ):
        await coresys.plugins.multicast.update()


async def test_repair_skipped_when_disabled(coresys: CoreSys):
    """Test repair does nothing while disabled."""
    coresys.plugins.multicast._data["enabled"] = False  # pylint: disable=protected-access

    with (
        patch.object(DockerMulticast, "exists", return_value=False),
        patch.object(DockerMulticast, "install") as install,
    ):
        await coresys.plugins.multicast.repair()

    install.assert_not_called()
