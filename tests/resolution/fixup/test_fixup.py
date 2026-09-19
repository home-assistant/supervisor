"""Test check."""

# pylint: disable=import-error, protected-access
from unittest.mock import AsyncMock, PropertyMock, patch

from supervisor.const import CoreState
from supervisor.coresys import CoreSys
from supervisor.exceptions import HassioError
from supervisor.resolution.const import ContextType, SuggestionType
from supervisor.resolution.data import Suggestion
from supervisor.resolution.fixup import ResolutionFixup
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


async def test_autofix_error_handling(coresys: CoreSys):
    """Test autofix continues on errors and only captures unexpected ones."""
    await coresys.core.set_state(CoreState.RUNNING)

    fix_hassio_error = AsyncMock(side_effect=HassioError("fail"))
    fix_hassio_error.auto = True
    fix_hassio_error.suggestion = SuggestionType.EXECUTE_RELOAD

    unexpected = RuntimeError("boom")
    fix_unexpected_error = AsyncMock(side_effect=unexpected)
    fix_unexpected_error.auto = True
    fix_unexpected_error.suggestion = SuggestionType.EXECUTE_RESET

    with (
        patch.object(
            ResolutionFixup,
            "all_fixes",
            new_callable=PropertyMock,
            return_value=[fix_hassio_error, fix_unexpected_error],
        ),
        patch(
            "supervisor.resolution.fixup.async_capture_exception",
            new_callable=AsyncMock,
        ) as capture,
    ):
        await coresys.resolution.fixup.run_autofix()

    # The HassioError did not abort the loop, the next fixup still ran
    fix_hassio_error.assert_awaited_once()
    fix_unexpected_error.assert_awaited_once()

    # Only the unexpected error is reported to Sentry
    capture.assert_awaited_once_with(unexpected)


async def test_dynamic_fixup_loader(coresys: CoreSys):
    """Test dynamic fixup loader, this ensures that all fixups have defined a setup function."""
    for fixup in await coresys.run_in_executor(get_valid_modules, "fixups"):
        assert fixup in coresys.resolution.fixup._fixups
