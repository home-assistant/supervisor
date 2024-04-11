"""Rename data disk fixup."""

import logging
from pathlib import Path

from ...coresys import CoreSys
from ...dbus.udisks2.data import DeviceSpecification
from ...exceptions import DBusError, ResolutionFixupError
from ...os.const import FILESYSTEM_LABEL_OLD_DATA_DISK
from ..const import ContextType, IssueType, SuggestionType
from .base import FixupBase

_LOGGER: logging.Logger = logging.getLogger(__name__)


def setup(coresys: CoreSys) -> FixupBase:
    """Check setup function."""
    return FixupSystemRenameDataDisk(coresys)


class FixupSystemRenameDataDisk(FixupBase):
    """Storage class for fixup."""

    async def process_fixup(self, reference: str | None = None) -> None:
        """Initialize the fixup class."""
        resolved = await self.sys_dbus.udisks2.resolve_device(
            DeviceSpecification(path=Path(reference))
        )

        if not resolved:
            _LOGGER.info(
                "Data disk at %s with name conflict was removed, skipping rename",
                reference,
            )
            return

        if not resolved[0].filesystem:
            _LOGGER.warning(
                "Data disk at %s no longer appears to be a filesystem, skipping rename",
                reference,
            )
            return

        _LOGGER.info(
            "Renaming %s to %s to prevent data disk name conflict",
            reference,
            FILESYSTEM_LABEL_OLD_DATA_DISK,
        )
        try:
            await resolved[0].filesystem.set_label(FILESYSTEM_LABEL_OLD_DATA_DISK)
        except DBusError as err:
            raise ResolutionFixupError(
                f"Could not rename filesystem at {reference}: {err!s}", _LOGGER.error
            ) from err

    @property
    def suggestion(self) -> SuggestionType:
        """Return a SuggestionType enum."""
        return SuggestionType.RENAME_DATA_DISK

    @property
    def context(self) -> ContextType:
        """Return a ContextType enum."""
        return ContextType.SYSTEM

    @property
    def issues(self) -> list[IssueType]:
        """Return a IssueType enum list."""
        return [IssueType.DISABLED_DATA_DISK, IssueType.MULTIPLE_DATA_DISKS]
