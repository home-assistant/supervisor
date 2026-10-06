"""Test multicast plugin."""

import asyncio
from contextlib import AbstractContextManager, nullcontext
from unittest.mock import AsyncMock, PropertyMock, patch

from awesomeversion import AwesomeVersion
import pytest

from supervisor.coresys import CoreSys
from supervisor.docker.manager import DockerAPI
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
    PluginError,
)
from supervisor.plugins.base import PluginBase
from supervisor.plugins.multicast import PluginMulticast


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


@pytest.mark.usefixtures("supervisor_internet")
async def test_enable_failure(coresys: CoreSys):
    """Test enable translates plugin errors into MulticastError."""
    coresys.hardware.disk.get_disk_free_space = lambda x: 5000

    with (
        patch.object(PluginBase, "enable", side_effect=PluginError("boom")),
        pytest.raises(MulticastError),
    ):
        await coresys.plugins.multicast.enable()


async def test_disable_failure(coresys: CoreSys):
    """Test disable translates plugin errors into MulticastError."""
    with (
        patch.object(PluginBase, "disable", side_effect=PluginError("boom")),
        pytest.raises(MulticastError),
    ):
        await coresys.plugins.multicast.disable()


@pytest.mark.parametrize("action", ["start", "restart"])
async def test_actions_rejected_when_disabled(coresys: CoreSys, action: str):
    """Test start and restart refuse to run while disabled."""
    coresys.plugins.multicast._data["enabled"] = False  # pylint: disable=protected-access

    with pytest.raises(MulticastDisabledError):
        await getattr(coresys.plugins.multicast, action)()


async def test_repair_skipped_when_disabled(coresys: CoreSys):
    """Test repair does nothing while disabled."""
    coresys.plugins.multicast._data["enabled"] = False  # pylint: disable=protected-access

    with (
        patch.object(DockerMulticast, "exists", return_value=False),
        patch.object(DockerMulticast, "install") as install,
    ):
        await coresys.plugins.multicast.repair()

    install.assert_not_called()


@pytest.mark.parametrize(
    ("action", "expectation"),
    [
        pytest.param("update", pytest.raises(MulticastDisabledError), id="update"),
        pytest.param("restart", pytest.raises(MulticastDisabledError), id="restart"),
        pytest.param("repair", nullcontext(), id="repair"),
    ],
)
async def test_lifecycle_actions_wait_for_disable(
    coresys: CoreSys, action: str, expectation: AbstractContextManager
):
    """Test update, restart and repair wait for an in-progress disable."""
    coresys.hardware.disk.get_disk_free_space = lambda x: 5000
    coresys.plugins.multicast.version = AwesomeVersion("2024.01.0")
    stop_started = asyncio.Event()
    finish_stop = asyncio.Event()

    async def _stop(*args, **kwargs) -> None:
        stop_started.set()
        await finish_stop.wait()

    with (
        patch.object(
            PluginMulticast,
            "latest_version",
            new=PropertyMock(return_value=AwesomeVersion("2025.01.0")),
        ),
        patch.object(DockerMulticast, "stop", new=_stop),
        patch.object(DockerMulticast, "exists", return_value=False),
        patch.object(DockerMulticast, "install") as install,
        patch.object(DockerMulticast, "update") as update,
        patch.object(DockerMulticast, "restart") as restart,
        patch.object(DockerAPI, "remove_image"),
        patch.object(PluginMulticast, "save_data"),
    ):
        disable_task = asyncio.create_task(coresys.plugins.multicast.disable())
        await stop_started.wait()
        action_task = asyncio.create_task(getattr(coresys.plugins.multicast, action)())
        await asyncio.sleep(0)

        assert not action_task.done()

        finish_stop.set()
        await disable_task
        with expectation:
            await action_task

    install.assert_not_called()
    update.assert_not_called()
    restart.assert_not_called()
    assert coresys.plugins.multicast.enabled is False
    assert coresys.plugins.multicast.version is None
