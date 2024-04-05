"""Helpers to check for multiple data disks."""

from pathlib import Path

from ...const import CoreState
from ...coresys import CoreSys
from ...dbus.udisks2.block import UDisks2Block
from ...dbus.udisks2.data import DeviceSpecification
from ...os.const import FILESYSTEM_LABEL_DATA_DISK
from ..const import ContextType, IssueType, SuggestionType
from .base import CheckBase


def setup(coresys: CoreSys) -> CheckBase:
    """Check setup function."""
    return CheckMultipleDataDisks(coresys)


class CheckMultipleDataDisks(CheckBase):
    """CheckMultipleDataDisks class for check."""

    async def run_check(self) -> None:
        """Run check if not affected by issue."""
        for block_device in self.sys_dbus.udisks2.block_devices:
            if self._block_device_has_name_issue(block_device):
                self.sys_resolution.create_issue(
                    IssueType.MULTIPLE_DATA_DISKS,
                    ContextType.SYSTEM,
                    reference=block_device.device.as_posix(),
                    suggestions=[
                        SuggestionType.RENAME_DATA_DISK,
                        SuggestionType.ADOPT_DATA_DISK,
                    ],
                )

    async def approve_check(self, reference: str | None = None) -> bool:
        """Approve check if it is affected by issue."""
        resolved = await self.sys_dbus.udisks2.resolve_device(
            DeviceSpecification(path=Path(reference))
        )
        return resolved and self._block_device_has_name_issue(resolved[0])

    def _block_device_has_name_issue(self, block_device: UDisks2Block) -> bool:
        """Return true if filesystem block device incorrectly has data disk name."""
        return (
            block_device.filesystem
            and block_device.id_label == FILESYSTEM_LABEL_DATA_DISK
            and block_device.device != self.sys_dbus.agent.datadisk.current_device
        )

    @property
    def issue(self) -> IssueType:
        """Return a IssueType enum."""
        return IssueType.MULTIPLE_DATA_DISKS

    @property
    def context(self) -> ContextType:
        """Return a ContextType enum."""
        return ContextType.SYSTEM

    @property
    def states(self) -> list[CoreState]:
        """Return a list of valid states when this check can run."""
        return [CoreState.RUNNING, CoreState.SETUP]
