"""Constants for mount manager."""

from enum import Enum
from pathlib import Path

from ..const import SUPERVISOR_DATA

FILE_CONFIG_MOUNTS = Path(SUPERVISOR_DATA, "mounts.json")
HOST_SUPERVISOR_DATA = Path("/mnt/data/supervisor")

ATTR_MOUNTS = "mounts"
ATTR_PATH = "path"
ATTR_SERVER = "server"
ATTR_SHARE = "share"
ATTR_USAGE = "usage"


class MountType(str, Enum):
    """Mount type."""

    BIND = "bind"
    CIFS = "cifs"
    NFS = "nfs"


class MountUsage(str, Enum):
    """Mount usage."""

    BACKUP = "backup"
    MEDIA = "media"


class MountState(str, Enum):
    """Mount state."""

    ACTIVE = "active"
    FAILED = "failed"
    UNKNOWN = "unknown"
