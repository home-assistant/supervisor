"""Test check."""

# pylint: disable=import-error, protected-access
from unittest.mock import AsyncMock, patch

from supervisor.const import CoreState
from supervisor.coresys import CoreSys
from supervisor.resolution.const import ContextType, SuggestionType
from supervisor.resolution.data import Suggestion
from supervisor.resolution.validate import get_valid_modules


async def test_check_autofix(coresys: CoreSys):
    """Test check for setup."""
    await coresys.core.set_state(CoreState.RUNNING)

    coresys.resolution.fixup._fixups[
        "system_create_full_backup"
    ].process_fixup = AsyncMock()

    with patch(
        "supervisor.resolution.fixups.system_create_full_backup.FixupSystemCreateFullBackup.auto",
        return_value=True,
    ):
        await coresys.resolution.fixup.run_autofix()

    coresys.resolution.fixup._fixups[
        "system_create_full_backup"
    ].process_fixup.assert_not_called()

    coresys.resolution.add_suggestion(
        Suggestion(SuggestionType.CREATE_FULL_BACKUP, ContextType.SYSTEM)
    )
    with patch(
        "supervisor.resolution.fixups.system_create_full_backup.FixupSystemCreateFullBackup.auto",
        return_value=True,
    ):
        await coresys.resolution.fixup.run_autofix()

    coresys.resolution.fixup._fixups[
        "system_create_full_backup"
    ].process_fixup.assert_called_once()
    assert len(coresys.resolution.suggestions) == 0


async def test_dynamic_fixup_loader(coresys: CoreSys):
    """Test dynamic fixup loader, this ensures that all fixups have defined a setup function."""
    for fixup in await coresys.run_in_executor(get_valid_modules, "fixups"):
        assert fixup in coresys.resolution.fixup._fixups
