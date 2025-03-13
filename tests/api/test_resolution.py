"""Test Resolution API."""

from unittest.mock import AsyncMock

from aiohttp.test_utils import TestClient
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
async def test_api_resolution_base(coresys: CoreSys, api_client: TestClient):
    """Test resolution manager api."""
    coresys.resolution.add_unsupported_reason(UnsupportedReason.OS)
    coresys.resolution.add_suggestion(
        Suggestion(SuggestionType.CLEAR_FULL_BACKUP, ContextType.SYSTEM)
    )
    coresys.resolution.create_issue(IssueType.FREE_SPACE, ContextType.SYSTEM)

    resp = await api_client.get("/resolution/info")
    result = await resp.json()
    assert UnsupportedReason.OS in result["data"][ATTR_UNSUPPORTED]
    assert (
        result["data"][ATTR_SUGGESTIONS][-1]["type"] == SuggestionType.CLEAR_FULL_BACKUP
    )
    assert result["data"][ATTR_ISSUES][-1]["type"] == IssueType.FREE_SPACE


@pytest.mark.asyncio
async def test_api_resolution_dismiss_suggestion(
    coresys: CoreSys, api_client: TestClient
):
    """Test resolution manager suggestion apply api."""
    coresys.resolution.add_suggestion(
        clear_backup := Suggestion(SuggestionType.CLEAR_FULL_BACKUP, ContextType.SYSTEM)
    )

    assert coresys.resolution.suggestions[-1].type == SuggestionType.CLEAR_FULL_BACKUP
    await api_client.delete(f"/resolution/suggestion/{clear_backup.uuid}")
    assert clear_backup not in coresys.resolution.suggestions


@pytest.mark.asyncio
async def test_api_resolution_apply_suggestion(
    coresys: CoreSys, api_client: TestClient
):
    """Test resolution manager suggestion apply api."""
    coresys.resolution.add_suggestion(
        clear_backup := Suggestion(SuggestionType.CLEAR_FULL_BACKUP, ContextType.SYSTEM)
    )
    coresys.resolution.add_suggestion(
        create_backup := Suggestion(
            SuggestionType.CREATE_FULL_BACKUP, ContextType.SYSTEM
        )
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
async def test_api_resolution_dismiss_issue(coresys: CoreSys, api_client: TestClient):
    """Test resolution manager issue apply api."""
    coresys.resolution.add_issue(
        updated_failed := Issue(IssueType.UPDATE_FAILED, ContextType.SYSTEM)
    )

    assert coresys.resolution.issues[-1].type == IssueType.UPDATE_FAILED
    await api_client.delete(f"/resolution/issue/{updated_failed.uuid}")
    assert updated_failed not in coresys.resolution.issues


@pytest.mark.asyncio
async def test_api_resolution_unhealthy(coresys: CoreSys, api_client: TestClient):
    """Test resolution manager api."""
    coresys.resolution.add_unhealthy_reason(UnhealthyReason.DOCKER)

    resp = await api_client.get("/resolution/info")
    result = await resp.json()
    assert result["data"][ATTR_UNHEALTHY][-1] == UnhealthyReason.DOCKER


@pytest.mark.asyncio
async def test_api_resolution_check_options(coresys: CoreSys, api_client: TestClient):
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
async def test_api_resolution_check_run(coresys: CoreSys, api_client: TestClient):
    """Test client API with run check."""
    await coresys.core.set_state(CoreState.RUNNING)
    free_space = coresys.resolution.check.get("free_space")

    free_space.run_check = AsyncMock()

    await api_client.post(f"/resolution/check/{free_space.slug}/run")

    assert free_space.run_check.called


async def test_api_resolution_suggestions_for_issue(
    coresys: CoreSys, api_client: TestClient
):
    """Test getting suggestions that fix an issue."""
    coresys.resolution.add_issue(
        corrupt_repo := Issue(IssueType.CORRUPT_REPOSITORY, ContextType.STORE, "repo_1")
    )

    resp = await api_client.get(f"/resolution/issue/{corrupt_repo.uuid}/suggestions")
    result = await resp.json()

    assert result["data"]["suggestions"] == []

    coresys.resolution.add_suggestion(
        execute_reset := Suggestion(
            SuggestionType.EXECUTE_RESET, ContextType.STORE, "repo_1"
        )
    )
    coresys.resolution.add_suggestion(
        execute_remove := Suggestion(
            SuggestionType.EXECUTE_REMOVE, ContextType.STORE, "repo_1"
        )
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


@pytest.mark.parametrize(
    ("method", "url"),
    [("delete", "/resolution/issue/bad"), ("get", "/resolution/issue/bad/suggestions")],
)
async def test_issue_not_found(api_client: TestClient, method: str, url: str):
    """Test issue not found error."""
    resp = await api_client.request(method, url)
    assert resp.status == 404
    body = await resp.json()
    assert body["message"] == "The supplied UUID is not a valid issue"


@pytest.mark.parametrize(
    ("method", "url"),
    [("delete", "/resolution/suggestion/bad"), ("post", "/resolution/suggestion/bad")],
)
async def test_suggestion_not_found(api_client: TestClient, method: str, url: str):
    """Test suggestion not found error."""
    resp = await api_client.request(method, url)
    assert resp.status == 404
    body = await resp.json()
    assert body["message"] == "The supplied UUID is not a valid suggestion"


@pytest.mark.parametrize(
    ("method", "url"),
    [("post", "/resolution/check/bad/options"), ("post", "/resolution/check/bad/run")],
)
async def test_check_not_found(api_client: TestClient, method: str, url: str):
    """Test check not found error."""
    resp = await api_client.request(method, url)
    assert resp.status == 404
    body = await resp.json()
    assert body["message"] == "The supplied check slug is not available"
