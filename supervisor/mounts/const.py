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
# Deliberately not `UDisks2Manager.supported_filesystems`: that property
# reflects which filesystems the host has userspace tooling for (mkfs,
# fsck), which is neither necessary nor sufficient for mounting one. The
# HAOS kernel has ext4 and vfat built in and ships ntfs3, exfat and btrfs
# as modules, so this is the set we can actually hand to systemd. ext2 and
# ext3 are probed as distinct types but mounted by the same ext4 driver.
SUPPORTED_LOCAL_FILESYSTEMS = {
    "btrfs",
    "exfat",
    "ext2",
    "ext3",
    "ext4",
    "ntfs",
    "vfat",
}

# UDisks2/blkid report the probed signature, which is not always the name of
# the kernel driver that mounts it: the "ntfs" signature is mounted by the
# in-tree ntfs3 driver, and ext2/ext3 are both handled by ext4. Only the
# systemd unit's Type= is translated — the probed value is what gets
# persisted and reported back over the API.
KERNEL_FILESYSTEM_MAP = {"ext2": "ext4", "ext3": "ext4", "ntfs": "ntfs3"}

# Filesystem labels starting with this prefix belong to Home Assistant OS
# itself (hassos-data, hassos-data-old, hassos-boot, ...) and must never be
# offered as a user mount, regardless of what the system hints say.
HASSOS_LABEL_PREFIX = "hassos"

# UDisks2 Block.IdUsage value marking a device as holding a mountable
# filesystem, as opposed to swap, a LUKS container, a RAID member or a
# partition table.
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
