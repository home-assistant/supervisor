"""Test docker login."""

# pylint: disable=protected-access
from supervisor.coresys import CoreSys
from supervisor.docker.interface import DOCKER_HUB, DockerInterface


def test_no_credentials(coresys: CoreSys, test_docker_interface: DockerInterface):
    """Test no credentials."""
    coresys.docker.config._data["registries"] = {
        DOCKER_HUB: {"username": "Spongebob Squarepants", "password": "Password1!"}
    }
    assert not test_docker_interface._get_credentials("ghcr.io/homeassistant")
    assert not test_docker_interface._get_credentials(
        "ghcr.io/homeassistant/amd64-supervisor"
    )


def test_no_matching_credentials(
    coresys: CoreSys, test_docker_interface: DockerInterface
):
    """Test no matching credentials."""
    coresys.docker.config._data["registries"] = {
        DOCKER_HUB: {"username": "Spongebob Squarepants", "password": "Password1!"}
    }
    assert not test_docker_interface._get_credentials("ghcr.io/homeassistant")
    assert not test_docker_interface._get_credentials(
        "ghcr.io/homeassistant/amd64-supervisor"
    )


def test_matching_credentials(coresys: CoreSys, test_docker_interface: DockerInterface):
    """Test no matching credentials."""
    coresys.docker.config._data["registries"] = {
        "ghcr.io": {"username": "Octocat", "password": "Password1!"},
        DOCKER_HUB: {"username": "Spongebob Squarepants", "password": "Password1!"},
    }

    credentials = test_docker_interface._get_credentials(
        "ghcr.io/homeassistant/amd64-supervisor"
    )
    assert credentials["registry"] == "ghcr.io"

    credentials = test_docker_interface._get_credentials(
        "homeassistant/amd64-supervisor"
    )
    assert credentials["username"] == "Spongebob Squarepants"
    assert "registry" not in credentials
