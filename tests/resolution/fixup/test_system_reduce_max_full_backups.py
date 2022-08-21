"""Test reduce max full backups fixup."""
from supervisor.backups.backup import Backup
from supervisor.backups.const import BackupType
from supervisor.coresys import CoreSys
from supervisor.resolution.const import ContextType, SuggestionType
from supervisor.resolution.data import Suggestion
from supervisor.resolution.fixups.reduce_max_full_backups import (
    FixupReduceMaxFullBackups,
)


async def test_fixup(coresys: CoreSys, backups: list[Backup]):
    """Test fixup."""
    reduce_max_full_backups = FixupReduceMaxFullBackups(coresys)

    assert reduce_max_full_backups.auto is False

    coresys.backups.max_full_backups = 5
    coresys.resolution.suggestions = Suggestion(
        SuggestionType.REDUCE_MAX_FULL_BACKUPS, ContextType.SYSTEM
    )

    await reduce_max_full_backups()

    assert coresys.backups.max_full_backups == 2
    assert (
        len([x for x in coresys.backups.list_backups if x.sys_type == BackupType.FULL])
        == 2
    )

    assert len(coresys.resolution.suggestions) == 0
