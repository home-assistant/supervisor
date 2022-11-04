"""Test fixup system reboot."""

from unittest.mock import PropertyMock, patch

from supervisor.coresys import CoreSys
from supervisor.host.const import HostFeature
from supervisor.host.manager import HostManager
from supervisor.resolution.const import ContextType, IssueType, SuggestionType
from supervisor.resolution.data import Issue, Suggestion
from supervisor.resolution.fixups.system_execute_reboot import FixupSystemExecuteReboot


async def test_fixup(coresys: CoreSys, dbus: list[str]):
    """Test fixup."""
    await coresys.dbus.logind.connect(coresys.dbus.bus)
    dbus.clear()

    system_execute_reboot = FixupSystemExecuteReboot(coresys)
    assert system_execute_reboot.auto is False

    coresys.resolution.suggestions = Suggestion(
        SuggestionType.EXECUTE_REBOOT, ContextType.SYSTEM
    )
    coresys.resolution.issues = Issue(IssueType.REBOOT_REQUIRED, ContextType.SYSTEM)

    with patch.object(
        HostManager, "features", new=PropertyMock(return_value=[HostFeature.REBOOT])
    ):
        await system_execute_reboot()

    assert dbus == ["/org/freedesktop/login1-org.freedesktop.login1.Manager.Reboot"]
    assert len(coresys.resolution.suggestions) == 0
    assert len(coresys.resolution.issues) == 0
