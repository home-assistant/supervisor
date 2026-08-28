"""Test cli plugin."""

from unittest.mock import AsyncMock, patch

import pytest

from supervisor.coresys import CoreSys
from supervisor.docker.cli import DockerCli
from supervisor.exceptions import (
    CliNotRunningError,
    CliStatsTimeoutError,
    CliUnknownError,
    DockerContainerNotFoundError,
    DockerContainerNotRunningError,
    DockerError,
    DockerStatsTimeoutError,
)


async def test_stats_not_running(coresys: CoreSys):
    """Test stats raises CliNotRunningError when the container isn't running."""
    with (
        patch.object(
            DockerCli,
            "stats",
            AsyncMock(side_effect=DockerContainerNotRunningError(name="hassio_cli")),
        ),
        pytest.raises(CliNotRunningError),
    ):
        await coresys.plugins.cli.stats()

    with (
        patch.object(
            DockerCli,
            "stats",
            AsyncMock(side_effect=DockerContainerNotFoundError(name="hassio_cli")),
        ),
        pytest.raises(CliNotRunningError),
    ):
        await coresys.plugins.cli.stats()


async def test_stats_timeout(coresys: CoreSys):
    """Test stats raises CliStatsTimeoutError on timeout."""
    with (
        patch.object(
            DockerCli,
            "stats",
            AsyncMock(side_effect=DockerStatsTimeoutError(name="hassio_cli")),
        ),
        pytest.raises(CliStatsTimeoutError),
    ):
        await coresys.plugins.cli.stats()


async def test_stats_unknown_error(coresys: CoreSys):
    """Test stats raises CliUnknownError on an unexpected Docker error."""
    with (
        patch.object(DockerCli, "stats", AsyncMock(side_effect=DockerError("boom"))),
        pytest.raises(CliUnknownError),
    ):
        await coresys.plugins.cli.stats()
