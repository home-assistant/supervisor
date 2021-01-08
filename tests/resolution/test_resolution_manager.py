"""Tests for resolution manager."""
from unittest.mock import AsyncMock

import pytest

from supervisor.coresys import CoreSys
from supervisor.exceptions import ResolutionError
from supervisor.resolution.const import (
    ContextType,
    IssueType,
    SuggestionType,
    UnhealthyReason,
    UnsupportedReason,
)
from supervisor.resolution.data import Issue, Suggestion


def test_properies_unsupported(coresys: CoreSys):
    """Test resolution manager properties unsupported."""

    assert coresys.core.supported

    coresys.resolution.unsupported = UnsupportedReason.OS
    assert not coresys.core.supported


def test_properies_unhealthy(coresys: CoreSys):
    """Test resolution manager properties unhealthy."""

    assert coresys.core.healthy

    coresys.resolution.unhealthy = UnhealthyReason.SUPERVISOR
    assert not coresys.core.healthy


@pytest.mark.asyncio
async def test_resolution_dismiss_suggestion(coresys: CoreSys):
    """Test resolution manager suggestion apply api."""
    coresys.resolution.suggestions = clear_snapshot = Suggestion(
        SuggestionType.CLEAR_FULL_SNAPSHOT, ContextType.SYSTEM
    )

    assert SuggestionType.CLEAR_FULL_SNAPSHOT == coresys.resolution.suggestions[-1].type
    coresys.resolution.dismiss_suggestion(clear_snapshot)
    assert clear_snapshot not in coresys.resolution.suggestions

    with pytest.raises(ResolutionError):
        coresys.resolution.dismiss_suggestion(clear_snapshot)


@pytest.mark.asyncio
async def test_resolution_apply_suggestion(coresys: CoreSys):
    """Test resolution manager suggestion apply api."""
    coresys.resolution.suggestions = clear_snapshot = Suggestion(
        SuggestionType.CLEAR_FULL_SNAPSHOT, ContextType.SYSTEM
    )
    coresys.resolution.suggestions = create_snapshot = Suggestion(
        SuggestionType.CREATE_FULL_SNAPSHOT, ContextType.SYSTEM
    )

    mock_snapshots = AsyncMock()
    mock_health = AsyncMock()
    coresys.snapshots.do_snapshot_full = mock_snapshots
    coresys.resolution.healthcheck = mock_health

    await coresys.resolution.apply_suggestion(clear_snapshot)
    await coresys.resolution.apply_suggestion(create_snapshot)

    assert mock_snapshots.called
    assert mock_health.called

    assert clear_snapshot not in coresys.resolution.suggestions
    assert create_snapshot not in coresys.resolution.suggestions

    with pytest.raises(ResolutionError):
        await coresys.resolution.apply_suggestion(clear_snapshot)


@pytest.mark.asyncio
async def test_resolution_dismiss_issue(coresys: CoreSys):
    """Test resolution manager issue apply api."""
    coresys.resolution.issues = updated_failed = Issue(
        IssueType.UPDATE_FAILED, ContextType.SYSTEM
    )

    assert IssueType.UPDATE_FAILED == coresys.resolution.issues[-1].type
    coresys.resolution.dismiss_issue(updated_failed)
    assert updated_failed not in coresys.resolution.issues

    with pytest.raises(ResolutionError):
        coresys.resolution.dismiss_issue(updated_failed)


@pytest.mark.asyncio
async def test_resolution_create_issue_suggestion(coresys: CoreSys):
    """Test resolution manager issue and suggestion."""
    coresys.resolution.create_issue(
        IssueType.UPDATE_ROLLBACK,
        ContextType.CORE,
        "slug",
        [SuggestionType.EXECUTE_REPAIR],
    )

    assert IssueType.UPDATE_ROLLBACK == coresys.resolution.issues[-1].type
    assert ContextType.CORE == coresys.resolution.issues[-1].context
    assert coresys.resolution.issues[-1].reference == "slug"

    assert SuggestionType.EXECUTE_REPAIR == coresys.resolution.suggestions[-1].type
    assert ContextType.CORE == coresys.resolution.suggestions[-1].context


@pytest.mark.asyncio
async def test_resolution_dismiss_unsupported(coresys: CoreSys):
    """Test resolution manager dismiss unsupported reason."""
    coresys.resolution.unsupported = UnsupportedReason.CONTAINER

    coresys.resolution.dismiss_unsupported(UnsupportedReason.CONTAINER)
    assert UnsupportedReason.CONTAINER not in coresys.resolution.unsupported

    with pytest.raises(ResolutionError):
        coresys.resolution.dismiss_unsupported(UnsupportedReason.CONTAINER)
