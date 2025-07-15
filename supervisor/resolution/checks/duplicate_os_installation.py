"""Helpers to check for duplicate OS installations."""

import logging

from ...const import CoreState
from ...coresys import CoreSys
from ...dbus.udisks2.data import DeviceSpecification
from ..const import ContextType, IssueType, UnhealthyReason
from .base import CheckBase

_LOGGER: logging.Logger = logging.getLogger(__name__)

# Partition labels to check for duplicates (GPT-based installations)
HAOS_PARTITIONS = [
    "hassos-boot",
    "hassos-kernel0",
    "hassos-kernel1",
    "hassos-system0",
    "hassos-system1",
]

# Partition UUIDs to check for duplicates (MBR-based installations)
HAOS_PARTITION_UUIDS = [
    "48617373-01",  # hassos-boot
    "48617373-05",  # hassos-kernel0
    "48617373-06",  # hassos-system0
    "48617373-07",  # hassos-kernel1
    "48617373-08",  # hassos-system1
]


def setup(coresys: CoreSys) -> CheckBase:
    """Check setup function."""
    return CheckDuplicateOSInstallation(coresys)


class CheckDuplicateOSInstallation(CheckBase):
    """CheckDuplicateOSInstallation class for check."""

    async def run_check(self) -> None:
        """Run check if not affected by issue."""
        # Check GPT-based installations (partition labels)
        for partition_label in HAOS_PARTITIONS:
            try:
                resolved = await self.sys_dbus.udisks2.resolve_device(
                    DeviceSpecification(partlabel=partition_label)
                )
                if resolved and len(resolved) > 1:
                    _LOGGER.warning(
                        "Found duplicate OS installation: %s partition exists on %d devices",
                        partition_label,
                        len(resolved),
                    )
                    self.sys_resolution.add_unhealthy_reason(
                        UnhealthyReason.DUPLICATE_OS_INSTALLATION
                    )
                    self.sys_resolution.create_issue(
                        IssueType.DUPLICATE_OS_INSTALLATION,
                        ContextType.SYSTEM,
                    )
                    return
            except Exception as err:
                _LOGGER.debug(
                    "Failed to resolve device for partition %s: %s",
                    partition_label,
                    err,
                )

        # Check MBR-based installations (partition UUIDs)
        for partition_uuid in HAOS_PARTITION_UUIDS:
            try:
                resolved = await self.sys_dbus.udisks2.resolve_device(
                    DeviceSpecification(partuuid=partition_uuid)
                )
                if resolved and len(resolved) > 1:
                    _LOGGER.warning(
                        "Found duplicate OS installation: %s partition UUID exists on %d devices",
                        partition_uuid,
                        len(resolved),
                    )
                    self.sys_resolution.add_unhealthy_reason(
                        UnhealthyReason.DUPLICATE_OS_INSTALLATION
                    )
                    self.sys_resolution.create_issue(
                        IssueType.DUPLICATE_OS_INSTALLATION,
                        ContextType.SYSTEM,
                    )
                    return
            except Exception as err:
                _LOGGER.debug(
                    "Failed to resolve device for partition UUID %s: %s",
                    partition_uuid,
                    err,
                )

    async def approve_check(self, reference: str | None = None) -> bool:
        """Approve check if it is affected by issue."""
        # Check all partitions for duplicates since issue is created without reference

        # Check GPT-based installations (partition labels)
        for partition_label in HAOS_PARTITIONS:
            try:
                resolved = await self.sys_dbus.udisks2.resolve_device(
                    DeviceSpecification(partlabel=partition_label)
                )
                if resolved and len(resolved) > 1:
                    return True
            except Exception as err:
                _LOGGER.debug(
                    "Failed to resolve device for partition %s: %s",
                    partition_label,
                    err,
                )

        # Check MBR-based installations (partition UUIDs)
        for partition_uuid in HAOS_PARTITION_UUIDS:
            try:
                resolved = await self.sys_dbus.udisks2.resolve_device(
                    DeviceSpecification(partuuid=partition_uuid)
                )
                if resolved and len(resolved) > 1:
                    return True
            except Exception as err:
                _LOGGER.debug(
                    "Failed to resolve device for partition UUID %s: %s",
                    partition_uuid,
                    err,
                )

        return False

    @property
    def issue(self) -> IssueType:
        """Return a IssueType enum."""
        return IssueType.DUPLICATE_OS_INSTALLATION

    @property
    def context(self) -> ContextType:
        """Return a ContextType enum."""
        return ContextType.SYSTEM

    @property
    def states(self) -> list[CoreState]:
        """Return a list of valid states when this check can run."""
        return [CoreState.SETUP]
