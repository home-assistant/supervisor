"""Helpers for local disk mounts."""

from ..coresys import CoreSys
from ..dbus.udisks2.block import UDisks2Block
from ..exceptions import (
    MountDeviceInUseError,
    MountDeviceMissingUUIDError,
    MountDeviceProtectedError,
    MountFilesystemNotSupportedError,
)
from ..os.const import (
    PARTITION_NAME_EXTERNAL_DATA_DISK,
    PARTITION_NAME_OLD_EXTERNAL_DATA_DISK,
)
from .const import HASSOS_LABEL_PREFIX, ID_USAGE_FILESYSTEM, SUPPORTED_LOCAL_FILESYSTEMS

# Partition names HAOS uses for an external data disk. Mounting one would
# race the OS for the same partition on the next boot.
PROTECTED_PARTITION_NAMES = {
    PARTITION_NAME_EXTERNAL_DATA_DISK,
    PARTITION_NAME_OLD_EXTERNAL_DATA_DISK,
}


def validate_block_for_mount(
    coresys: CoreSys, block: UDisks2Block, *, used_uuids: set[str]
) -> None:
    """Raise if a block device cannot be used as a disk mount.

    One code path serves both callers: enumerating candidates catches these
    to filter the list, while creating a mount lets them propagate to the
    user. The two can therefore never disagree about what is mountable.

    Order matters. The cheap structural checks come first so a device that
    is excluded for several reasons reports the most fundamental one.
    """
    device = block.device.as_posix() if block.device else ""

    # Only devices holding a mountable filesystem: excludes swap, LUKS
    # containers, RAID members and bare partition tables.
    if block.id_usage != ID_USAGE_FILESYSTEM:
        raise MountFilesystemNotSupportedError(device=device)

    # UDisks2 asks that devices hinted as hidden are not shown to users
    if block.hint_ignore:
        raise MountDeviceProtectedError(device=device)

    if block.hint_system:
        raise MountDeviceProtectedError(device=device)

    # Load-bearing beyond the system hint: a previous data disk is labelled
    # hassos-data-old and reports HintSystem=False, but is still ours.
    if (block.id_label or "").startswith(HASSOS_LABEL_PREFIX):
        raise MountDeviceProtectedError(device=device)

    if block.partition and block.partition.name_ in PROTECTED_PARTITION_NAMES:
        raise MountDeviceProtectedError(device=device)

    if _is_current_data_disk(coresys, block):
        raise MountDeviceProtectedError(device=device)

    # Mounted anywhere on the host already, by us or by anything else
    if block.filesystem and block.filesystem.mount_points:
        raise MountDeviceInUseError(device=device)

    if block.id_type not in SUPPORTED_LOCAL_FILESYSTEMS:
        raise MountFilesystemNotSupportedError(device=device)

    # A mount is persisted and re-mounted by UUID, so without one there is
    # nothing stable to record.
    if not block.id_uuid:
        raise MountDeviceMissingUUIDError(device=device)

    if block.id_uuid in used_uuids:
        raise MountDeviceInUseError(device=device)


def _is_current_data_disk(coresys: CoreSys, block: UDisks2Block) -> bool:
    """Return true if this block device holds the data partition in use.

    OS-Agent is absent on non-HAOS installations, where there is no managed
    data disk to protect in the first place.
    """
    datadisk = coresys.dbus.agent.datadisk
    if not datadisk.is_connected:
        return False

    current_device = datadisk.current_device
    return bool(current_device) and block.device == current_device
