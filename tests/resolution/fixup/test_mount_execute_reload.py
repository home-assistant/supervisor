"""Test fixup mount reload."""

import errno
from unittest.mock import MagicMock, patch

from supervisor.coresys import CoreSys
from supervisor.mounts.mount import Mount
from supervisor.resolution.const import ContextType, IssueType, SuggestionType
from supervisor.resolution.data import Issue
from supervisor.resolution.fixups.mount_execute_reload import FixupMountExecuteReload

from tests.dbus_service_mocks.base import DBusServiceMock
from tests.dbus_service_mocks.systemd import Systemd as SystemdService


async def test_fixup(
    coresys: CoreSys,
    all_dbus_services: dict[str, DBusServiceMock],
    path_extern,
    mount_propagation,
    mock_is_mount,
):
    """Test fixup."""
    systemd_service: SystemdService = all_dbus_services["systemd"]
    systemd_service.ReloadOrRestartUnit.calls.clear()

    mount_execute_reload = FixupMountExecuteReload(coresys)

    assert mount_execute_reload.auto is False

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
    await mount_execute_reload()

    assert coresys.resolution.issues == []
    assert coresys.resolution.suggestions == []
    assert "test" in coresys.mounts
    # Mount is reachable (probe passes via mock_is_mount); the fixup
    # clears the issue without needing to touch systemd. A user invoking
    # the fixup on a still-broken mount would fail the probe, exercising
    # the reload->restart path covered by test_fixup_error_after_reload.
    assert systemd_service.ReloadOrRestartUnit.calls == []


async def test_fixup_error_after_reload(
    coresys: CoreSys,
    all_dbus_services: dict[str, DBusServiceMock],
    mock_is_mount: MagicMock,
    path_extern,
    mount_propagation,
):
    """Test fixup."""
    mount_execute_reload = FixupMountExecuteReload(coresys)
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
    # Probe (statvfs) fails — the mount stays unreachable through the
    # reload -> restart cycle. Fixup catches MountError and re-raises
    # ResolutionFixupError, which FixupBase.__call__ swallows to skip
    # issue cleanup. Caller sees no error.
    with patch(
        "supervisor.mounts.mount.os.statvfs",
        side_effect=OSError(errno.EHOSTDOWN, "Host is down"),
    ):
        await mount_execute_reload()

    # Probe never succeeds, issue remains.
    assert (
        Issue(IssueType.MOUNT_FAILED, ContextType.MOUNT, reference="test")
        in coresys.resolution.issues
    )
