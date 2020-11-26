"""Test check."""
# pylint: disable=import-error, protected-access
from unittest.mock import AsyncMock, patch

from supervisor.const import CoreState
from supervisor.coresys import CoreSys
from supervisor.resolution.const import ContextType, SuggestionType
from supervisor.resolution.data import Suggestion


async def test_check_autofix(coresys: CoreSys):
    """Test check for setup."""
    coresys.core.state = CoreState.RUNNING

    coresys.resolution.fixup._create_full_snapshot.process_fixup = AsyncMock()

    with patch(
        "supervisor.resolution.fixups.create_full_snapshot.FixupCreateFullSnapshot.auto",
        return_value=True,
    ):
        await coresys.resolution.fixup.run_autofix()

    coresys.resolution.fixup._create_full_snapshot.process_fixup.assert_not_called()

    coresys.resolution.suggestions = Suggestion(
        SuggestionType.CREATE_FULL_SNAPSHOT, ContextType.SYSTEM
    )
    with patch(
        "supervisor.resolution.fixups.create_full_snapshot.FixupCreateFullSnapshot.auto",
        return_value=True,
    ):
        await coresys.resolution.fixup.run_autofix()

    coresys.resolution.fixup._create_full_snapshot.process_fixup.assert_called_once()
    assert len(coresys.resolution.suggestions) == 0
