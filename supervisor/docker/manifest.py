"""Docker registry manifest fetcher.

Fetches image manifests directly from container registries to get layer sizes
before pulling an image. This enables accurate size-based progress tracking.
"""

from __future__ import annotations

from dataclasses import dataclass
import logging
import re
from typing import TYPE_CHECKING

import aiohttp

from supervisor.docker.utils import get_registry_from_image

from .const import DOCKER_HUB, DOCKER_HUB_LEGACY

if TYPE_CHECKING:
    from ..coresys import CoreSys

_LOGGER = logging.getLogger(__name__)

# Media types for manifest requests
MANIFEST_MEDIA_TYPES = (
    "application/vnd.docker.distribution.manifest.v2+json",
    "application/vnd.oci.image.manifest.v1+json",
    "application/vnd.docker.distribution.manifest.list.v2+json",
    "application/vnd.oci.image.index.v1+json",
)


@dataclass
class ImageManifest:
    """Container image manifest with layer information."""

    digest: str
    total_size: int
    layers: dict[str, int]  # digest -> size in bytes

    @property
    def layer_count(self) -> int:
        """Return number of layers."""
        return len(self.layers)


def parse_image_reference(image: str, tag: str) -> tuple[str, str, str]:
    """Parse image reference into (registry, repository, tag).

    Examples:
        ghcr.io/home-assistant/home-assistant:2025.1.0
            -> (ghcr.io, home-assistant/home-assistant, 2025.1.0)
        homeassistant/home-assistant:latest
            -> (registry-1.docker.io, homeassistant/home-assistant, latest)
        alpine:3.18
            -> (registry-1.docker.io, library/alpine, 3.18)

    """
    # Check if image has explicit registry host
    registry = get_registry_from_image(image)
    if registry:
        repository = image[len(registry) + 1 :]  # Remove "registry/" prefix
    else:
        registry = DOCKER_HUB
        repository = image
        # Docker Hub requires "library/" prefix for official images
        if "/" not in repository:
            repository = f"library/{repository}"

    return registry, repository, tag


