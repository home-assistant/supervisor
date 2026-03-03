"""Tests for registry manifest fetcher."""

from unittest.mock import AsyncMock, MagicMock, patch

from supervisor.coresys import CoreSys
from supervisor.docker.manifest import (
    DOCKER_HUB,
    DOCKER_HUB_API,
    ImageManifest,
    RegistryManifestFetcher,
    parse_image_reference,
)


def test_parse_image_reference_ghcr_io():
    """Test parsing ghcr.io image."""
    registry, repo, tag = parse_image_reference(
        "ghcr.io/home-assistant/home-assistant", "2025.1.0"
    )
    assert registry == "ghcr.io"
    assert repo == "home-assistant/home-assistant"
    assert tag == "2025.1.0"


def test_parse_image_reference_docker_hub_with_org():
    """Test parsing Docker Hub image with organization."""
    registry, repo, tag = parse_image_reference(
        "homeassistant/home-assistant", "latest"
    )
    assert registry == DOCKER_HUB
    assert repo == "homeassistant/home-assistant"
    assert tag == "latest"


def test_parse_image_reference_docker_hub_official_image():
    """Test parsing Docker Hub official image (no org)."""
    registry, repo, tag = parse_image_reference("alpine", "3.18")
    assert registry == DOCKER_HUB
    assert repo == "library/alpine"
    assert tag == "3.18"


def test_parse_image_reference_gcr_io():
    """Test parsing gcr.io image."""
    registry, repo, tag = parse_image_reference("gcr.io/project/image", "v1")
    assert registry == "gcr.io"
    assert repo == "project/image"
    assert tag == "v1"


def test_image_manifest_layer_count():
    """Test ImageManifest layer_count property."""
    manifest = ImageManifest(
        digest="sha256:abc",
        total_size=1000,
        layers={"layer1": 500, "layer2": 500},
    )
    assert manifest.layer_count == 2


async def test_get_manifest_success(coresys: CoreSys, websession: MagicMock):
    """Test successful manifest fetch by mocking internal methods."""
    fetcher = RegistryManifestFetcher(coresys)
    manifest_data = {
        "mediaType": "application/vnd.docker.distribution.manifest.v2+json",
        "config": {"digest": "sha256:abc123"},
        "layers": [
            {"digest": "sha256:layer1abc123def456789012", "size": 1000},
            {"digest": "sha256:layer2def456abc789012345", "size": 2000},
        ],
    }

    # Mock the internal methods
    with (
        patch.object(
            fetcher, "_get_auth_token", new=AsyncMock(return_value="test-token")
        ),
        patch.object(
            fetcher, "_fetch_manifest", new=AsyncMock(return_value=manifest_data)
        ),
    ):
        result = await fetcher.get_manifest(
            "test.io/org/image", "v1.0", platform="linux/amd64"
        )

        assert result is not None
        assert result.total_size == 3000
        assert result.layer_count == 2
        # First 12 chars after sha256:
        assert "layer1abc123" in result.layers
        assert result.layers["layer1abc123"] == 1000


async def test_get_manifest_returns_none_on_failure(
    coresys: CoreSys, websession: MagicMock
):
    """Test that get_manifest returns None on failure."""
    fetcher = RegistryManifestFetcher(coresys)

    with (
        patch.object(
            fetcher, "_get_auth_token", new=AsyncMock(return_value="test-token")
        ),
        patch.object(fetcher, "_fetch_manifest", new=AsyncMock(return_value=None)),
    ):
        result = await fetcher.get_manifest(
            "test.io/org/image", "v1.0", platform="linux/amd64"
        )

        assert result is None


def test_get_credentials_docker_hub(coresys: CoreSys, websession: MagicMock):
    """Test getting Docker Hub credentials."""
    coresys.docker.config._data["registries"] = {  # pylint: disable=protected-access
        "docker.io": {"username": "user", "password": "pass"}
    }
    fetcher = RegistryManifestFetcher(coresys)

    creds = fetcher._get_credentials(DOCKER_HUB)  # pylint: disable=protected-access

    assert creds == ("user", "pass")


def test_get_credentials_custom_registry(coresys: CoreSys, websession: MagicMock):
    """Test getting credentials for custom registry."""
    coresys.docker.config._data["registries"] = {  # pylint: disable=protected-access
        "ghcr.io": {"username": "user", "password": "token"}
    }
    fetcher = RegistryManifestFetcher(coresys)

    creds = fetcher._get_credentials("ghcr.io")  # pylint: disable=protected-access

    assert creds == ("user", "token")


def test_get_credentials_not_found(coresys: CoreSys, websession: MagicMock):
    """Test no credentials found."""
    coresys.docker.config._data["registries"] = {}  # pylint: disable=protected-access
    fetcher = RegistryManifestFetcher(coresys)

    creds = fetcher._get_credentials("unknown.io")  # pylint: disable=protected-access

    assert creds is None


def test_get_api_endpoint_docker_hub(coresys: CoreSys, websession: MagicMock):
    """Test Docker Hub registry translates to API endpoint."""
    fetcher = RegistryManifestFetcher(coresys)

    endpoint = fetcher._get_api_endpoint(DOCKER_HUB)  # pylint: disable=protected-access

    assert endpoint == DOCKER_HUB_API


def test_get_api_endpoint_other_registry(coresys: CoreSys, websession: MagicMock):
    """Test other registries pass through unchanged."""
    fetcher = RegistryManifestFetcher(coresys)

    endpoint = fetcher._get_api_endpoint("ghcr.io")  # pylint: disable=protected-access

    assert endpoint == "ghcr.io"
