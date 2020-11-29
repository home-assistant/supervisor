"""Test evaluation base."""
# pylint: disable=import-error,protected-access
from unittest.mock import AsyncMock

from supervisor.coresys import CoreSys
from supervisor.resolution.const import ContextType, IssueType, SuggestionType
from supervisor.resolution.data import Issue, Suggestion
from supervisor.resolution.fixups.store_execute_remove import FixupStoreExecuteRemove


async def test_fixup(coresys: CoreSys):
    """Test fixup."""
    store_execute_remove = FixupStoreExecuteRemove(coresys)

    assert store_execute_remove.auto

    coresys.resolution.suggestions = Suggestion(
        SuggestionType.EXECUTE_REMOVE, ContextType.STORE, reference="test"
    )
    coresys.resolution.issues = Issue(
        IssueType.CORRUPT_REPOSITORY, ContextType.STORE, reference="test"
    )

    mock_repositorie = AsyncMock()
    mock_repositorie.slug = "test"

    coresys.store.repositories["test"] = mock_repositorie

    await store_execute_remove()

    assert mock_repositorie.remove.called
    assert coresys.config.save_data.called
    assert len(coresys.resolution.suggestions) == 0
    assert len(coresys.resolution.issues) == 0

    assert "test" not in coresys.store.repositories
