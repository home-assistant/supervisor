"""Test fixup mount move local data."""

from unittest.mock import patch

from supervisor.coresys import CoreSys
from supervisor.exceptions import MountError
from supervisor.mounts.manager import MountManager
from supervisor.mounts.mount import Mount
from supervisor.resolution.const import ContextType, IssueType, SuggestionType
from supervisor.resolution.fixups.mount_move_local_data import FixupMountMoveLocalData

from tests.dbus_service_mocks.base import DBusServiceMock

MEDIA_TEST_DATA = {
    "name": "media_test",
    "type": "nfs",
    "usage": "media",
    "server": "media.local",
    "path": "/media",
}
BACKUP_TEST_DATA = {
    "name": "backup_test",
    "type": "cifs",
    "usage": "backup",
    "server": "backup.local",
    "share": "backups",
}


async def test_fixup_media_mount(
    coresys: CoreSys,
    all_dbus_services: dict[str, DBusServiceMock],
    tmp_supervisor_data,
    path_extern,
    mount_propagation,
    mock_is_mount,
):
    """Test fixup moves local data out of the media directory and remounts."""
    mount_move_local_data = FixupMountMoveLocalData(coresys)

    assert mount_move_local_data.auto is False

    await coresys.mounts.create_mount(Mount.from_dict(coresys, MEDIA_TEST_DATA))

    media_dir = coresys.config.path_media / "media_test"
    media_dir.mkdir(exist_ok=True)
    (media_dir / "recording.mp4").touch()

    coresys.resolution.create_issue(
        IssueType.MOUNT_FAILED,
        ContextType.MOUNT,
        reference="media_test",
        suggestions=[
            SuggestionType.MOVE_LOCAL_DATA,
            SuggestionType.EXECUTE_RELOAD,
            SuggestionType.EXECUTE_REMOVE,
        ],
    )

    await mount_move_local_data()

    recovery_dir = coresys.config.path_media / "media_test_local_recovery"
    assert (recovery_dir / "recording.mp4").exists()
    assert media_dir.is_dir()
    assert not any(media_dir.iterdir())
    assert coresys.resolution.issues == []
    assert coresys.resolution.suggestions == []
    assert "media_test" in coresys.mounts


async def test_fixup_backup_mount(
    coresys: CoreSys,
    all_dbus_services: dict[str, DBusServiceMock],
    tmp_supervisor_data,
    path_extern,
    mount_propagation,
    mock_is_mount,
):
    """Test fixup moves local data of a backup mount to local backup storage."""
    mount_move_local_data = FixupMountMoveLocalData(coresys)

    await coresys.mounts.create_mount(Mount.from_dict(coresys, BACKUP_TEST_DATA))

    mount_dir = coresys.mounts.get("backup_test").local_where
    mount_dir.mkdir(parents=True, exist_ok=True)
    (mount_dir / "stranded_backup.tar").touch()

    coresys.resolution.create_issue(
        IssueType.MOUNT_FAILED,
        ContextType.MOUNT,
        reference="backup_test",
        suggestions=[
            SuggestionType.MOVE_LOCAL_DATA,
            SuggestionType.EXECUTE_RELOAD,
            SuggestionType.EXECUTE_REMOVE,
        ],
    )

    await mount_move_local_data()

    recovery_dir = coresys.config.path_backup / "backup_test_local_recovery"
    assert (recovery_dir / "stranded_backup.tar").exists()
    assert mount_dir.is_dir()
    assert not any(mount_dir.iterdir())
    assert coresys.resolution.issues == []
    assert coresys.resolution.suggestions == []


async def test_fixup_failed_remount_drops_move_suggestion(
    coresys: CoreSys,
    all_dbus_services: dict[str, DBusServiceMock],
    tmp_supervisor_data,
    path_extern,
    mount_propagation,
    mock_is_mount,
):
    """Test a failed remount after moving keeps the issue without move suggestion.

    Once the data was moved aside, moving it again cannot help — only the
    reload and remove suggestions still apply to the remaining failure.
    """
    mount_move_local_data = FixupMountMoveLocalData(coresys)

    await coresys.mounts.create_mount(Mount.from_dict(coresys, MEDIA_TEST_DATA))

    media_dir = coresys.config.path_media / "media_test"
    media_dir.mkdir(exist_ok=True)
    (media_dir / "recording.mp4").touch()

    coresys.resolution.create_issue(
        IssueType.MOUNT_FAILED,
        ContextType.MOUNT,
        reference="media_test",
        suggestions=[
            SuggestionType.MOVE_LOCAL_DATA,
            SuggestionType.EXECUTE_RELOAD,
            SuggestionType.EXECUTE_REMOVE,
        ],
    )

    with patch.object(
        MountManager, "reload_mount", side_effect=MountError("Test remount failure")
    ):
        await mount_move_local_data()

    recovery_dir = coresys.config.path_media / "media_test_local_recovery"
    assert (recovery_dir / "recording.mp4").exists()
    assert len(coresys.resolution.issues) == 1
    assert {suggestion.type for suggestion in coresys.resolution.suggestions} == {
        SuggestionType.EXECUTE_RELOAD,
        SuggestionType.EXECUTE_REMOVE,
    }


async def test_fixup_failure_keeps_suggestion(
    coresys: CoreSys,
    all_dbus_services: dict[str, DBusServiceMock],
    tmp_supervisor_data,
    path_extern,
    mount_propagation,
    mock_is_mount,
):
    """Test failing to relocate keeps the issue and suggestion for retry."""
    mount_move_local_data = FixupMountMoveLocalData(coresys)

    await coresys.mounts.create_mount(Mount.from_dict(coresys, MEDIA_TEST_DATA))

    coresys.resolution.create_issue(
        IssueType.MOUNT_FAILED,
        ContextType.MOUNT,
        reference="media_test",
        suggestions=[
            SuggestionType.MOVE_LOCAL_DATA,
            SuggestionType.EXECUTE_RELOAD,
            SuggestionType.EXECUTE_REMOVE,
        ],
    )

    with patch.object(
        MountManager, "relocate_local_data", side_effect=MountError("fail")
    ):
        await mount_move_local_data()

    assert len(coresys.resolution.issues) == 1
    assert len(coresys.resolution.suggestions) == 3


async def test_fixup_missing_mount(
    coresys: CoreSys,
    all_dbus_services: dict[str, DBusServiceMock],
    tmp_supervisor_data,
    path_extern,
    mount_propagation,
    mock_is_mount,
):
    """Test fixup dismisses the issue if the mount no longer exists."""
    mount_move_local_data = FixupMountMoveLocalData(coresys)

    await coresys.mounts.load()

    coresys.resolution.create_issue(
        IssueType.MOUNT_FAILED,
        ContextType.MOUNT,
        reference="does_not_exist",
        suggestions=[
            SuggestionType.MOVE_LOCAL_DATA,
            SuggestionType.EXECUTE_RELOAD,
            SuggestionType.EXECUTE_REMOVE,
        ],
    )

    await mount_move_local_data()

    assert coresys.resolution.issues == []
    assert coresys.resolution.suggestions == []
