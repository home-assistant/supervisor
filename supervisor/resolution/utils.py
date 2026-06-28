"""Helpers for resolution manager state."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from .const import ContextType, IssueType, SuggestionType

if TYPE_CHECKING:
    from ..coresys import CoreSys
    from ..dbus.agent.boards.rpi_firmware import RPiFirmware


RPI_FIRMWARE_UPDATE_ISSUES = (
    IssueType.RPI_FIRMWARE_UPDATE_AVAILABLE,
    IssueType.RPI_FIRMWARE_UPDATE_BLOCKED,
)


def _dismiss_issue_type(coresys: CoreSys, issue_type: IssueType) -> None:
    """Dismiss all system issues of a type."""
    for issue in list(coresys.resolution.issues):
        if issue.type == issue_type and issue.context == ContextType.SYSTEM:
            coresys.resolution.dismiss_issue(issue)


def dismiss_rpi_firmware_update_issues(coresys: CoreSys) -> None:
    """Dismiss all Raspberry Pi firmware update issues."""
    for issue_type in RPI_FIRMWARE_UPDATE_ISSUES:
        _dismiss_issue_type(coresys, issue_type)


def _upsert_issue(
    coresys: CoreSys,
    issue_type: IssueType,
    *,
    suggestions: list[SuggestionType] | None = None,
    reference_extra: dict[str, Any] | None = None,
) -> None:
    """Create a system issue, replacing stale metadata for that issue type."""
    for issue in list(coresys.resolution.issues):
        if issue.type != issue_type or issue.context != ContextType.SYSTEM:
            continue
        if issue.reference_extra == reference_extra:
            break
        coresys.resolution.dismiss_issue(issue)

    coresys.resolution.create_issue(
        issue_type,
        ContextType.SYSTEM,
        suggestions=suggestions,
        reference_extra=reference_extra,
    )


def sync_rpi_firmware_issues(coresys: CoreSys, rpi_firmware: RPiFirmware) -> None:
    """Sync Raspberry Pi firmware state into resolution issues."""
    if rpi_firmware.update_pending:
        dismiss_rpi_firmware_update_issues(coresys)
        coresys.resolution.create_issue(
            IssueType.REBOOT_REQUIRED,
            ContextType.SYSTEM,
            suggestions=[SuggestionType.EXECUTE_REBOOT],
        )
        return

    if rpi_firmware.update_blocked:
        _dismiss_issue_type(coresys, IssueType.RPI_FIRMWARE_UPDATE_AVAILABLE)
        _upsert_issue(
            coresys,
            IssueType.RPI_FIRMWARE_UPDATE_BLOCKED,
            reference_extra={
                "current_version": rpi_firmware.current_version,
                "latest_version": rpi_firmware.latest_version,
                "blocked_reason": rpi_firmware.blocked_reason,
            },
        )
        return

    _dismiss_issue_type(coresys, IssueType.RPI_FIRMWARE_UPDATE_BLOCKED)
    if rpi_firmware.update_available:
        _upsert_issue(
            coresys,
            IssueType.RPI_FIRMWARE_UPDATE_AVAILABLE,
            suggestions=[SuggestionType.UPDATE_RPI_FIRMWARE],
            reference_extra={
                "current_version": rpi_firmware.current_version,
                "latest_version": rpi_firmware.latest_version,
            },
        )
        return

    _dismiss_issue_type(coresys, IssueType.RPI_FIRMWARE_UPDATE_AVAILABLE)
