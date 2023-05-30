"""Test fixup mount remove."""

from supervisor.coresys import CoreSys
from supervisor.mounts.mount import Mount
from supervisor.resolution.const import ContextType, IssueType, SuggestionType
from supervisor.resolution.fixups.mount_execute_remove import FixupMountExecuteRemove

from tests.dbus_service_mocks.base import DBusServiceMock
from tests.dbus_service_mocks.systemd import Systemd as SystemdService


async def test_fixup(
    coresys: CoreSys,
    all_dbus_services: dict[str, DBusServiceMock],
    path_extern,
    mount_propagation,
):
    """Test fixup."""
    systemd_service: SystemdService = all_dbus_services["systemd"]
    systemd_service.StopUnit.calls.clear()

    mount_execute_remove = FixupMountExecuteRemove(coresys)

    assert mount_execute_remove.auto is False

    await coresys.mounts.create_mount(
        Mount.from_dict(
            coresys,
            {
                "name": "test",
                "usage": "backup",
                "type": "cifs",
                "server": "test.local",
                "share": "test",
            },
        )
    )

    coresys.resolution.create_issue(
        IssueType.MOUNT_FAILED,
        ContextType.MOUNT,
        reference="test",
        suggestions=[SuggestionType.EXECUTE_RELOAD, SuggestionType.EXECUTE_REMOVE],
    )
    await mount_execute_remove()

    assert coresys.resolution.issues == []
    assert coresys.resolution.suggestions == []
    assert coresys.mounts.mounts == []
    assert systemd_service.StopUnit.calls == [
        ("mnt-data-supervisor-mounts-test.mount", "fail")
    ]
