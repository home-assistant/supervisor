"""Test evaluation base."""

# pylint: disable=import-error,protected-access
import asyncio
from unittest.mock import AsyncMock, patch

import pytest

from supervisor.const import BusEvent
from supervisor.coresys import CoreSys
from supervisor.exceptions import ResolutionFixupError
from supervisor.resolution.const import ContextType, IssueType, SuggestionType
from supervisor.resolution.data import Issue, Suggestion
from supervisor.resolution.fixups.store_execute_reload import FixupStoreExecuteReload


async def test_fixup(coresys: CoreSys, supervisor_internet):
    """Test fixup."""
    store_execute_reload = FixupStoreExecuteReload(coresys)

    assert store_execute_reload.auto

    coresys.resolution.add_suggestion(
        Suggestion(SuggestionType.EXECUTE_RELOAD, ContextType.STORE, reference="test")
    )
    coresys.resolution.add_issue(
        Issue(IssueType.FATAL_ERROR, ContextType.STORE, reference="test")
    )

    mock_repositorie = AsyncMock()
    coresys.store.repositories["test"] = mock_repositorie

    with patch("shutil.disk_usage", return_value=(42, 42, 2 * (1024.0**3))):
        await store_execute_reload()

    assert mock_repositorie.load.called
    assert mock_repositorie.update.called
    assert len(coresys.resolution.suggestions) == 0
    assert len(coresys.resolution.issues) == 0


@pytest.mark.usefixtures("supervisor_internet")
async def test_store_execute_reload_runs_on_connectivity_true(coresys: CoreSys):
    """Test fixup runs when connectivity goes from false to true."""
    coresys.hardware.disk.get_disk_free_space = lambda x: 5000
    coresys.supervisor.connectivity = False
    await asyncio.sleep(0)

    mock_repository = AsyncMock()
    coresys.store.repositories["test_store"] = mock_repository
    coresys.resolution.add_issue(
        Issue(
            IssueType.FATAL_ERROR,
            ContextType.STORE,
            reference="test_store",
        ),
        suggestions=[SuggestionType.EXECUTE_RELOAD],
    )

    with patch.object(coresys.store, "reload") as mock_reload:
        # Fire event with connectivity True
        coresys.supervisor.connectivity = True
        await asyncio.sleep(0.1)

        mock_repository.load.assert_called_once()
        mock_reload.assert_awaited_once_with(mock_repository)


@pytest.mark.usefixtures("supervisor_internet")
async def test_store_execute_reload_does_not_run_on_connectivity_false(
    coresys: CoreSys,
):
    """Test fixup does not run when connectivity goes from true to false."""
    coresys.hardware.disk.get_disk_free_space = lambda x: 5000
    coresys.supervisor.connectivity = True
    await asyncio.sleep(0)

    mock_repository = AsyncMock()
    coresys.store.repositories["test_store"] = mock_repository
    coresys.resolution.add_issue(
        Issue(
            IssueType.FATAL_ERROR,
            ContextType.STORE,
            reference="test_store",
        ),
        suggestions=[SuggestionType.EXECUTE_RELOAD],
    )

    # Fire event with connectivity True
    coresys.supervisor.connectivity = False
    await asyncio.sleep(0.1)

    mock_repository.load.assert_not_called()


@pytest.mark.usefixtures("supervisor_internet")
async def test_store_execute_reload_dismiss_suggestion_removes_listener(
    coresys: CoreSys,
):
    """Test fixup does not run on event if suggestion has been dismissed."""
    coresys.hardware.disk.get_disk_free_space = lambda x: 5000
    coresys.supervisor.connectivity = True
    await asyncio.sleep(0)

    mock_repository = AsyncMock()
    coresys.store.repositories["test_store"] = mock_repository
    coresys.resolution.add_issue(
        issue := Issue(
            IssueType.FATAL_ERROR,
            ContextType.STORE,
            reference="test_store",
        ),
        suggestions=[SuggestionType.EXECUTE_RELOAD],
    )

    with patch.object(
        FixupStoreExecuteReload, "process_fixup", side_effect=ResolutionFixupError
    ) as mock_fixup:
        # Fire event with issue there to trigger fixup
        coresys.bus.fire_event(BusEvent.SUPERVISOR_CONNECTIVITY_CHANGE, True)
        await asyncio.sleep(0.1)
        mock_fixup.assert_called_once()

        # Remove issue and suggestion and re-fire to see listener is gone
        mock_fixup.reset_mock()
        coresys.resolution.dismiss_issue(issue)

        coresys.bus.fire_event(BusEvent.SUPERVISOR_CONNECTIVITY_CHANGE, True)
        await asyncio.sleep(0.1)
        mock_fixup.assert_not_called()
