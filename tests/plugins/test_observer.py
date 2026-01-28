"""Test observer plugin."""

from http import HTTPStatus

import aiodocker
import pytest

from supervisor.coresys import CoreSys
from supervisor.exceptions import ObserverPortConflict


@pytest.mark.usefixtures("container", "tmp_supervisor_data", "path_extern")
async def test_observer_start_port_conflict(
    coresys: CoreSys, caplog: pytest.LogCaptureFixture
):
    """Test port conflict error when trying to start observer."""
    coresys.docker.containers.create.return_value.start.side_effect = aiodocker.DockerError(
        HTTPStatus.INTERNAL_SERVER_ERROR,
        {
            "message": "failed to set up container networking: driver failed programming external connectivity on endpoint hassio_observer (ea4d0fdaa72cf86f2c9199a04208e3eaf0c5a0d6fd34b3c7f4fab2daadb1f3a9): failed to bind host port for 0.0.0.0:4357:172.30.33.4:80/tcp: address already in use"
        },
    )
    await coresys.plugins.observer.load()

    caplog.clear()
    with pytest.raises(ObserverPortConflict):
        await coresys.plugins.observer.start()

    assert (
        "Cannot start container hassio_observer because port 4357 is already in use"
        in caplog.text
    )
