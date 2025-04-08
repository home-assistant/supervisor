"""Fixtures for docker tests."""

import pytest

from supervisor.coresys import CoreSys
from supervisor.docker.interface import DockerInterface


class TestDockerInterface(DockerInterface):
    """Test docker interface."""

    @property
    def name(self) -> str:
        """Name of test interface."""
        return "test_interface"


@pytest.fixture
def test_docker_interface(coresys: CoreSys) -> TestDockerInterface:
    """Return test docker interface."""
    return TestDockerInterface(coresys)
