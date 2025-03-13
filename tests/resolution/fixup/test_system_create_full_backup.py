"""Test create full backup fixup."""

# pylint: disable=import-error,protected-access
from unittest.mock import AsyncMock

from supervisor.coresys import CoreSys
from supervisor.resolution.const import ContextType, SuggestionType
from supervisor.resolution.data import Suggestion
from supervisor.resolution.fixups.system_create_full_backup import (
    FixupSystemCreateFullBackup,
)


async def test_fixup(coresys: CoreSys):
    """Test fixup."""
    create_full_backup = FixupSystemCreateFullBackup(coresys)

    assert not create_full_backup.auto

    coresys.resolution.add_suggestion(
        Suggestion(SuggestionType.CREATE_FULL_BACKUP, ContextType.SYSTEM)
    )

    mock_backups = AsyncMock()
    coresys.backups.do_backup_full = mock_backups

    await create_full_backup()

    mock_backups.assert_called()
    assert len(coresys.resolution.suggestions) == 0
