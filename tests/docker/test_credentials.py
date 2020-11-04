"""Test docker login."""
# pylint: disable=protected-access
from supervisor.coresys import CoreSys
from supervisor.docker.interface import DOCKER_HUB, DOCKER_HUB_REGISTRY, DockerInterface


def test_no_credentials(coresys: CoreSys):
    """Test no credentials."""
    docker = DockerInterface(coresys)
    coresys.docker.config.registries = {
        DOCKER_HUB: {"username": "Spongebob Squarepants", "password": "Password1!"}
    }
    assert not docker._get_credentials("ghcr.io/homeassistant")
    assert not docker._get_credentials("ghcr.io/homeassistant/amd64-supervisor")


def test_no_matching_credentials(coresys: CoreSys):
    """Test no matching credentials."""
    docker = DockerInterface(coresys)
    coresys.docker.config.registries = {
        DOCKER_HUB: {"username": "Spongebob Squarepants", "password": "Password1!"}
    }
    assert not docker._get_credentials("ghcr.io/homeassistant")
    assert not docker._get_credentials("ghcr.io/homeassistant/amd64-supervisor")


def test_matching_credentials(coresys: CoreSys):
    """Test no matching credentials."""
    docker = DockerInterface(coresys)
    coresys.docker.config.registries = {
        "ghcr.io": {"username": "Octocat", "password": "Password1!"},
        DOCKER_HUB: {"username": "Spongebob Squarepants", "password": "Password1!"},
    }

    credentials = docker._get_credentials("ghcr.io/homeassistant")
    assert credentials["registry"] == "ghcr.io"

    credentials = docker._get_credentials("homeassistant/amd64-supervisor")
    assert credentials["registry"] == DOCKER_HUB_REGISTRY
