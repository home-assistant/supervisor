"""Fixtures for docker tests."""

import pytest

from supervisor.coresys import CoreSys
from supervisor.docker.interface import DockerInterface


class FakeDockerInterface(DockerInterface):
    """Fake docker interface for tests."""

    @property
    def name(self) -> str:
        """Name of test interface."""
        return "test_interface"


@pytest.fixture
def test_docker_interface(coresys: CoreSys) -> FakeDockerInterface:
    """Return test docker interface."""
    return FakeDockerInterface(coresys)
