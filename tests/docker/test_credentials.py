"""Test docker login."""

import pytest

# pylint: disable=protected-access
from supervisor.coresys import CoreSys
from supervisor.docker.const import DOCKER_HUB, DOCKER_HUB_LEGACY, get_domain
from supervisor.docker.interface import DockerInterface


@pytest.mark.parametrize(
    ("image_ref", "expected_domain"),
    [
        # No domain - Docker Hub images
        ("nginx", None),
        ("nginx:latest", None),
        ("library/nginx", None),
        ("library/nginx:latest", None),
        ("homeassistant/amd64-supervisor", None),
        ("homeassistant/amd64-supervisor:1.2.3", None),
        # Domain with dot
        ("ghcr.io/homeassistant/amd64-supervisor", "ghcr.io"),
        ("ghcr.io/homeassistant/amd64-supervisor:latest", "ghcr.io"),
        ("myregistry.com/nginx", "myregistry.com"),
        ("registry.example.com/org/image:v1", "registry.example.com"),
        ("127.0.0.1/myimage", "127.0.0.1"),
        # Domain with port
        ("myregistry:5000/myimage", "myregistry:5000"),
        ("localhost:5000/myimage", "localhost:5000"),
        ("registry.io:5000/org/app:v1", "registry.io:5000"),
        # localhost special case
        ("localhost/myimage", "localhost"),
        ("localhost/myimage:tag", "localhost"),
        # IPv6
        ("[::1]:5000/myimage", "[::1]:5000"),
        ("[2001:db8::1]:5000/myimage:tag", "[2001:db8::1]:5000"),
    ],
)
def test_get_domain(image_ref: str, expected_domain: str | None):
    """Test get_domain extracts registry domain from image reference.

    Based on Docker's reference implementation:
    vendor/github.com/distribution/reference/normalize.go
    """
    assert get_domain(image_ref) == expected_domain


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


def test_legacy_docker_hub_credentials(
    coresys: CoreSys, test_docker_interface: DockerInterface
):
    """Test legacy hub.docker.com credentials are used for Docker Hub images."""
    coresys.docker.config._data["registries"] = {
        DOCKER_HUB_LEGACY: {"username": "LegacyUser", "password": "Password1!"},
    }

    credentials = test_docker_interface._get_credentials(
        "homeassistant/amd64-supervisor"
    )
    assert credentials["username"] == "LegacyUser"
    # No registry should be included for Docker Hub
    assert "registry" not in credentials


def test_docker_hub_preferred_over_legacy(
    coresys: CoreSys, test_docker_interface: DockerInterface
):
    """Test docker.io is preferred over legacy hub.docker.com when both exist."""
    coresys.docker.config._data["registries"] = {
        DOCKER_HUB: {"username": "NewUser", "password": "Password1!"},
        DOCKER_HUB_LEGACY: {"username": "LegacyUser", "password": "Password2!"},
    }

    credentials = test_docker_interface._get_credentials(
        "homeassistant/amd64-supervisor"
    )
    # docker.io should be preferred
    assert credentials["username"] == "NewUser"
    assert "registry" not in credentials
