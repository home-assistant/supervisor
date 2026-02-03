"""Docker constants."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from pathlib import PurePath
import re
from typing import Any

from ..const import MACHINE_ID

RE_RETRYING_DOWNLOAD_STATUS = re.compile(r"Retrying in \d+ seconds?")

# Docker Hub registry identifier (official default)
# Docker's default registry is docker.io
DOCKER_HUB = "docker.io"

# Docker Hub API endpoint (used for direct registry API calls)
# While docker.io is the registry identifier, registry-1.docker.io is the actual API endpoint
DOCKER_HUB_API = "registry-1.docker.io"

# Legacy Docker Hub identifier for backward compatibility
DOCKER_HUB_LEGACY = "hub.docker.com"


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


@dataclass(slots=True, frozen=True)
class MountBindOptions:
    """Bind options for docker mount."""

    propagation: PropagationMode | None = None
    read_only_non_recursive: bool | None = None

    def to_dict(self) -> dict[str, Any]:
        """To dictionary representation."""
        out: dict[str, Any] = {}
        if self.propagation:
            out["Propagation"] = self.propagation.value
        if self.read_only_non_recursive is not None:
            out["ReadOnlyNonRecursive"] = self.read_only_non_recursive
        return out


@dataclass(slots=True, frozen=True)
class DockerMount:
    """A docker mount."""

    type: MountType
    source: str
    target: str
    read_only: bool
    bind_options: MountBindOptions | None = None

    def to_dict(self) -> dict[str, Any]:
        """To dictionary representation."""
        out: dict[str, Any] = {
            "Type": self.type.value,
            "Source": self.source,
            "Target": self.target,
            "ReadOnly": self.read_only,
        }
        if self.bind_options:
            out["BindOptions"] = self.bind_options.to_dict()
        return out


@dataclass(slots=True, frozen=True)
class Ulimit:
    """A linux user limit."""

    name: str
    soft: int
    hard: int

    def to_dict(self) -> dict[str, str | int]:
        """To dictionary representation."""
        return {
            "Name": self.name,
            "Soft": self.soft,
            "Hard": self.hard,
        }


ENV_DUPLICATE_LOG_FILE = "HA_DUPLICATE_LOG_FILE"
ENV_TIME = "TZ"
ENV_TOKEN = "SUPERVISOR_TOKEN"
ENV_TOKEN_OLD = "HASSIO_TOKEN"

LABEL_MANAGED = "supervisor_managed"

MOUNT_DBUS = DockerMount(
    type=MountType.BIND, source="/run/dbus", target="/run/dbus", read_only=True
)
MOUNT_DEV = DockerMount(
    type=MountType.BIND,
    source="/dev",
    target="/dev",
    read_only=True,
    bind_options=MountBindOptions(read_only_non_recursive=True),
)
MOUNT_DOCKER = DockerMount(
    type=MountType.BIND,
    source="/run/docker.sock",
    target="/run/docker.sock",
    read_only=True,
)
MOUNT_MACHINE_ID = DockerMount(
    type=MountType.BIND,
    source=MACHINE_ID.as_posix(),
    target=MACHINE_ID.as_posix(),
    read_only=True,
)
MOUNT_UDEV = DockerMount(
    type=MountType.BIND, source="/run/udev", target="/run/udev", read_only=True
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
