"""Test multicast plugin."""

from unittest.mock import AsyncMock, patch

import pytest

from supervisor.coresys import CoreSys
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
