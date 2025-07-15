"""Helpers to check for duplicate OS installations."""

import logging

from ...const import CoreState
from ...coresys import CoreSys
from ...dbus.udisks2.data import DeviceSpecification
from ..const import ContextType, IssueType, UnhealthyReason
from .base import CheckBase

_LOGGER: logging.Logger = logging.getLogger(__name__)

# Partition labels to check for duplicates
HAOS_PARTITIONS = [
    "hassos-kernel0",
    "hassos-kernel1",
    "hassos-system0",
    "hassos-system1",
    "hassos-boot",
]


def setup(coresys: CoreSys) -> CheckBase:
    """Check setup function."""
    return CheckDuplicateOSInstallation(coresys)


class CheckDuplicateOSInstallation(CheckBase):
    """CheckDuplicateOSInstallation class for check."""

    async def run_check(self) -> None:
        """Run check if not affected by issue."""
        for partition_label in HAOS_PARTITIONS:
            try:
                resolved = await self.sys_dbus.udisks2.resolve_device(
                    DeviceSpecification(label=partition_label)
                )
                if resolved and len(resolved) > 1:
                    _LOGGER.warning(
                        "Found duplicate OS installation: %s partition exists on %d devices",
                        partition_label,
                        len(resolved),
                    )
                    self.sys_resolution.add_unhealthy_reason(UnhealthyReason.SETUP)
                    self.sys_resolution.create_issue(
                        IssueType.DUPLICATE_OS_INSTALLATION,
                        ContextType.SYSTEM,
                        reference=partition_label,
                    )
                    return
            except Exception as err:
                _LOGGER.debug(
                    "Failed to resolve device for partition %s: %s",
                    partition_label,
                    err,
                )

    async def approve_check(self, reference: str | None = None) -> bool:
        """Approve check if it is affected by issue."""
        if not reference:
            return False

        try:
            resolved = await self.sys_dbus.udisks2.resolve_device(
                DeviceSpecification(label=reference)
            )
            return resolved and len(resolved) > 1
        except Exception as err:
            _LOGGER.debug(
                "Failed to resolve device for partition %s: %s",
                reference,
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
