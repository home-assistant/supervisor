"""Constants for mount manager."""

from enum import StrEnum
from pathlib import PurePath

FILE_CONFIG_MOUNTS = PurePath("mounts.json")

ATTR_DEFAULT_BACKUP_MOUNT = "default_backup_mount"
ATTR_MOUNTS = "mounts"
ATTR_PATH = "path"
ATTR_READ_ONLY = "read_only"
ATTR_SERVER = "server"
ATTR_SHARE = "share"
ATTR_USAGE = "usage"


class MountType(StrEnum):
    """Mount type."""

    BIND = "bind"
    CIFS = "cifs"
    NFS = "nfs"


class MountUsage(StrEnum):
    """Mount usage."""

    BACKUP = "backup"
    MEDIA = "media"
    SHARE = "share"


class MountCifsVersion(StrEnum):
    """Mount CIFS version."""

    LEGACY_1_0 = "1.0"
    LEGACY_2_0 = "2.0"
