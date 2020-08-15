"""Common test functions."""
from unittest.mock import MagicMock, PropertyMock, patch
from uuid import uuid4

import pytest

from supervisor.bootstrap import initialize_coresys
from supervisor.docker import DockerAPI

# pylint: disable=redefined-outer-name, protected-access


@pytest.fixture
def docker():
    """Mock DockerAPI."""
    images = [MagicMock(tags=["homeassistant/amd64-hassio-supervisor:latest"])]

    with patch("docker.DockerClient", return_value=MagicMock()), patch(
        "supervisor.docker.DockerAPI.images", return_value=MagicMock()
    ), patch("supervisor.docker.DockerAPI.containers", return_value=MagicMock()), patch(
        "supervisor.docker.DockerAPI.api", return_value=MagicMock()
    ), patch(
        "supervisor.docker.DockerAPI.images.list", return_value=images
    ):
        docker_obj = DockerAPI()

        yield docker_obj


@pytest.fixture
async def coresys(loop, docker):
    """Create a CoreSys Mock."""
    with patch("supervisor.bootstrap.initialize_system_data"), patch(
        "supervisor.bootstrap.setup_diagnostics"
    ), patch(
        "supervisor.bootstrap.fetch_timezone", return_value="Europe/Zurich",
    ):
        coresys_obj = await initialize_coresys()

    coresys_obj.ingress.save_data = MagicMock()
    coresys_obj.arch._default_arch = "amd64"

    coresys_obj._machine = "qemux86-64"
    coresys_obj._machine_id = uuid4()

    yield coresys_obj


@pytest.fixture
def sys_machine():
    """Mock sys_machine."""
    with patch("supervisor.coresys.CoreSys.machine", new_callable=PropertyMock) as mock:
        yield mock


@pytest.fixture
def sys_supervisor():
    """Mock sys_supervisor."""
    with patch(
        "supervisor.coresys.CoreSys.supervisor", new_callable=PropertyMock
    ) as mock:
        mock.return_value = MagicMock()
        yield MagicMock
