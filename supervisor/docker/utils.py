"""Docker utilities."""

from __future__ import annotations

import re

# Docker image reference domain regex
# Based on Docker's reference implementation:
# vendor/github.com/distribution/reference/normalize.go
#
# A domain is detected if the part before the first / contains:
# - "localhost" (with optional port)
# - Contains "." (like registry.example.com or 127.0.0.1)
# - Contains ":" (like myregistry:5000)
# - IPv6 addresses in brackets (like [::1]:5000)
#
# Note: Docker also treats uppercase letters as registry indicators since
# namespaces must be lowercase, but this regex handles lowercase matching
# and the get_registry_from_image() function validates the registry rules.
IMAGE_REGISTRY_REGEX = re.compile(
    r"^(?P<registry>"
    r"localhost(?::[0-9]+)?|"  # localhost with optional port
    r"(?:[a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9-]*[a-zA-Z0-9])"  # domain component
    r"(?:\.(?:[a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9-]*[a-zA-Z0-9]))*"  # more components
    r"(?::[0-9]+)?|"  # optional port
    r"\[[a-fA-F0-9:]+\](?::[0-9]+)?"  # IPv6 with optional port
    r")/"  # must be followed by /
)


def get_registry_from_image(image_ref: str) -> str | None:
    """Extract registry from Docker image reference.

    Returns the registry if the image reference contains one,
    or None if the image uses Docker Hub (docker.io).

    Based on Docker's reference implementation:
    vendor/github.com/distribution/reference/normalize.go

    Examples:
        get_registry_from_image("nginx")                        -> None (docker.io)
        get_registry_from_image("library/nginx")                -> None (docker.io)
        get_registry_from_image("myregistry.com/nginx")         -> "myregistry.com"
        get_registry_from_image("localhost/myimage")            -> "localhost"
        get_registry_from_image("localhost:5000/myimage")       -> "localhost:5000"
        get_registry_from_image("registry.io:5000/org/app:v1")  -> "registry.io:5000"
        get_registry_from_image("[::1]:5000/myimage")           -> "[::1]:5000"

    """
    match = IMAGE_REGISTRY_REGEX.match(image_ref)
    if match:
        registry = match.group("registry")
        # Must contain '.' or ':' or be 'localhost' to be a real registry
        # This prevents treating "myuser/myimage" as having registry "myuser"
        if "." in registry or ":" in registry or registry == "localhost":
            return registry
    return None  # No registry = Docker Hub (docker.io)
