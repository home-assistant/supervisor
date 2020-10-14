"""Test Resolution API."""
from unittest.mock import MagicMock, patch

import pytest

from supervisor.const import ATTR_ISSUES, ATTR_SUGGESTIONS, ATTR_UNSUPPORTED
from supervisor.coresys import CoreSys
from supervisor.resolution.const import IssueType, Suggestion, UnsupportedReason


@pytest.mark.asyncio
async def test_api_resolution_base(coresys: CoreSys, api_client):
    """Test resolution manager api."""
    coresys.resolution.unsupported = UnsupportedReason.OS
    coresys.resolution.suggestions = Suggestion.CLEAR_FULL_SNAPSHOT
    coresys.resolution.issues = IssueType.FREE_SPACE
    resp = await api_client.get("/resolution")
    result = await resp.json()
    assert UnsupportedReason.OS in result["data"][ATTR_UNSUPPORTED]
    assert Suggestion.CLEAR_FULL_SNAPSHOT in result["data"][ATTR_SUGGESTIONS]
    assert IssueType.FREE_SPACE in result["data"][ATTR_ISSUES]


@pytest.mark.asyncio
async def test_api_resolution_dismiss_suggestion(coresys: CoreSys, api_client):
    """Test resolution manager suggestion apply api."""
    coresys.resolution.suggestions = Suggestion.CLEAR_FULL_SNAPSHOT

    assert Suggestion.CLEAR_FULL_SNAPSHOT in coresys.resolution.suggestions
    await coresys.resolution.dismiss_suggestion(Suggestion.CLEAR_FULL_SNAPSHOT)
    assert Suggestion.CLEAR_FULL_SNAPSHOT not in coresys.resolution.suggestions


@pytest.mark.asyncio
async def test_api_resolution_apply_suggestion(coresys: CoreSys, api_client):
    """Test resolution manager suggestion apply api."""
    coresys.resolution.suggestions = Suggestion.CLEAR_FULL_SNAPSHOT
    coresys.resolution.suggestions = Suggestion.CREATE_FULL_SNAPSHOT

    with patch("supervisor.snapshots.SnapshotManager", return_value=MagicMock()):
        await coresys.resolution.apply_suggestion(Suggestion.CLEAR_FULL_SNAPSHOT)
        await coresys.resolution.apply_suggestion(Suggestion.CREATE_FULL_SNAPSHOT)

        assert Suggestion.CLEAR_FULL_SNAPSHOT not in coresys.resolution.suggestions
        assert Suggestion.CREATE_FULL_SNAPSHOT not in coresys.resolution.suggestions

    await coresys.resolution.apply_suggestion(Suggestion.CLEAR_FULL_SNAPSHOT)
