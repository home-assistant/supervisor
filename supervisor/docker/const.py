"""Docker constants."""

from __future__ import annotations

from contextlib import suppress
from enum import Enum, StrEnum
from functools import total_ordering
from pathlib import PurePath
import re
from typing import cast

from docker.types import Mount

from ..const import MACHINE_ID

RE_RETRYING_DOWNLOAD_STATUS = re.compile(r"Retrying in \d+ seconds?")

# Docker Hub registry identifier (official default)
# Docker's default registry is docker.io
DOCKER_HUB = "docker.io"

# Legacy Docker Hub identifier for backward compatibility
DOCKER_HUB_LEGACY = "hub.docker.com"

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
# and the get_domain() function validates the domain rules.
IMAGE_DOMAIN_REGEX = re.compile(
    r"^("
    r"localhost(?::[0-9]+)?|"  # localhost with optional port
    r"(?:[a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9-]*[a-zA-Z0-9])"  # domain component
    r"(?:\.(?:[a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9-]*[a-zA-Z0-9]))*"  # more components
    r"(?::[0-9]+)?|"  # optional port
    r"\[[a-fA-F0-9:]+\](?::[0-9]+)?"  # IPv6 with optional port
    r")/"  # must be followed by /
)


def get_domain(image_ref: str) -> str | None:
    """Extract domain from Docker image reference.

    Returns the registry domain if the image reference contains one,
    or None if the image uses Docker Hub (docker.io).

    Based on Docker's reference implementation:
    vendor/github.com/distribution/reference/normalize.go

    Examples:
        get_domain("nginx")                        -> None (docker.io)
        get_domain("library/nginx")                -> None (docker.io)
        get_domain("myregistry.com/nginx")         -> "myregistry.com"
        get_domain("localhost/myimage")            -> "localhost"
        get_domain("localhost:5000/myimage")       -> "localhost:5000"
        get_domain("registry.io:5000/org/app:v1")  -> "registry.io:5000"
        get_domain("[::1]:5000/myimage")           -> "[::1]:5000"

    """
    match = IMAGE_DOMAIN_REGEX.match(image_ref)
    if match:
        domain = match.group(1)
        # Must contain '.' or ':' or be 'localhost' to be a real domain
        # This prevents treating "myuser/myimage" as having domain "myuser"
        if "." in domain or ":" in domain or domain == "localhost":
            return domain
    return None  # No domain = Docker Hub (docker.io)


class Capabilities(StrEnum):
    """Linux Capabilities."""

    BPF = "BPF"
    CHECKPOINT_RESTORE = "CHECKPOINT_RESTORE"
    DAC_READ_SEARCH = "DAC_READ_SEARCH"
    IPC_LOCK = "IPC_LOCK"
    NET_ADMIN = "NET_ADMIN"
    NET_RAW = "NET_RAW"
    PERFMON = "PERFMON"
    SYS_ADMIN = "SYS_ADMIN"
    SYS_MODULE = "SYS_MODULE"
    SYS_NICE = "SYS_NICE"
    SYS_PTRACE = "SYS_PTRACE"
    SYS_RAWIO = "SYS_RAWIO"
    SYS_RESOURCE = "SYS_RESOURCE"
    SYS_TIME = "SYS_TIME"


class ContainerState(StrEnum):
    """State of supervisor managed docker container."""

    FAILED = "failed"
    HEALTHY = "healthy"
    RUNNING = "running"
    STOPPED = "stopped"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


class RestartPolicy(StrEnum):
    """Restart policy of container."""

    NO = "no"
    ON_FAILURE = "on-failure"
    UNLESS_STOPPED = "unless-stopped"
    ALWAYS = "always"


class MountType(StrEnum):
    """Mount type."""

    BIND = "bind"
    VOLUME = "volume"
    TMPFS = "tmpfs"
    NPIPE = "npipe"


class PropagationMode(StrEnum):
    """Propagataion mode, only for bind type mounts."""

    PRIVATE = "private"
    SHARED = "shared"
    SLAVE = "slave"
    RPRIVATE = "rprivate"
    RSHARED = "rshared"
    RSLAVE = "rslave"


@total_ordering
class PullImageLayerStage(Enum):
    """Job stages for pulling an image layer.

    These are a subset of the statuses in a docker pull image log. They
    are the standardized ones that are the most useful to us.
    """

    PULLING_FS_LAYER = 1, "Pulling fs layer"
    RETRYING_DOWNLOAD = 2, "Retrying download"
    DOWNLOADING = 2, "Downloading"
    VERIFYING_CHECKSUM = 3, "Verifying Checksum"
    DOWNLOAD_COMPLETE = 4, "Download complete"
    EXTRACTING = 5, "Extracting"
    PULL_COMPLETE = 6, "Pull complete"

    def __init__(self, order: int, status: str) -> None:
        """Set fields from values."""
        self.order = order
        self.status = status

    def __eq__(self, value: object, /) -> bool:
        """Check equality, allow StrEnum style comparisons on status."""
        with suppress(AttributeError):
            return self.status == cast(PullImageLayerStage, value).status
        return self.status == value

    def __lt__(self, other: object) -> bool:
        """Order instances."""
        with suppress(AttributeError):
            return self.order < cast(PullImageLayerStage, other).order
        return False

    def __hash__(self) -> int:
        """Hash instance."""
        return hash(self.status)

    @classmethod
    def from_status(cls, status: str) -> PullImageLayerStage | None:
        """Return stage instance from pull log status."""
        for i in cls:
            if i.status == status:
                return i

        # This one includes number of seconds until download so its not constant
        if RE_RETRYING_DOWNLOAD_STATUS.match(status):
            return cls.RETRYING_DOWNLOAD

        return None


ENV_TIME = "TZ"
ENV_TOKEN = "SUPERVISOR_TOKEN"
ENV_TOKEN_OLD = "HASSIO_TOKEN"

LABEL_MANAGED = "supervisor_managed"

MOUNT_DBUS = Mount(
    type=MountType.BIND.value, source="/run/dbus", target="/run/dbus", read_only=True
)
MOUNT_DEV = Mount(
    type=MountType.BIND.value, source="/dev", target="/dev", read_only=True
)
MOUNT_DEV.setdefault("BindOptions", {})["ReadOnlyNonRecursive"] = True
MOUNT_DOCKER = Mount(
    type=MountType.BIND.value,
    source="/run/docker.sock",
    target="/run/docker.sock",
    read_only=True,
)
MOUNT_MACHINE_ID = Mount(
    type=MountType.BIND.value,
    source=MACHINE_ID.as_posix(),
    target=MACHINE_ID.as_posix(),
    read_only=True,
)
MOUNT_UDEV = Mount(
    type=MountType.BIND.value, source="/run/udev", target="/run/udev", read_only=True
)

PATH_PRIVATE_DATA = PurePath("/data")
PATH_HOMEASSISTANT_CONFIG_LEGACY = PurePath("/config")
PATH_HOMEASSISTANT_CONFIG = PurePath("/homeassistant")
PATH_PUBLIC_CONFIG = PurePath("/config")
PATH_ALL_ADDON_CONFIGS = PurePath("/addon_configs")
PATH_SSL = PurePath("/ssl")
PATH_LOCAL_ADDONS = PurePath("/addons")
PATH_BACKUP = PurePath("/backup")
PATH_SHARE = PurePath("/share")
PATH_MEDIA = PurePath("/media")

# https://hub.docker.com/_/docker
ADDON_BUILDER_IMAGE = "docker.io/library/docker"
