"""Docker constants."""
from enum import Enum

from docker.types import Mount

from ..const import MACHINE_ID


class Capabilities(str, Enum):
    """Linux Capabilities."""

    BPF = "BPF"
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


class ContainerState(str, Enum):
    """State of supervisor managed docker container."""

    FAILED = "failed"
    HEALTHY = "healthy"
    RUNNING = "running"
    STOPPED = "stopped"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


class RestartPolicy(str, Enum):
    """Restart policy of container."""

    NO = "no"
    ON_FAILURE = "on-failure"
    UNLESS_STOPPED = "unless-stopped"
    ALWAYS = "always"


class MountType(str, Enum):
    """Mount type."""

    BIND = "bind"
    VOLUME = "volume"
    TMPFS = "tmpfs"
    NPIPE = "npipe"


class PropagationMode(str, Enum):
    """Propagataion mode, only for bind type mounts."""

    PRIVATE = "private"
    SHARED = "shared"
    SLAVE = "slave"
    RPRIVATE = "rprivate"
    RSHARED = "rshared"
    RSLAVE = "rslave"


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
