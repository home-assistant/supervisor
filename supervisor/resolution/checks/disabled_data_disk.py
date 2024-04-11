"""Helpers to check for a disabled data disk."""

from pathlib import Path

from ...const import CoreState
from ...coresys import CoreSys
from ...dbus.udisks2.block import UDisks2Block
from ...dbus.udisks2.data import DeviceSpecification
from ...os.const import FILESYSTEM_LABEL_DISABLED_DATA_DISK
from ..const import ContextType, IssueType, SuggestionType
from .base import CheckBase


def setup(coresys: CoreSys) -> CheckBase:
    """Check setup function."""
    return CheckDisabledDataDisk(coresys)


class CheckDisabledDataDisk(CheckBase):
    """CheckDisabledDataDisk class for check."""

    async def run_check(self) -> None:
        """Run check if not affected by issue."""
        for block_device in self.sys_dbus.udisks2.block_devices:
            if self._is_disabled_data_disk(block_device):
                self.sys_resolution.create_issue(
                    IssueType.DISABLED_DATA_DISK,
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
        return resolved and self._is_disabled_data_disk(resolved[0])

    def _is_disabled_data_disk(self, block_device: UDisks2Block) -> bool:
        """Return true if filesystem block device has name indicating it was disabled by OS."""
        return (
            block_device.filesystem
            and block_device.id_label == FILESYSTEM_LABEL_DISABLED_DATA_DISK
        )

    @property
    def issue(self) -> IssueType:
        """Return a IssueType enum."""
        return IssueType.DISABLED_DATA_DISK

    @property
    def context(self) -> ContextType:
        """Return a ContextType enum."""
        return ContextType.SYSTEM

    @property
    def states(self) -> list[CoreState]:
        """Return a list of valid states when this check can run."""
        return [CoreState.RUNNING, CoreState.SETUP]
