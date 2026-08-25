"""Docker utilities."""

from __future__ import annotations

import re

from .const import DOCKER_HUB

# Docker's legacy default registry domain, canonicalized to DOCKER_HUB
LEGACY_DEFAULT_DOMAIN = "index.docker.io"
# Reserved namespace which is always treated as a registry domain
LOCALHOST_DOMAIN = "localhost"

# Registry domain of an image reference, covering domain names, IPv6 addresses
# and an optional port.
#
# Port of DomainRegexp from Docker's reference implementation:
# https://github.com/distribution/reference/blob/main/regexp.go
_DOMAIN_NAME_COMPONENT = r"(?:[a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9-]*[a-zA-Z0-9])"
_IPV6_ADDRESS = r"\[(?:[a-fA-F0-9:]+)\]"
IMAGE_DOMAIN_REGEX = re.compile(
    rf"(?:{_DOMAIN_NAME_COMPONENT}(?:\.{_DOMAIN_NAME_COMPONENT})*|{_IPV6_ADDRESS})"
    r"(?::[0-9]+)?"
)


def split_docker_domain(image_ref: str) -> tuple[str | None, str]:
    """Split a Docker image reference into registry domain and remainder.

    Returns None as the domain for images without an explicit registry, which
    are hosted on Docker Hub. The domain is not validated, use
    is_registry_domain() for that.

    Port of splitDockerDomain() from Docker's reference implementation:
    https://github.com/distribution/reference/blob/main/normalize.go

    Examples:
        split_docker_domain("nginx")               -> (None, "nginx")
        split_docker_domain("library/nginx")       -> (None, "library/nginx")
        split_docker_domain("ghcr.io/org/app:v1")  -> ("ghcr.io", "org/app:v1")
        split_docker_domain("localhost/myimage")   -> ("localhost", "myimage")
        split_docker_domain("myregistry:5000/app") -> ("myregistry:5000", "app")
        split_docker_domain("[::1]:5000/myimage")  -> ("[::1]:5000", "myimage")
        split_docker_domain("index.docker.io/a/b") -> ("docker.io", "a/b")

    """
    maybe_domain, separator, maybe_remainder = image_ref.partition("/")
    if not separator:
        # Single element like "nginx" is never a domain
        return None, image_ref

    if maybe_domain == LEGACY_DEFAULT_DOMAIN:
        # Canonicalize the legacy Docker Hub domain
        return DOCKER_HUB, maybe_remainder

    if (
        # localhost is a reserved namespace and always considered a domain
        maybe_domain == LOCALHOST_DOMAIN
        # A dot or colon means a domain, covering ports, IPv4 and IPv6 as well
        or "." in maybe_domain
        or ":" in maybe_domain
        # Uppercase is not allowed in a path component, so it must be a domain
        or maybe_domain.lower() != maybe_domain
    ):
        return maybe_domain, maybe_remainder

    return None, image_ref


def is_registry_domain(domain: str) -> bool:
    """Return True if the domain is a well-formed registry domain."""
    return IMAGE_DOMAIN_REGEX.fullmatch(domain) is not None


def get_registry_from_image(image_ref: str) -> str | None:
    """Return the registry of a Docker image reference.

    Returns None if the image reference has no registry, meaning it is hosted
    on Docker Hub.
    """
    return split_docker_domain(image_ref)[0]


def split_image_tag(image_ref: str) -> tuple[str, str | None]:
    """Split a Docker image reference into image name and tag.

    A colon only separates the tag if no slash follows it, which keeps the port
    of a registry (e.g. "myregistry:5000/nginx") part of the image name. This
    mirrors Docker's TagRegexp, which does not allow a slash in a tag. Any
    digest is stripped along with the tag.

    Examples:
        split_image_tag("nginx")                   -> ("nginx", None)
        split_image_tag("nginx:latest")            -> ("nginx", "latest")
        split_image_tag("myregistry:5000/nginx")   -> ("myregistry:5000/nginx", None)
        split_image_tag("registry.io:5000/app:v1") -> ("registry.io:5000/app", "v1")
        split_image_tag("[::1]:5000/myimage")      -> ("[::1]:5000/myimage", None)
        split_image_tag("nginx@sha256:1234")       -> ("nginx", None)

    """
    image_ref = image_ref.partition("@")[0]
    name, separator, tag = image_ref.rpartition(":")
    if not separator or "/" in tag:
        return image_ref, None
    return name, tag
