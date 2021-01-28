"""Test evaluation base."""
# pylint: disable=import-error,protected-access
from pathlib import Path
from unittest.mock import AsyncMock, patch

from supervisor.coresys import CoreSys
from supervisor.resolution.const import ContextType, IssueType, SuggestionType
from supervisor.resolution.data import Issue, Suggestion
from supervisor.resolution.fixups.store_execute_reset import FixupStoreExecuteReset


async def test_fixup(coresys: CoreSys, tmp_path):
    """Test fixup."""
    store_execute_reset = FixupStoreExecuteReset(coresys)
    test_repo = Path(tmp_path, "test_repo")

    assert store_execute_reset.auto

    coresys.resolution.suggestions = Suggestion(
        SuggestionType.EXECUTE_RESET, ContextType.STORE, reference="test"
    )
    coresys.resolution.issues = Issue(
        IssueType.CORRUPT_REPOSITORY, ContextType.STORE, reference="test"
    )

    test_repo.mkdir()
    assert test_repo.exists()

    mock_repositorie = AsyncMock()
    mock_repositorie.git.path = test_repo
    coresys.store.repositories["test"] = mock_repositorie

    with patch("shutil.disk_usage", return_value=(42, 42, 2 * (1024.0 ** 3))):
        await store_execute_reset()

    assert not test_repo.exists()
    assert mock_repositorie.load.called
    assert len(coresys.resolution.suggestions) == 0
    assert len(coresys.resolution.issues) == 0
