"""Test Docker utilities."""

import pytest

from supervisor.docker.const import DOCKER_HUB
from supervisor.docker.utils import (
    get_registry_from_image,
    is_registry_domain,
    split_docker_domain,
    split_image_tag,
)


@pytest.mark.parametrize(
    ("image_ref", "expected"),
    [
        # No registry, hosted on Docker Hub
        ("nginx", (None, "nginx")),
        ("nginx:latest", (None, "nginx:latest")),
        ("library/nginx", (None, "library/nginx")),
        ("homeassistant/amd64-supervisor", (None, "homeassistant/amd64-supervisor")),
        # Registry with a dot
        (
            "ghcr.io/home-assistant/amd64-supervisor",
            ("ghcr.io", "home-assistant/amd64-supervisor"),
        ),
        ("registry.example.com/org/image:v1", ("registry.example.com", "org/image:v1")),
        ("127.0.0.1/myimage", ("127.0.0.1", "myimage")),
        # Registry with a port
        ("myregistry:5000/myimage", ("myregistry:5000", "myimage")),
        ("registry.io:5000/org/app:v1", ("registry.io:5000", "org/app:v1")),
        # localhost is a reserved namespace and always a registry
        ("localhost/myimage", ("localhost", "myimage")),
        ("localhost:5000/myimage:tag", ("localhost:5000", "myimage:tag")),
        # IPv6 registry
        ("[::1]:5000/myimage", ("[::1]:5000", "myimage")),
        ("[2001:db8::1]:5000/myimage:tag", ("[2001:db8::1]:5000", "myimage:tag")),
        # Legacy Docker Hub domain gets canonicalized
        ("index.docker.io/library/nginx", (DOCKER_HUB, "library/nginx")),
        # Uppercase is not allowed in a path component, so it is a registry
        ("Foo/bar", ("Foo", "bar")),
    ],
)
def test_split_docker_domain(image_ref: str, expected: tuple[str | None, str]):
    """Test splitting an image reference into registry domain and remainder."""
    assert split_docker_domain(image_ref) == expected


def test_get_registry_from_image():
    """Test get_registry_from_image returns only the registry domain."""
    assert get_registry_from_image("ghcr.io/home-assistant/supervisor") == "ghcr.io"
    assert get_registry_from_image("homeassistant/supervisor") is None
    assert get_registry_from_image("index.docker.io/library/nginx") == DOCKER_HUB


@pytest.mark.parametrize(
    ("domain", "valid"),
    [
        ("ghcr.io", True),
        ("registry.example.com", True),
        ("myregistry:5000", True),
        ("localhost", True),
        ("localhost:5000", True),
        ("127.0.0.1", True),
        ("[::1]:5000", True),
        ("[2001:db8::1]", True),
        # Malformed domains
        (".ghcr.io", False),
        ("ghcr.io.", False),
        ("-bad-.com", False),
        ("bad-.com", False),
        ("....", False),
        ("ghcr.io:", False),
        ("ghcr.io:port", False),
        ("ghcr.io/org", False),
    ],
)
def test_is_registry_domain(domain: str, valid: bool):
    """Test validation of registry domains."""
    assert is_registry_domain(domain) is valid


@pytest.mark.parametrize(
    ("image_ref", "expected"),
    [
        # No tag
        ("nginx", ("nginx", None)),
        ("library/nginx", ("library/nginx", None)),
        (
            "ghcr.io/home-assistant/amd64-supervisor",
            ("ghcr.io/home-assistant/amd64-supervisor", None),
        ),
        # With tag
        ("nginx:latest", ("nginx", "latest")),
        (
            "homeassistant/amd64-supervisor:1.2.3",
            ("homeassistant/amd64-supervisor", "1.2.3"),
        ),
        # Registry with a port, the port must stay part of the image name
        ("myregistry:5000/myimage", ("myregistry:5000/myimage", None)),
        ("registry.io:5000/org/app:v1", ("registry.io:5000/org/app", "v1")),
        (
            "gitlab.example.com:5005/org/app/aarch64:0.3.3-dev1",
            ("gitlab.example.com:5005/org/app/aarch64", "0.3.3-dev1"),
        ),
        # localhost with a port
        ("localhost:5000/myimage", ("localhost:5000/myimage", None)),
        ("localhost:5000/myimage:tag", ("localhost:5000/myimage", "tag")),
        # IPv6 registry
        ("[::1]:5000/myimage", ("[::1]:5000/myimage", None)),
        ("[2001:db8::1]:5000/myimage:tag", ("[2001:db8::1]:5000/myimage", "tag")),
        # Digests are stripped along with the tag
        ("nginx@sha256:1234abcd", ("nginx", None)),
        ("ghcr.io/org/app@sha256:1234abcd", ("ghcr.io/org/app", None)),
        # A bare digest keeps its algorithm prefix as the name
        ("sha256:1234abcd", ("sha256", "1234abcd")),
    ],
)
def test_split_image_tag(image_ref: str, expected: tuple[str, str | None]):
    """Test splitting an image reference into image name and tag."""
    assert split_image_tag(image_ref) == expected
