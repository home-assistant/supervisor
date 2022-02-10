"""Test evaluation base."""
# pylint: disable=import-error,protected-access
from unittest.mock import AsyncMock, patch

from supervisor.coresys import CoreSys
from supervisor.resolution.const import ContextType, IssueType, SuggestionType
from supervisor.resolution.data import Issue, Suggestion
from supervisor.resolution.fixups.store_execute_reload import FixupStoreExecuteReload


async def test_fixup(coresys: CoreSys):
    """Test fixup."""
    store_execute_reload = FixupStoreExecuteReload(coresys)

    assert store_execute_reload.auto

    coresys.resolution.suggestions = Suggestion(
        SuggestionType.EXECUTE_RELOAD, ContextType.STORE, reference="test"
    )
    coresys.resolution.issues = Issue(
        IssueType.FATAL_ERROR, ContextType.STORE, reference="test"
    )

    mock_repositorie = AsyncMock()
    coresys.store.repositories["test"] = mock_repositorie

    with patch("shutil.disk_usage", return_value=(42, 42, 2 * (1024.0**3))):
        await store_execute_reload()

    assert mock_repositorie.load.called
    assert mock_repositorie.update.called
    assert len(coresys.resolution.suggestions) == 0
    assert len(coresys.resolution.issues) == 0
