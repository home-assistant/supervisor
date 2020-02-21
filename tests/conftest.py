"""Common test functions."""
from unittest.mock import patch, PropertyMock, MagicMock

import pytest

from supervisor.bootstrap import initialize_coresys

from tests.common import mock_coro

# pylint: disable=redefined-outer-name


@pytest.fixture
def docker():
    """Mock Docker API."""
    with patch("supervisor.coresys.DockerAPI") as mock:
        yield mock


@pytest.fixture
async def coresys(loop, docker):
    """Create a CoreSys Mock."""
    with patch("supervisor.bootstrap.initialize_system_data"), patch(
        "supervisor.bootstrap.fetch_timezone",
        return_value=mock_coro(return_value="Europe/Zurich"),
    ):
        coresys_obj = await initialize_coresys()

    coresys_obj.ingress.save_data = MagicMock()

    yield coresys_obj


@pytest.fixture
def sys_machine():
    """Mock sys_machine."""
    with patch("supervisor.coresys.CoreSys.machine", new_callable=PropertyMock) as mock:
        yield mock


@pytest.fixture
def sys_supervisor():
    with patch(
        "supervisor.coresys.CoreSys.supervisor", new_callable=PropertyMock
    ) as mock:
        mock.return_value = MagicMock()
        yield MagicMock