class RegistryManifestFetcher:
    """Fetches manifests from container registries."""

    def __init__(self, coresys: CoreSys) -> None:
        """Initialize the fetcher."""
        self.coresys = coresys
        self._session: aiohttp.ClientSession | None = None

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session."""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session

    async def close(self) -> None:
        """Close the session."""
        if self._session and not self._session.closed:
            await self._session.close()
            self._session = None

    def _get_credentials(self, registry: str) -> tuple[str, str] | None:
        """Get credentials for registry from Docker config.

        Returns (username, password) tuple or None if no credentials.
        """
        registries = self.coresys.docker.config.registries

        # Map registry hostname to config key
        # Docker Hub can be stored as "hub.docker.com" in config
        if registry in (DOCKER_HUB, DOCKER_HUB_LEGACY):
            if DOCKER_HUB in registries:
                creds = registries[DOCKER_HUB]
                return creds.get("username"), creds.get("password")
        elif registry in registries:
            creds = registries[registry]
            return creds.get("username"), creds.get("password")

        return None

    async def _get_auth_token(
        self,
        session: aiohttp.ClientSession,
        registry: str,
        repository: str,
    ) -> str | None:
        """Get authentication token for registry.

        Uses the WWW-Authenticate header from a 401 response to discover
        the token endpoint, then requests a token with appropriate scope.
        """
        # First, make an unauthenticated request to get WWW-Authenticate header
        manifest_url = f"https://{registry}/v2/{repository}/manifests/latest"

        try:
            async with session.get(manifest_url) as resp:
                if resp.status == 200:
                    # No auth required
                    return None

                if resp.status != 401:
                    _LOGGER.warning(
                        "Unexpected status %d from registry %s", resp.status, registry
                    )
                    return None

                www_auth = resp.headers.get("WWW-Authenticate", "")
        except aiohttp.ClientError as err:
            _LOGGER.warning("Failed to connect to registry %s: %s", registry, err)
            return None

        # Parse WWW-Authenticate: Bearer realm="...",service="...",scope="..."
        if not www_auth.startswith("Bearer "):
            _LOGGER.warning("Unsupported auth type from %s: %s", registry, www_auth)
            return None

        params = {}
        for match in re.finditer(r'(\w+)="([^"]*)"', www_auth):
            params[match.group(1)] = match.group(2)

        realm = params.get("realm")
        service = params.get("service")

        if not realm:
            _LOGGER.warning("No realm in WWW-Authenticate from %s", registry)
            return None

        # Build token request URL
        token_url = f"{realm}?scope=repository:{repository}:pull"
        if service:
            token_url += f"&service={service}"

        # Check for credentials
        auth = None
        credentials = self._get_credentials(registry)
        if credentials:
            username, password = credentials
            if username and password:
                auth = aiohttp.BasicAuth(username, password)
                _LOGGER.debug("Using credentials for %s", registry)

        try:
            async with session.get(token_url, auth=auth) as resp:
                if resp.status != 200:
                    _LOGGER.warning(
                        "Failed to get token from %s: %d", realm, resp.status
                    )
                    return None

                data = await resp.json()
                return data.get("token") or data.get("access_token")
        except aiohttp.ClientError as err:
            _LOGGER.warning("Failed to get auth token: %s", err)
            return None

    async def _fetch_manifest(
        self,
        session: aiohttp.ClientSession,
        registry: str,
        repository: str,
        reference: str,
        token: str | None,
        platform: str | None = None,
    ) -> dict | None:
        """Fetch manifest from registry.

        If the manifest is a manifest list (multi-arch), fetches the
        platform-specific manifest.
        """
        manifest_url = f"https://{registry}/v2/{repository}/manifests/{reference}"

        headers = {"Accept": ", ".join(MANIFEST_MEDIA_TYPES)}
        if token:
            headers["Authorization"] = f"Bearer {token}"

        try:
            async with session.get(manifest_url, headers=headers) as resp:
                if resp.status != 200:
                    _LOGGER.warning(
                        "Failed to fetch manifest for %s/%s:%s - %d",
                        registry,
                        repository,
                        reference,
                        resp.status,
                    )
                    return None

                manifest = await resp.json()
        except aiohttp.ClientError as err:
            _LOGGER.warning("Failed to fetch manifest: %s", err)
            return None

        media_type = manifest.get("mediaType", "")

        # Check if this is a manifest list (multi-arch image)
        if "list" in media_type or "index" in media_type:
            manifests = manifest.get("manifests", [])
            if not manifests:
                _LOGGER.warning("Empty manifest list for %s/%s", registry, repository)
                return None

            # Find matching platform
            target_os = "linux"
            target_arch = "amd64"  # Default

            if platform:
                # Platform format is "linux/amd64", "linux/arm64", etc.
                parts = platform.split("/")
                if len(parts) >= 2:
                    target_os, target_arch = parts[0], parts[1]

            platform_manifest = None
            for m in manifests:
                plat = m.get("platform", {})
                if (
                    plat.get("os") == target_os
                    and plat.get("architecture") == target_arch
                ):
                    platform_manifest = m
                    break

            if not platform_manifest:
                # Fall back to first manifest
                _LOGGER.debug(
                    "Platform %s/%s not found, using first manifest",
                    target_os,
                    target_arch,
                )
                platform_manifest = manifests[0]

            # Fetch the platform-specific manifest
            return await self._fetch_manifest(
                session,
                registry,
                repository,
                platform_manifest["digest"],
                token,
                platform,
            )

        return manifest

    async def get_manifest(
        self,
        image: str,
        tag: str,
        platform: str | None = None,
    ) -> ImageManifest | None:
        """Fetch manifest and extract layer sizes.

        Args:
            image: Image name (e.g., "ghcr.io/home-assistant/home-assistant")
            tag: Image tag (e.g., "2025.1.0")
            platform: Target platform (e.g., "linux/amd64")

        Returns:
            ImageManifest with layer sizes, or None if fetch failed.

        """
        registry, repository, tag = parse_image_reference(image, tag)

        _LOGGER.debug(
            "Fetching manifest for %s/%s:%s (platform=%s)",
            registry,
            repository,
            tag,
            platform,
        )

        session = await self._get_session()

        # Get auth token
        token = await self._get_auth_token(session, registry, repository)

        # Fetch manifest
        manifest = await self._fetch_manifest(
            session, registry, repository, tag, token, platform
        )

        if not manifest:
            return None

        # Extract layer information
        layers = manifest.get("layers", [])
        if not layers:
            _LOGGER.warning(
                "No layers in manifest for %s/%s:%s", registry, repository, tag
            )
            return None

        layer_sizes: dict[str, int] = {}
        total_size = 0

        for layer in layers:
            digest = layer.get("digest", "")
            size = layer.get("size", 0)
            if digest and size:
                # Store by short digest (first 12 chars after sha256:)
                short_digest = (
                    digest.split(":")[1][:12] if ":" in digest else digest[:12]
                )
                layer_sizes[short_digest] = size
                total_size += size

        digest = manifest.get("config", {}).get("digest", "")

        _LOGGER.debug(
            "Manifest for %s/%s:%s - %d layers, %d bytes total",
            registry,
            repository,
            tag,
            len(layer_sizes),
            total_size,
        )

        return ImageManifest(
            digest=digest,
            total_size=total_size,
            layers=layer_sizes,
        )
