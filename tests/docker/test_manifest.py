"""Tests for registry manifest fetcher."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from supervisor.docker.manifest import (
    DOCKER_HUB,
    ImageManifest,
    RegistryManifestFetcher,
    parse_image_reference,
)


class TestParseImageReference:
    """Tests for parse_image_reference function."""

    def test_ghcr_io_image(self):
        """Test parsing ghcr.io image."""
        registry, repo, tag = parse_image_reference(
            "ghcr.io/home-assistant/home-assistant", "2025.1.0"
        )
        assert registry == "ghcr.io"
        assert repo == "home-assistant/home-assistant"
        assert tag == "2025.1.0"

    def test_docker_hub_with_org(self):
        """Test parsing Docker Hub image with organization."""
        registry, repo, tag = parse_image_reference(
            "homeassistant/home-assistant", "latest"
        )
        assert registry == DOCKER_HUB
        assert repo == "homeassistant/home-assistant"
        assert tag == "latest"

    def test_docker_hub_official_image(self):
        """Test parsing Docker Hub official image (no org)."""
        registry, repo, tag = parse_image_reference("alpine", "3.18")
        assert registry == DOCKER_HUB
        assert repo == "library/alpine"
        assert tag == "3.18"

    def test_gcr_io_image(self):
        """Test parsing gcr.io image."""
        registry, repo, tag = parse_image_reference("gcr.io/project/image", "v1")
        assert registry == "gcr.io"
        assert repo == "project/image"
        assert tag == "v1"


class TestImageManifest:
    """Tests for ImageManifest dataclass."""

    def test_layer_count(self):
        """Test layer_count property."""
        manifest = ImageManifest(
            digest="sha256:abc",
            total_size=1000,
            layers={"layer1": 500, "layer2": 500},
        )
        assert manifest.layer_count == 2


class TestRegistryManifestFetcher:
    """Tests for RegistryManifestFetcher class."""

    # pylint: disable=protected-access

    @pytest.fixture
    def mock_coresys(self):
        """Create mock coresys."""
        coresys = MagicMock()
        coresys.docker.config.registries = {}
        return coresys

    @pytest.fixture
    def fetcher(self, mock_coresys):
        """Create fetcher instance."""
        return RegistryManifestFetcher(mock_coresys)

    async def test_get_manifest_success(self, fetcher):
        """Test successful manifest fetch by mocking internal methods."""
        manifest_data = {
            "mediaType": "application/vnd.docker.distribution.manifest.v2+json",
            "config": {"digest": "sha256:abc123"},
            "layers": [
                {"digest": "sha256:layer1abc123def456789012", "size": 1000},
                {"digest": "sha256:layer2def456abc789012345", "size": 2000},
            ],
        }

        # Mock the internal methods instead of the session
        with (
            patch.object(
                fetcher, "_get_auth_token", new=AsyncMock(return_value="test-token")
            ),
            patch.object(
                fetcher, "_fetch_manifest", new=AsyncMock(return_value=manifest_data)
            ),
            patch.object(fetcher, "_get_session", new=AsyncMock()),
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

    async def test_get_manifest_returns_none_on_failure(self, fetcher):
        """Test that get_manifest returns None on failure."""
        with (
            patch.object(
                fetcher, "_get_auth_token", new=AsyncMock(return_value="test-token")
            ),
            patch.object(fetcher, "_fetch_manifest", new=AsyncMock(return_value=None)),
            patch.object(fetcher, "_get_session", new=AsyncMock()),
        ):
            result = await fetcher.get_manifest(
                "test.io/org/image", "v1.0", platform="linux/amd64"
            )

            assert result is None

    async def test_close_session(self, fetcher):
        """Test session cleanup."""
        mock_session = AsyncMock()
        mock_session.closed = False
        mock_session.close = AsyncMock()
        fetcher._session = mock_session

        await fetcher.close()

        mock_session.close.assert_called_once()
        assert fetcher._session is None

    def test_get_credentials_docker_hub(self, mock_coresys, fetcher):
        """Test getting Docker Hub credentials."""
        mock_coresys.docker.config.registries = {
            "docker.io": {"username": "user", "password": "pass"}
        }

        creds = fetcher._get_credentials(DOCKER_HUB)

        assert creds == ("user", "pass")

    def test_get_credentials_custom_registry(self, mock_coresys, fetcher):
        """Test getting credentials for custom registry."""
        mock_coresys.docker.config.registries = {
            "ghcr.io": {"username": "user", "password": "token"}
        }

        creds = fetcher._get_credentials("ghcr.io")

        assert creds == ("user", "token")

    def test_get_credentials_not_found(self, mock_coresys, fetcher):
        """Test no credentials found."""
        mock_coresys.docker.config.registries = {}

        creds = fetcher._get_credentials("unknown.io")

        assert creds is None
