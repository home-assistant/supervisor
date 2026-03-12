"""Test fixup system enable NTP."""

from supervisor.coresys import CoreSys
from supervisor.resolution.const import ContextType, IssueType, SuggestionType
from supervisor.resolution.data import Issue, Suggestion
from supervisor.resolution.fixups.system_enable_ntp import FixupSystemEnableNTP

from tests.dbus_service_mocks.base import DBusServiceMock
from tests.dbus_service_mocks.systemd import Systemd as SystemdService


async def test_fixup(
    coresys: CoreSys,
    all_dbus_services: dict[str, DBusServiceMock | dict[str, DBusServiceMock]],
):
    """Test fixup."""
    systemd_service: SystemdService = all_dbus_services["systemd"]
    systemd_service.StartUnit.calls.clear()

    system_enable_ntp = FixupSystemEnableNTP(coresys)
    assert system_enable_ntp.auto is False

    coresys.resolution.add_suggestion(
        Suggestion(SuggestionType.ENABLE_NTP, ContextType.SYSTEM)
    )
    coresys.resolution.add_issue(Issue(IssueType.NTP_SYNC_FAILED, ContextType.SYSTEM))

    await system_enable_ntp()

    assert systemd_service.StartUnit.calls == [("systemd-timesyncd.service", "replace")]
    assert len(coresys.resolution.suggestions) == 0
    assert len(coresys.resolution.issues) == 0
