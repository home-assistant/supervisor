"""Common test functions."""
from unittest.mock import patch, PropertyMock, MagicMock

import pytest

from hassio.bootstrap import initialize_coresys


@pytest.fixture
def docker():
    """Mock Docker API."""
    with patch('hassio.coresys.DockerAPI') as mock:
        yield mock


@pytest.fixture
async def coresys(loop, docker):
    """Create a CoreSys Mock."""
    coresys = await initialize_coresys(loop)
    yield coresys


@pytest.fixture
def sys_machine():
    """Mock sys_machine."""
    with patch(
            'hassio.coresys.CoreSys.machine',
            new_callable=PropertyMock) as mock:
        yield mock


@pytest.fixture
def sys_supervisor():
    with patch(
            'hassio.coresys.CoreSys.supervisor',
            new_callable=PropertyMock) as mock:
        mock.return_value = MagicMock()
        yield MagicMock
