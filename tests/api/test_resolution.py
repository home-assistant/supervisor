"""Test Resolution API."""
from unittest.mock import AsyncMock

import pytest

from supervisor.const import (
    ATTR_ISSUES,
    ATTR_SUGGESTIONS,
    ATTR_UNHEALTHY,
    ATTR_UNSUPPORTED,
    CoreState,
)
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


@pytest.mark.asyncio
async def test_api_resolution_base(coresys: CoreSys, api_client):
    """Test resolution manager api."""
    coresys.resolution.unsupported = UnsupportedReason.OS
    coresys.resolution.suggestions = Suggestion(
        SuggestionType.CLEAR_FULL_BACKUP, ContextType.SYSTEM
    )
    coresys.resolution.create_issue(IssueType.FREE_SPACE, ContextType.SYSTEM)

    resp = await api_client.get("/resolution/info")
    result = await resp.json()
    assert UnsupportedReason.OS in result["data"][ATTR_UNSUPPORTED]
    assert (
        SuggestionType.CLEAR_FULL_BACKUP == result["data"][ATTR_SUGGESTIONS][-1]["type"]
    )
    assert IssueType.FREE_SPACE == result["data"][ATTR_ISSUES][-1]["type"]


@pytest.mark.asyncio
async def test_api_resolution_dismiss_suggestion(coresys: CoreSys, api_client):
    """Test resolution manager suggestion apply api."""
    coresys.resolution.suggestions = clear_backup = Suggestion(
        SuggestionType.CLEAR_FULL_BACKUP, ContextType.SYSTEM
    )

    assert SuggestionType.CLEAR_FULL_BACKUP == coresys.resolution.suggestions[-1].type
    await api_client.delete(f"/resolution/suggestion/{clear_backup.uuid}")
    assert clear_backup not in coresys.resolution.suggestions


@pytest.mark.asyncio
async def test_api_resolution_apply_suggestion(coresys: CoreSys, api_client):
    """Test resolution manager suggestion apply api."""
    coresys.resolution.suggestions = clear_backup = Suggestion(
        SuggestionType.CLEAR_FULL_BACKUP, ContextType.SYSTEM
    )
    coresys.resolution.suggestions = create_backup = Suggestion(
        SuggestionType.CREATE_FULL_BACKUP, ContextType.SYSTEM
    )

    mock_backups = AsyncMock()
    mock_health = AsyncMock()
    coresys.backups.do_backup_full = mock_backups
    coresys.resolution.healthcheck = mock_health

    await api_client.post(f"/resolution/suggestion/{clear_backup.uuid}")
    await api_client.post(f"/resolution/suggestion/{create_backup.uuid}")

    assert clear_backup not in coresys.resolution.suggestions
    assert create_backup not in coresys.resolution.suggestions

    assert mock_backups.called
    assert mock_health.called

    with pytest.raises(ResolutionError):
        await coresys.resolution.apply_suggestion(clear_backup)


@pytest.mark.asyncio
async def test_api_resolution_dismiss_issue(coresys: CoreSys, api_client):
    """Test resolution manager issue apply api."""
    coresys.resolution.issues = updated_failed = Issue(
        IssueType.UPDATE_FAILED, ContextType.SYSTEM
    )

    assert IssueType.UPDATE_FAILED == coresys.resolution.issues[-1].type
    await api_client.delete(f"/resolution/issue/{updated_failed.uuid}")
    assert updated_failed not in coresys.resolution.issues


@pytest.mark.asyncio
async def test_api_resolution_unhealthy(coresys: CoreSys, api_client):
    """Test resolution manager api."""
    coresys.resolution.unhealthy = UnhealthyReason.DOCKER

    resp = await api_client.get("/resolution/info")
    result = await resp.json()
    assert UnhealthyReason.DOCKER == result["data"][ATTR_UNHEALTHY][-1]


@pytest.mark.asyncio
async def test_api_resolution_check_options(coresys: CoreSys, api_client):
    """Test client API with checks options."""
    free_space = coresys.resolution.check.get("free_space")

    assert free_space.enabled
    await api_client.post(
        f"/resolution/check/{free_space.slug}/options", json={"enabled": False}
    )
    assert not free_space.enabled

    await api_client.post(
        f"/resolution/check/{free_space.slug}/options", json={"enabled": True}
    )
    assert free_space.enabled


@pytest.mark.asyncio
async def test_api_resolution_check_run(coresys: CoreSys, api_client):
    """Test client API with run check."""
    coresys.core.state = CoreState.RUNNING
    free_space = coresys.resolution.check.get("free_space")

    free_space.run_check = AsyncMock()

    await api_client.post(f"/resolution/check/{free_space.slug}/run")

    assert free_space.run_check.called


async def test_api_resolution_suggestions_for_issue(coresys: CoreSys, api_client):
    """Test getting suggestions that fix an issue."""
    coresys.resolution.issues = corrupt_repo = Issue(
        IssueType.CORRUPT_REPOSITORY, ContextType.STORE, "repo_1"
    )

    resp = await api_client.get(f"/resolution/issue/{corrupt_repo.uuid}/suggestions")
    result = await resp.json()

    assert result["data"]["suggestions"] == []

    coresys.resolution.suggestions = execute_reset = Suggestion(
        SuggestionType.EXECUTE_RESET, ContextType.STORE, "repo_1"
    )
    coresys.resolution.suggestions = execute_remove = Suggestion(
        SuggestionType.EXECUTE_REMOVE, ContextType.STORE, "repo_1"
    )

    resp = await api_client.get(f"/resolution/issue/{corrupt_repo.uuid}/suggestions")
    result = await resp.json()

    suggestion = [
        su for su in result["data"]["suggestions"] if su["uuid"] == execute_reset.uuid
    ]
    assert len(suggestion) == 1
    assert suggestion[0]["auto"] is True

    suggestion = [
        su for su in result["data"]["suggestions"] if su["uuid"] == execute_remove.uuid
    ]
    assert len(suggestion) == 1
    assert suggestion[0]["auto"] is False
