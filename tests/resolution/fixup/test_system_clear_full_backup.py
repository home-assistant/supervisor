"""Test clear full backup fixup."""

# pylint: disable=import-error,protected-access
from supervisor.backups.backup import Backup
from supervisor.backups.const import BackupType
from supervisor.coresys import CoreSys
from supervisor.resolution.const import ContextType, SuggestionType
from supervisor.resolution.data import Suggestion
from supervisor.resolution.fixups.system_clear_full_backup import (
    FixupSystemClearFullBackup,
)


async def test_fixup(coresys: CoreSys, backups: list[Backup]):
    """Test fixup."""
    clear_full_backup = FixupSystemClearFullBackup(coresys)

    assert not clear_full_backup.auto

    coresys.resolution.add_suggestion(
        Suggestion(SuggestionType.CLEAR_FULL_BACKUP, ContextType.SYSTEM)
    )

    newest_full_backup = coresys.backups._backups["sn4"]

    assert newest_full_backup in coresys.backups.list_backups
    assert (
        len([x for x in coresys.backups.list_backups if x.sys_type == BackupType.FULL])
        == 3
    )

    await clear_full_backup()
    assert newest_full_backup in coresys.backups.list_backups
    assert (
        len([x for x in coresys.backups.list_backups if x.sys_type == BackupType.FULL])
        == 2
    )

    assert len(coresys.resolution.suggestions) == 0
