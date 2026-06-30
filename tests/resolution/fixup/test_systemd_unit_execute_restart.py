"""Test fixup systemd unit execute restart."""

from unittest.mock import AsyncMock, patch

from supervisor.coresys import CoreSys
from supervisor.dbus.const import StartUnitMode
from supervisor.exceptions import DBusError, DBusSystemdNoSuchUnit
from supervisor.resolution.const import ContextType, IssueType, SuggestionType
from supervisor.resolution.data import Issue, Suggestion
from supervisor.resolution.fixups.systemd_unit_execute_restart import (
    FixupSystemdUnitExecuteRestart,
)

ISSUE = Issue(IssueType.SYSTEMD_UNIT_FAILED, ContextType.SYSTEM, reference="a.service")
SUGGESTION = Suggestion(
    SuggestionType.EXECUTE_RESTART,
    ContextType.SYSTEM,
    reference="a.service",
)


async def test_fixup_restart_success(coresys: CoreSys):
    """Test restart fixup succeeds and cleans issue/suggestion."""
    systemd_unit_execute_restart = FixupSystemdUnitExecuteRestart(coresys)
    assert systemd_unit_execute_restart.suggestion == SuggestionType.EXECUTE_RESTART
    assert systemd_unit_execute_restart.context == ContextType.SYSTEM
    assert systemd_unit_execute_restart.issues == [IssueType.SYSTEMD_UNIT_FAILED]
    assert systemd_unit_execute_restart.auto is False

    coresys.resolution.add_suggestion(SUGGESTION)
    coresys.resolution.add_issue(ISSUE)

    with patch.object(
        coresys.dbus.systemd,
        "restart_unit",
        new_callable=AsyncMock,
    ) as restart_unit:
        await systemd_unit_execute_restart()

    restart_unit.assert_awaited_once_with("a.service", StartUnitMode.REPLACE)
    assert not coresys.resolution.suggestions
    assert not coresys.resolution.issues


async def test_fixup_restart_no_such_unit(coresys: CoreSys):
    """Test no-such-unit is tolerated and clears issue/suggestion."""
    systemd_unit_execute_restart = FixupSystemdUnitExecuteRestart(coresys)
    coresys.resolution.add_suggestion(SUGGESTION)
    coresys.resolution.add_issue(ISSUE)

    with patch.object(
        coresys.dbus.systemd,
        "restart_unit",
        new_callable=AsyncMock,
        side_effect=DBusSystemdNoSuchUnit("missing"),
    ) as restart_unit:
        await systemd_unit_execute_restart()

    restart_unit.assert_awaited_once_with("a.service", StartUnitMode.REPLACE)
    assert not coresys.resolution.suggestions
    assert not coresys.resolution.issues


async def test_fixup_restart_dbus_error_keeps_issue(coresys: CoreSys):
    """Test DBus error keeps issue/suggestion in place."""
    systemd_unit_execute_restart = FixupSystemdUnitExecuteRestart(coresys)
    coresys.resolution.add_suggestion(SUGGESTION)
    coresys.resolution.add_issue(ISSUE)

    with patch.object(
        coresys.dbus.systemd,
        "restart_unit",
        new_callable=AsyncMock,
        side_effect=DBusError("boom"),
    ) as restart_unit:
        await systemd_unit_execute_restart()

    restart_unit.assert_awaited_once_with("a.service", StartUnitMode.REPLACE)
    assert ISSUE in coresys.resolution.issues
    assert SUGGESTION in coresys.resolution.suggestions
