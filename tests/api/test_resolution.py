"""Test Resolution API."""
from unittest.mock import MagicMock, patch

import pytest

from supervisor.const import ATTR_ISSUES, ATTR_SUGGESTIONS, ATTR_UNSUPPORTED
from supervisor.coresys import CoreSys
from supervisor.exceptions import ResolutionError
from supervisor.resolution.const import (
    ContextType,
    IssueType,
    SuggestionType,
    UnsupportedReason,
)
from supervisor.resolution.data import Suggestion


@pytest.mark.asyncio
async def test_api_resolution_base(coresys: CoreSys, api_client):
    """Test resolution manager api."""
    coresys.resolution.unsupported = UnsupportedReason.OS
    coresys.resolution.suggestions = Suggestion(
        SuggestionType.CLEAR_FULL_SNAPSHOT, ContextType.SYSTEM
    )
    coresys.resolution.create_issue(IssueType.FREE_SPACE, ContextType.SYSTEM)

    resp = await api_client.get("/resolution")
    result = await resp.json()
    assert UnsupportedReason.OS in result["data"][ATTR_UNSUPPORTED]
    assert (
        SuggestionType.CLEAR_FULL_SNAPSHOT
        == result["data"][ATTR_SUGGESTIONS][-1]["type"]
    )
    assert IssueType.FREE_SPACE == result["data"][ATTR_ISSUES][-1]["type"]


@pytest.mark.asyncio
async def test_api_resolution_dismiss_suggestion(coresys: CoreSys, api_client):
    """Test resolution manager suggestion apply api."""
    coresys.resolution.suggestions = clear_snapshot = Suggestion(
        SuggestionType.CLEAR_FULL_SNAPSHOT, ContextType.SYSTEM
    )

    assert SuggestionType.CLEAR_FULL_SNAPSHOT == coresys.resolution.suggestions[-1].type
    await api_client.delete(f"/resolution/suggestion/{clear_snapshot.uuid}")
    assert clear_snapshot not in coresys.resolution.suggestions


@pytest.mark.asyncio
async def test_api_resolution_apply_suggestion(coresys: CoreSys, api_client):
    """Test resolution manager suggestion apply api."""
    coresys.resolution.suggestions = clear_snapshot = Suggestion(
        SuggestionType.CLEAR_FULL_SNAPSHOT, ContextType.SYSTEM
    )
    coresys.resolution.suggestions = create_snapshot = Suggestion(
        SuggestionType.CREATE_FULL_SNAPSHOT, ContextType.SYSTEM
    )

    with patch("supervisor.snapshots.SnapshotManager", return_value=MagicMock()):
        await api_client.post(f"/resolution/suggestion/{clear_snapshot.uuid}")
        await api_client.post(f"/resolution/suggestion/{create_snapshot.uuid}")

        assert clear_snapshot not in coresys.resolution.suggestions
        assert create_snapshot not in coresys.resolution.suggestions

    with pytest.raises(ResolutionError):
        await coresys.resolution.apply_suggestion(clear_snapshot)
