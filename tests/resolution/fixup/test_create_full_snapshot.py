"""Test evaluation base."""
# pylint: disable=import-error,protected-access
from unittest.mock import AsyncMock

from supervisor.coresys import CoreSys
from supervisor.resolution.const import ContextType, SuggestionType
from supervisor.resolution.data import Suggestion
from supervisor.resolution.fixups.create_full_snapshot import FixupCreateFullSnapshot


async def test_fixup(coresys: CoreSys):
    """Test fixup."""
    create_full_snapshot = FixupCreateFullSnapshot(coresys)

    assert not create_full_snapshot.auto

    coresys.resolution.suggestions = Suggestion(
        SuggestionType.CREATE_FULL_SNAPSHOT, ContextType.SYSTEM
    )

    mock_snapshots = AsyncMock()
    coresys.snapshots.do_snapshot_full = mock_snapshots

    await create_full_snapshot()

    mock_snapshots.assert_called()
    assert len(coresys.resolution.suggestions) == 0
