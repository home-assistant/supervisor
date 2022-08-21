"""Test clear full backup fixup."""
# pylint: disable=import-error,protected-access
import pytest

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

    coresys.resolution.suggestions = Suggestion(
        SuggestionType.CLEAR_FULL_BACKUP, ContextType.SYSTEM
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


@pytest.mark.parametrize("backups", [10], indirect=True)
async def test_increased_max_full_backups(coresys: CoreSys, backups: list[Backup]):
    """Test fixup with increased max full backups."""
    clear_full_backup = FixupSystemClearFullBackup(coresys)

    coresys.backups.max_full_backups = 5
    coresys.resolution.suggestions = Suggestion(
        SuggestionType.CLEAR_FULL_BACKUP, ContextType.SYSTEM
    )

    assert (
        len([x for x in coresys.backups.list_backups if x.sys_type == BackupType.FULL])
        == 8
    )

    await clear_full_backup()
    assert (
        len([x for x in coresys.backups.list_backups if x.sys_type == BackupType.FULL])
        == 5
    )
    assert len(coresys.resolution.suggestions) == 0


async def test_fixup_auto_backup(coresys: CoreSys):
    """Test fixup is auto when auto backup enabled."""
    coresys.backups.auto_backup = True

    clear_full_backup = FixupSystemClearFullBackup(coresys)
    assert clear_full_backup.auto is True
