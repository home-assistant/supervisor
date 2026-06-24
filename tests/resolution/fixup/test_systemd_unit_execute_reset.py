"""Test fixup systemd unit execute reset."""

from unittest.mock import AsyncMock, patch

from supervisor.coresys import CoreSys
from supervisor.exceptions import DBusError, DBusSystemdNoSuchUnit
from supervisor.resolution.const import ContextType, IssueType, SuggestionType
from supervisor.resolution.data import Issue, Suggestion
from supervisor.resolution.fixups.systemd_unit_execute_reset import (
    FixupSystemdUnitExecuteReset,
)

ISSUE = Issue(IssueType.SYSTEMD_UNIT_FAILED, ContextType.SYSTEM, reference="a.service")
SUGGESTION = Suggestion(
    SuggestionType.EXECUTE_RESET,
    ContextType.SYSTEM,
    reference="a.service",
)


async def test_fixup_reset_success(coresys: CoreSys):
    """Test reset fixup succeeds and cleans issue/suggestion."""
    systemd_unit_execute_reset = FixupSystemdUnitExecuteReset(coresys)
    assert systemd_unit_execute_reset.suggestion == SuggestionType.EXECUTE_RESET
    assert systemd_unit_execute_reset.context == ContextType.SYSTEM
    assert systemd_unit_execute_reset.issues == [IssueType.SYSTEMD_UNIT_FAILED]
    assert systemd_unit_execute_reset.auto is False

    coresys.resolution.add_suggestion(SUGGESTION)
    coresys.resolution.add_issue(ISSUE)

    with patch.object(
        coresys.dbus.systemd,
        "reset_failed_unit",
        new_callable=AsyncMock,
    ) as reset_failed_unit:
        await systemd_unit_execute_reset()

    reset_failed_unit.assert_awaited_once_with("a.service")
    assert not coresys.resolution.suggestions
    assert not coresys.resolution.issues


async def test_fixup_reset_no_such_unit(coresys: CoreSys):
    """Test no-such-unit is tolerated and clears issue/suggestion."""
    systemd_unit_execute_reset = FixupSystemdUnitExecuteReset(coresys)
    coresys.resolution.add_suggestion(SUGGESTION)
    coresys.resolution.add_issue(ISSUE)

    with patch.object(
        coresys.dbus.systemd,
        "reset_failed_unit",
        new_callable=AsyncMock,
        side_effect=DBusSystemdNoSuchUnit("missing"),
    ) as reset_failed_unit:
        await systemd_unit_execute_reset()

    reset_failed_unit.assert_awaited_once_with("a.service")
    assert not coresys.resolution.suggestions
    assert not coresys.resolution.issues


async def test_fixup_reset_dbus_error_keeps_issue(coresys: CoreSys):
    """Test DBus error keeps issue/suggestion in place."""
    systemd_unit_execute_reset = FixupSystemdUnitExecuteReset(coresys)
    coresys.resolution.add_suggestion(SUGGESTION)
    coresys.resolution.add_issue(ISSUE)

    with patch.object(
        coresys.dbus.systemd,
        "reset_failed_unit",
        new_callable=AsyncMock,
        side_effect=DBusError("boom"),
    ) as reset_failed_unit:
        await systemd_unit_execute_reset()

    reset_failed_unit.assert_awaited_once_with("a.service")
    assert ISSUE in coresys.resolution.issues
    assert SUGGESTION in coresys.resolution.suggestions
