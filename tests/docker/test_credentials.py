"""Test docker login."""

# pylint: disable=protected-access
from supervisor.coresys import CoreSys
from supervisor.docker.const import DOCKER_HUB, DOCKER_HUB_LEGACY
from supervisor.docker.interface import DockerInterface


def test_no_credentials(coresys: CoreSys, test_docker_interface: DockerInterface):
    """Test no credentials."""
    coresys.docker.config._data["registries"] = {
        DOCKER_HUB: {"username": "Spongebob Squarepants", "password": "Password1!"}
    }
    credentials, image = test_docker_interface._get_credentials("ghcr.io/homeassistant")
    assert not credentials
    assert image == "ghcr.io/homeassistant"

    credentials, image = test_docker_interface._get_credentials(
        "ghcr.io/homeassistant/amd64-supervisor"
    )
    assert not credentials
    assert image == "ghcr.io/homeassistant/amd64-supervisor"


def test_no_matching_credentials(
    coresys: CoreSys, test_docker_interface: DockerInterface
):
    """Test no matching credentials."""
    coresys.docker.config._data["registries"] = {
        DOCKER_HUB: {"username": "Spongebob Squarepants", "password": "Password1!"}
    }
    credentials, image = test_docker_interface._get_credentials("ghcr.io/homeassistant")
    assert not credentials
    assert image == "ghcr.io/homeassistant"

    credentials, image = test_docker_interface._get_credentials(
        "ghcr.io/homeassistant/amd64-supervisor"
    )
    assert not credentials
    assert image == "ghcr.io/homeassistant/amd64-supervisor"


def test_matching_credentials(coresys: CoreSys, test_docker_interface: DockerInterface):
    """Test matching credentials."""
    coresys.docker.config._data["registries"] = {
        "ghcr.io": {"username": "Octocat", "password": "Password1!"},
        DOCKER_HUB: {"username": "Spongebob Squarepants", "password": "Password1!"},
    }

    credentials, image = test_docker_interface._get_credentials(
        "ghcr.io/homeassistant/amd64-supervisor"
    )
    assert credentials["registry"] == "ghcr.io"
    assert image == "ghcr.io/homeassistant/amd64-supervisor"

    credentials, image = test_docker_interface._get_credentials(
        "homeassistant/amd64-supervisor"
    )
    assert credentials["username"] == "Spongebob Squarepants"
    assert credentials["registry"] == DOCKER_HUB
    # Docker Hub images should be prefixed with docker.io/ for correct ServerAddress
    assert image == f"{DOCKER_HUB}/homeassistant/amd64-supervisor"


def test_legacy_docker_hub_credentials(
    coresys: CoreSys, test_docker_interface: DockerInterface
):
    """Test legacy hub.docker.com credentials are used for Docker Hub images."""
    coresys.docker.config._data["registries"] = {
        DOCKER_HUB_LEGACY: {"username": "LegacyUser", "password": "Password1!"},
    }

    credentials, image = test_docker_interface._get_credentials(
        "homeassistant/amd64-supervisor"
    )
    assert credentials["username"] == "LegacyUser"
    assert credentials["registry"] == DOCKER_HUB_LEGACY
    assert image == f"{DOCKER_HUB}/homeassistant/amd64-supervisor"


def test_explicit_docker_hub_domain_not_doubled(
    coresys: CoreSys, test_docker_interface: DockerInterface
):
    """Test an image already carrying a Docker Hub domain is not prefixed twice."""
    coresys.docker.config._data["registries"] = {
        DOCKER_HUB: {"username": "Spongebob Squarepants", "password": "Password1!"},
    }

    for image in (
        f"{DOCKER_HUB}/homeassistant/amd64-supervisor",
        "index.docker.io/homeassistant/amd64-supervisor",
    ):
        credentials, qualified_image = test_docker_interface._get_credentials(image)
        assert credentials["registry"] == DOCKER_HUB
        assert qualified_image == f"{DOCKER_HUB}/homeassistant/amd64-supervisor"


def test_docker_hub_preferred_over_legacy(
    coresys: CoreSys, test_docker_interface: DockerInterface
):
    """Test docker.io is preferred over legacy hub.docker.com when both exist."""
    coresys.docker.config._data["registries"] = {
        DOCKER_HUB: {"username": "NewUser", "password": "Password1!"},
        DOCKER_HUB_LEGACY: {"username": "LegacyUser", "password": "Password2!"},
    }

    credentials, image = test_docker_interface._get_credentials(
        "homeassistant/amd64-supervisor"
    )
    # docker.io should be preferred
    assert credentials["username"] == "NewUser"
    assert credentials["registry"] == DOCKER_HUB
    assert image == f"{DOCKER_HUB}/homeassistant/amd64-supervisor"
