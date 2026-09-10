"""Constants for mount manager."""

from enum import StrEnum
from pathlib import PurePath

FILE_CONFIG_MOUNTS = PurePath("mounts.json")

ATTR_DEFAULT_BACKUP_MOUNT = "default_backup_mount"
ATTR_DEVICE = "device"
ATTR_FILESYSTEM = "filesystem"
ATTR_MOUNTS = "mounts"
ATTR_PATH = "path"
ATTR_READ_ONLY = "read_only"
ATTR_SERVER = "server"
ATTR_SHARE = "share"
ATTR_USAGE = "usage"

# Filesystems a local disk may be mounted with.
#
# Not UDisks2Manager.supported_filesystems — that is mkfs/fsck tooling, not
# mount support. This is the set the HAOS kernel can actually mount: ext4
# and vfat built in, ntfs3/exfat/btrfs as modules. ext2/ext3 probe as their
# own types but use the ext4 driver.
#
# f2fs needs HAOS 18.3+. On an older OS the mount fails until the OS is
# updated, same as Supervised installs whose kernel we do not control.
SUPPORTED_LOCAL_FILESYSTEMS = {
    "btrfs",
    "exfat",
    "ext2",
    "ext3",
    "ext4",
    "f2fs",
    "ntfs",
    "vfat",
}

# UDisks2/blkid report the on-disk signature, which is not always the kernel
# driver name. Only Type= on the systemd unit is translated; the probed value
# is persisted and returned by the API.
KERNEL_FILESYSTEM_MAP = {"ext2": "ext4", "ext3": "ext4", "ntfs": "ntfs3"}

# Filesystem labels starting with this prefix belong to Home Assistant OS
# (hassos-data, hassos-data-old, hassos-boot, ...) and must not be offered
# as a user mount.
HASSOS_LABEL_PREFIX = "hassos"

# UDisks2 Block.IdUsage for a mountable filesystem (not swap, LUKS, RAID, or
# a partition table).
ID_USAGE_FILESYSTEM = "filesystem"


class MountType(StrEnum):
    """Mount type."""

    BIND = "bind"
    CIFS = "cifs"
    DISK = "disk"
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
