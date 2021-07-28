"""Test evaluation base."""
# pylint: disable=import-error,protected-access
from pathlib import Path

from supervisor.backups.backup import Backup
from supervisor.backups.const import BackupType
from supervisor.const import ATTR_DATE, ATTR_SLUG, ATTR_TYPE
from supervisor.coresys import CoreSys
from supervisor.resolution.const import ContextType, SuggestionType
from supervisor.resolution.data import Suggestion
from supervisor.resolution.fixups.clear_full_backup import FixupClearFullBackup
from supervisor.utils.dt import utcnow
from supervisor.utils.tar import SecureTarFile


async def test_fixup(coresys: CoreSys, tmp_path):
    """Test fixup."""
    clear_full_backup = FixupClearFullBackup(coresys)

    assert not clear_full_backup.auto

    coresys.resolution.suggestions = Suggestion(
        SuggestionType.CLEAR_FULL_BACKUP, ContextType.SYSTEM
    )

    for slug in ["sn1", "sn2", "sn3", "sn4", "sn5"]:
        temp_tar = Path(tmp_path, f"{slug}.tar")
        with SecureTarFile(temp_tar, "w"):
            pass
        backup = Backup(coresys, temp_tar)
        backup._data = {  # pylint: disable=protected-access
            ATTR_SLUG: slug,
            ATTR_DATE: utcnow().isoformat(),
            ATTR_TYPE: BackupType.PARTIAL
            if "1" in slug or "5" in slug
            else BackupType.FULL,
        }
        coresys.backups._backups[backup.slug] = backup

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
        == 1
    )

    assert len(coresys.resolution.suggestions) == 0
