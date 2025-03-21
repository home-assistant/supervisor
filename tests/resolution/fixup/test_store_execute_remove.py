"""Test evaluation base."""

# pylint: disable=import-error,protected-access
from unittest.mock import patch

from supervisor.coresys import CoreSys
from supervisor.resolution.const import ContextType, IssueType, SuggestionType
from supervisor.resolution.data import Issue, Suggestion
from supervisor.resolution.fixups.store_execute_remove import FixupStoreExecuteRemove
from supervisor.store.repository import Repository


async def test_fixup(coresys: CoreSys, repository: Repository):
    """Test fixup."""
    store_execute_remove = FixupStoreExecuteRemove(coresys)

    assert store_execute_remove.auto is False

    coresys.resolution.add_suggestion(
        Suggestion(
            SuggestionType.EXECUTE_REMOVE, ContextType.STORE, reference=repository.slug
        )
    )
    coresys.resolution.add_issue(
        Issue(
            IssueType.CORRUPT_REPOSITORY, ContextType.STORE, reference=repository.slug
        )
    )

    with patch.object(type(repository), "remove") as remove_repo:
        await store_execute_remove()

        assert remove_repo.called

    assert coresys.store.save_data.called
    assert len(coresys.resolution.suggestions) == 0
    assert len(coresys.resolution.issues) == 0

    assert repository.slug not in coresys.store.repositories
