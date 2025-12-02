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
# Note: Docker also treats uppercase letters as domain indicators since
# namespaces must be lowercase, but this regex handles lowercase matching
# and the get_domain_from_image() function validates the domain rules.
IMAGE_DOMAIN_REGEX = re.compile(
    r"^(?P<domain>"
    r"localhost(?::[0-9]+)?|"  # localhost with optional port
    r"(?:[a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9-]*[a-zA-Z0-9])"  # domain component
    r"(?:\.(?:[a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9-]*[a-zA-Z0-9]))*"  # more components
    r"(?::[0-9]+)?|"  # optional port
    r"\[[a-fA-F0-9:]+\](?::[0-9]+)?"  # IPv6 with optional port
    r")/"  # must be followed by /
)


def get_domain_from_image(image_ref: str) -> str | None:
    """Extract domain from Docker image reference.

    Returns the registry domain if the image reference contains one,
    or None if the image uses Docker Hub (docker.io).

    Based on Docker's reference implementation:
    vendor/github.com/distribution/reference/normalize.go

    Examples:
        get_domain_from_image("nginx")                        -> None (docker.io)
        get_domain_from_image("library/nginx")                -> None (docker.io)
        get_domain_from_image("myregistry.com/nginx")         -> "myregistry.com"
        get_domain_from_image("localhost/myimage")            -> "localhost"
        get_domain_from_image("localhost:5000/myimage")       -> "localhost:5000"
        get_domain_from_image("registry.io:5000/org/app:v1")  -> "registry.io:5000"
        get_domain_from_image("[::1]:5000/myimage")           -> "[::1]:5000"

    """
    match = IMAGE_DOMAIN_REGEX.match(image_ref)
    if match:
        domain = match.group("domain")
        # Must contain '.' or ':' or be 'localhost' to be a real domain
        # This prevents treating "myuser/myimage" as having domain "myuser"
        if "." in domain or ":" in domain or domain == "localhost":
            return domain
    return None  # No domain = Docker Hub (docker.io)
