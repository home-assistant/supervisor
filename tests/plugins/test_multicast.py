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
