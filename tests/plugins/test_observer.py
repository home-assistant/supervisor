"""Test observer plugin."""

from http import HTTPStatus
from unittest.mock import AsyncMock, patch

import aiodocker
import pytest

from supervisor.coresys import CoreSys
from supervisor.docker.observer import DockerObserver
from supervisor.exceptions import (
    DockerContainerNotFoundError,
    DockerContainerNotRunningError,
    DockerError,
    DockerStatsTimeoutError,
    ObserverNotRunningError,
    ObserverPortConflict,
    ObserverStatsTimeoutError,
    ObserverUnknownError,
)


@pytest.mark.parametrize(
    "docker_message",
    [
        "failed to set up container networking: driver failed programming external connectivity on endpoint hassio_observer (ea4d0fdaa72cf86f2c9199a04208e3eaf0c5a0d6fd34b3c7f4fab2daadb1f3a9): failed to bind host port for 0.0.0.0:4357:172.30.33.4:80/tcp: address already in use",
        "failed to set up container networking: driver failed programming external connectivity on endpoint hassio_observer (ea4d0fdaa72cf86f2c9199a04208e3eaf0c5a0d6fd34b3c7f4fab2daadb1f3a9): Bind for 0.0.0.0:4357 failed: port is already allocated",
        "failed to set up container networking: driver failed programming external connectivity on endpoint hassio_observer (ea4d0fdaa72cf86f2c9199a04208e3eaf0c5a0d6fd34b3c7f4fab2daadb1f3a9): failed to bind host port 0.0.0.0:4357/tcp: address already in use",
    ],
)
@pytest.mark.usefixtures("container", "tmp_supervisor_data", "path_extern")
async def test_observer_start_port_conflict(
    coresys: CoreSys, caplog: pytest.LogCaptureFixture, docker_message: str
):
    """Test port conflict error when trying to start observer."""
    coresys.docker.containers.create.return_value.start.side_effect = (
        aiodocker.DockerError(HTTPStatus.INTERNAL_SERVER_ERROR, docker_message)
    )
    await coresys.plugins.observer.load()

    caplog.clear()
    with pytest.raises(ObserverPortConflict):
        await coresys.plugins.observer.start()

    assert (
        "Cannot start container hassio_observer because port 4357 is already in use"
        in caplog.text
    )


async def test_stats_not_running(coresys: CoreSys):
    """Test stats raises ObserverNotRunningError when the container isn't running."""
    with (
        patch.object(
            DockerObserver,
            "stats",
            AsyncMock(
                side_effect=DockerContainerNotRunningError(name="hassio_observer")
            ),
        ),
        pytest.raises(ObserverNotRunningError),
    ):
        await coresys.plugins.observer.stats()

    with (
        patch.object(
            DockerObserver,
            "stats",
            AsyncMock(side_effect=DockerContainerNotFoundError(name="hassio_observer")),
        ),
        pytest.raises(ObserverNotRunningError),
    ):
        await coresys.plugins.observer.stats()


async def test_stats_timeout(coresys: CoreSys):
    """Test stats raises ObserverStatsTimeoutError on timeout."""
    with (
        patch.object(
            DockerObserver,
            "stats",
            AsyncMock(side_effect=DockerStatsTimeoutError(name="hassio_observer")),
        ),
        pytest.raises(ObserverStatsTimeoutError),
    ):
        await coresys.plugins.observer.stats()


async def test_stats_unknown_error(coresys: CoreSys):
    """Test stats raises ObserverUnknownError on an unexpected Docker error."""
    with (
        patch.object(
            DockerObserver, "stats", AsyncMock(side_effect=DockerError("boom"))
        ),
        pytest.raises(ObserverUnknownError),
    ):
        await coresys.plugins.observer.stats()
