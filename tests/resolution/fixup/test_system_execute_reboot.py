"""Test fixup system reboot."""

from supervisor.coresys import CoreSys
from supervisor.resolution.const import ContextType, IssueType, SuggestionType
from supervisor.resolution.data import Issue, Suggestion
from supervisor.resolution.fixups.system_execute_reboot import FixupSystemExecuteReboot

from tests.dbus_service_mocks.base import DBusServiceMock
from tests.dbus_service_mocks.logind import Logind as LogindService


async def test_fixup(
    coresys: CoreSys,
    all_dbus_services: dict[str, DBusServiceMock | dict[str, DBusServiceMock]],
):
    """Test fixup."""
    logind_service: LogindService = all_dbus_services["logind"]
    logind_service.Reboot.calls.clear()

    system_execute_reboot = FixupSystemExecuteReboot(coresys)
    assert system_execute_reboot.auto is False

    coresys.resolution.add_suggestion(
        Suggestion(SuggestionType.EXECUTE_REBOOT, ContextType.SYSTEM)
    )
    coresys.resolution.add_issue(Issue(IssueType.REBOOT_REQUIRED, ContextType.SYSTEM))

    await system_execute_reboot()

    assert logind_service.Reboot.calls == [(False,)]
    assert len(coresys.resolution.suggestions) == 0
    assert len(coresys.resolution.issues) == 0
