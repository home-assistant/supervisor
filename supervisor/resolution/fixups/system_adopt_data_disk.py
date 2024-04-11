"""Adopt data disk fixup."""

import logging
from pathlib import Path

from ...coresys import CoreSys
from ...dbus.udisks2.data import DeviceSpecification
from ...exceptions import DBusError, HostError, ResolutionFixupError
from ...os.const import FILESYSTEM_LABEL_DATA_DISK, FILESYSTEM_LABEL_OLD_DATA_DISK
from ..const import ContextType, IssueType, SuggestionType
from .base import FixupBase

_LOGGER: logging.Logger = logging.getLogger(__name__)


def setup(coresys: CoreSys) -> FixupBase:
    """Check setup function."""
    return FixupSystemAdoptDataDisk(coresys)


class FixupSystemAdoptDataDisk(FixupBase):
    """Storage class for fixup."""

    async def process_fixup(self, reference: str | None = None) -> None:
        """Initialize the fixup class."""
        if not (
            new_resolved := await self.sys_dbus.udisks2.resolve_device(
                DeviceSpecification(path=Path(reference))
            )
        ):
            _LOGGER.info(
                "Data disk at %s with name conflict was removed, skipping adopt",
                reference,
            )
            return

        current = self.sys_dbus.agent.datadisk.current_device
        if (
            not current
            or not (
                current_resolved := await self.sys_dbus.udisks2.resolve_device(
                    DeviceSpecification(path=current)
                )
            )
            or not current_resolved[0].filesystem
        ):
            raise ResolutionFixupError(
                "Cannot resolve current data disk for rename", _LOGGER.error
            )

        if new_resolved[0].id_label != FILESYSTEM_LABEL_DATA_DISK:
            _LOGGER.info(
                "Renaming disabled data disk at %s to %s to activate it",
                reference,
                FILESYSTEM_LABEL_DATA_DISK,
            )
            try:
                await new_resolved[0].filesystem.set_label(FILESYSTEM_LABEL_DATA_DISK)
            except DBusError as err:
                raise ResolutionFixupError(
                    f"Could not rename filesystem at {reference}: {err!s}",
                    _LOGGER.error,
                ) from err

        _LOGGER.info(
            "Renaming current data disk at %s to %s so new data disk at %s becomes primary ",
            self.sys_dbus.agent.datadisk.current_device,
            FILESYSTEM_LABEL_OLD_DATA_DISK,
            reference,
        )
        try:
            await current_resolved[0].filesystem.set_label(
                FILESYSTEM_LABEL_OLD_DATA_DISK
            )
        except DBusError as err:
            raise ResolutionFixupError(
                f"Could not rename filesystem at {current.as_posix()}: {err!s}",
                _LOGGER.error,
            ) from err

        _LOGGER.info("Rebooting the host to finish adoption")
        try:
            await self.sys_host.control.reboot()
        except (HostError, DBusError) as err:
            _LOGGER.warning(
                "Could not reboot host to finish data disk adoption, manual reboot required to finish process: %s",
                err,
            )
            self.sys_resolution.create_issue(
                IssueType.REBOOT_REQUIRED,
                ContextType.SYSTEM,
                suggestions=[SuggestionType.EXECUTE_REBOOT],
            )

    @property
    def suggestion(self) -> SuggestionType:
        """Return a SuggestionType enum."""
        return SuggestionType.ADOPT_DATA_DISK

    @property
    def context(self) -> ContextType:
        """Return a ContextType enum."""
        return ContextType.SYSTEM

    @property
    def issues(self) -> list[IssueType]:
        """Return a IssueType enum list."""
        return [IssueType.DISABLED_DATA_DISK, IssueType.MULTIPLE_DATA_DISKS]
