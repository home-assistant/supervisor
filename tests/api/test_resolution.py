"""Test Resolution API."""

import asyncio
from http import HTTPStatus
from unittest.mock import AsyncMock

from aiohttp.test_utils import TestClient
import pytest

from supervisor.const import (
    ATTR_ISSUES,
    ATTR_SUGGESTIONS,
    ATTR_UNHEALTHY,
    ATTR_UNSUPPORTED,
    CoreState,
    FeatureFlag,
)
from supervisor.coresys import CoreSys
from supervisor.exceptions import ResolutionError
from supervisor.homeassistant.const import WSType
from supervisor.resolution.const import (
    ContextType,
    IssueType,
    SuggestionType,
    UnhealthyReason,
    UnsupportedReason,
)
from supervisor.resolution.data import Issue, Suggestion


async def test_api_resolution_base(
    coresys: CoreSys, api_client_with_prefix: tuple[TestClient, str]
):
    """Test resolution manager api."""
    api_client, prefix = api_client_with_prefix
    coresys.resolution.add_unsupported_reason(UnsupportedReason.OS)
    coresys.resolution.add_suggestion(
        Suggestion(SuggestionType.CLEAR_FULL_BACKUP, ContextType.SYSTEM)
    )
    coresys.resolution.create_issue(IssueType.FREE_SPACE, ContextType.SYSTEM)

    resp = await api_client.get(f"{prefix}/resolution/info")
    result = await resp.json()
    assert UnsupportedReason.OS in result["data"][ATTR_UNSUPPORTED]
    assert (
        result["data"][ATTR_SUGGESTIONS][-1]["type"] == SuggestionType.CLEAR_FULL_BACKUP
    )
    assert result["data"][ATTR_ISSUES][-1]["type"] == IssueType.FREE_SPACE


async def test_api_resolution_dismiss_suggestion(
    coresys: CoreSys, api_client_with_prefix: tuple[TestClient, str]
):
    """Test resolution manager dismiss suggestion api."""
    api_client, prefix = api_client_with_prefix
    coresys.resolution.add_suggestion(
        clear_backup := Suggestion(SuggestionType.CLEAR_FULL_BACKUP, ContextType.SYSTEM)
    )

    assert coresys.resolution.suggestions[-1].type == SuggestionType.CLEAR_FULL_BACKUP
    await api_client.delete(f"{prefix}/resolution/suggestion/{clear_backup.uuid}")
    assert clear_backup not in coresys.resolution.suggestions


async def test_api_resolution_apply_suggestion(
    coresys: CoreSys, api_client_with_prefix: tuple[TestClient, str]
):
    """Test resolution manager suggestion apply api."""
    api_client, prefix = api_client_with_prefix
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

    await api_client.post(f"{prefix}/resolution/suggestion/{clear_backup.uuid}")
    await api_client.post(f"{prefix}/resolution/suggestion/{create_backup.uuid}")

    assert clear_backup not in coresys.resolution.suggestions
    assert create_backup not in coresys.resolution.suggestions

    assert mock_backups.called
    assert mock_health.called

    with pytest.raises(ResolutionError):
        await coresys.resolution.apply_suggestion(clear_backup)


async def test_api_resolution_dismiss_issue(
    coresys: CoreSys, api_client_with_prefix: tuple[TestClient, str]
):
    """Test resolution manager issue apply api."""
    api_client, prefix = api_client_with_prefix
    coresys.resolution.add_issue(
        updated_failed := Issue(IssueType.UPDATE_FAILED, ContextType.SYSTEM)
    )

    assert coresys.resolution.issues[-1].type == IssueType.UPDATE_FAILED
    await api_client.delete(f"{prefix}/resolution/issue/{updated_failed.uuid}")
    assert updated_failed not in coresys.resolution.issues


async def test_api_resolution_unhealthy(
    coresys: CoreSys, api_client_with_prefix: tuple[TestClient, str]
):
    """Test resolution manager api."""
    api_client, prefix = api_client_with_prefix
    coresys.resolution.add_unhealthy_reason(UnhealthyReason.DOCKER)

    resp = await api_client.get(f"{prefix}/resolution/info")
    result = await resp.json()
    assert result["data"][ATTR_UNHEALTHY][-1] == UnhealthyReason.DOCKER


async def test_api_resolution_check_options(
    coresys: CoreSys, api_client_with_prefix: tuple[TestClient, str]
):
    """Test client API with checks options."""
    api_client, prefix = api_client_with_prefix
    free_space = coresys.resolution.check.get("free_space")

    assert free_space.enabled
    await api_client.post(
        f"{prefix}/resolution/check/{free_space.slug}/options", json={"enabled": False}
    )
    assert not free_space.enabled

    await api_client.post(
        f"{prefix}/resolution/check/{free_space.slug}/options", json={"enabled": True}
    )
    assert free_space.enabled


async def test_api_resolution_check_run(
    coresys: CoreSys, api_client_with_prefix: tuple[TestClient, str]
):
    """Test client API with run check."""
    api_client, prefix = api_client_with_prefix
    await coresys.core.set_state(CoreState.RUNNING)
    free_space = coresys.resolution.check.get("free_space")

    free_space.run_check = AsyncMock()

    await api_client.post(f"{prefix}/resolution/check/{free_space.slug}/run")

    assert free_space.run_check.called


async def test_api_resolution_suggestions_for_issue(
    coresys: CoreSys, api_client_with_prefix: tuple[TestClient, str]
):
    """Test getting suggestions that fix an issue."""
    api_client, prefix = api_client_with_prefix
    coresys.resolution.add_issue(
        corrupt_repo := Issue(IssueType.CORRUPT_REPOSITORY, ContextType.STORE, "repo_1")
    )

    resp = await api_client.get(
        f"{prefix}/resolution/issue/{corrupt_repo.uuid}/suggestions"
    )
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

    resp = await api_client.get(
        f"{prefix}/resolution/issue/{corrupt_repo.uuid}/suggestions"
    )
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
async def test_issue_not_found(
    api_client_with_prefix: tuple[TestClient, str], method: str, url: str
):
    """Test issue not found error."""
    api_client, prefix = api_client_with_prefix
    resp = await api_client.request(method, f"{prefix}{url}")
    assert resp.status == 404
    body = await resp.json()
    assert body["message"] == "Issue bad does not exist"
    assert body["error_key"] == "resolution_issue_not_found_error"
    assert body["extra_fields"] == {"uuid": "bad"}


@pytest.mark.parametrize(
    ("method", "url"),
    [("delete", "/resolution/suggestion/bad"), ("post", "/resolution/suggestion/bad")],
)
async def test_suggestion_not_found(
    api_client_with_prefix: tuple[TestClient, str], method: str, url: str
):
    """Test suggestion not found error."""
    api_client, prefix = api_client_with_prefix
    resp = await api_client.request(method, f"{prefix}{url}")
    assert resp.status == 404
    body = await resp.json()
    assert body["message"] == "Suggestion bad does not exist"
    assert body["error_key"] == "resolution_suggestion_not_found_error"
    assert body["extra_fields"] == {"uuid": "bad"}


@pytest.mark.parametrize(
    ("method", "url"),
    [("post", "/resolution/check/bad/options"), ("post", "/resolution/check/bad/run")],
)
async def test_check_not_found(
    api_client_with_prefix: tuple[TestClient, str], method: str, url: str
):
    """Test check not found error."""
    api_client, prefix = api_client_with_prefix
    resp = await api_client.request(method, f"{prefix}{url}")
    assert resp.status == HTTPStatus.NOT_FOUND
    body = await resp.json()
    assert body["message"] == "Check 'bad' does not exist"
    assert body["error_key"] == "resolution_check_not_found_error"
    assert body["extra_fields"] == {"check": "bad"}


@pytest.mark.parametrize(
    ("issue_type", "legacy_issue_type"),
    [
        (IssueType.DEPRECATED_APP, "deprecated_addon"),
        (IssueType.DEPRECATED_ARCH_APP, "deprecated_arch_addon"),
        (IssueType.DETACHED_APP_MISSING, "detached_addon_missing"),
        (IssueType.DETACHED_APP_REMOVED, "detached_addon_removed"),
    ],
)
async def test_api_resolution_info_v1_uses_legacy_names(
    coresys: CoreSys, api_client: TestClient, issue_type: str, legacy_issue_type: str
):
    """Test v1 resolution info uses legacy issue type and check slug names."""
    coresys.resolution.add_issue(Issue(issue_type, ContextType.ADDON, reference="test"))

    resp = await api_client.get("/resolution/info")
    result = await resp.json()

    # V1 should return legacy issue type name
    issue_types = [issue["type"] for issue in result["data"][ATTR_ISSUES]]
    assert legacy_issue_type in issue_types
    assert issue_type not in issue_types

    # V1 should return legacy check slugs
    check_slugs = [check["slug"] for check in result["data"]["checks"]]
    assert "addon_pwned" in check_slugs
    assert "deprecated_addon" in check_slugs
    assert "deprecated_arch_addon" in check_slugs
    assert "detached_addon_missing" in check_slugs
    assert "detached_addon_removed" in check_slugs
    # Should NOT have new names
    assert "app_pwned" not in check_slugs
    assert "deprecated_app" not in check_slugs
    assert "deprecated_arch_app" not in check_slugs
    assert "detached_app_missing" not in check_slugs
    assert "detached_app_removed" not in check_slugs


@pytest.mark.parametrize(
    "issue_type",
    [
        IssueType.DEPRECATED_APP,
        IssueType.DEPRECATED_ARCH_APP,
        IssueType.DETACHED_APP_MISSING,
        IssueType.DETACHED_APP_REMOVED,
    ],
)
async def test_api_resolution_info_v2_uses_new_names(
    coresys: CoreSys, api_client_v2: TestClient, issue_type: str
):
    """Test v2 resolution info uses new issue type and check slug names."""
    coresys.resolution.add_issue(Issue(issue_type, ContextType.ADDON, reference="test"))

    resp = await api_client_v2.get("/v2/resolution/info")
    result = await resp.json()

    # V2 should return new issue type name
    issue_types = [issue["type"] for issue in result["data"][ATTR_ISSUES]]
    assert issue_type in issue_types

    # V2 should return new check slugs
    check_slugs = [check["slug"] for check in result["data"]["checks"]]
    assert "app_pwned" in check_slugs
    assert "deprecated_app" in check_slugs
    assert "deprecated_arch_app" in check_slugs
    assert "detached_app_missing" in check_slugs
    assert "detached_app_removed" in check_slugs
    # Should NOT have legacy names
    assert "addon_pwned" not in check_slugs
    assert "deprecated_addon" not in check_slugs
    assert "deprecated_arch_addon" not in check_slugs
    assert "detached_addon_missing" not in check_slugs
    assert "detached_addon_removed" not in check_slugs


@pytest.mark.parametrize(
    ("issue_type", "legacy_issue_type"),
    [
        (IssueType.DEPRECATED_APP, "deprecated_addon"),
        (IssueType.DEPRECATED_ARCH_APP, "deprecated_arch_addon"),
        (IssueType.DETACHED_APP_MISSING, "detached_addon_missing"),
        (IssueType.DETACHED_APP_REMOVED, "detached_addon_removed"),
    ],
)
async def test_ws_resolution_issue_events_legacy_compat(
    coresys: CoreSys,
    ha_ws_client: AsyncMock,
    issue_type: str,
    legacy_issue_type: str,
):
    """Test WS issue events use legacy names when SUPERVISOR_WEBSOCKET_V2_API is disabled."""
    # Default: SUPERVISOR_WEBSOCKET_V2_API is disabled
    coresys.resolution.add_issue(Issue(issue_type, ContextType.ADDON, reference="test"))
    await asyncio.sleep(0)

    ws_events = [
        call.args[0]
        for call in ha_ws_client.async_send_command.call_args_list
        if call.args[0].get("type") == WSType.SUPERVISOR_EVENT
        and call.args[0].get("data", {}).get("event") == "issue_changed"
    ]
    assert len(ws_events) == 1
    assert ws_events[0]["data"]["data"]["type"] == legacy_issue_type

    # After dismissing, the issue_removed event should also use legacy name
    ha_ws_client.async_send_command.reset_mock()
    issue = coresys.resolution.issues[0]
    coresys.resolution.dismiss_issue(issue)
    await asyncio.sleep(0)

    ws_events = [
        call.args[0]
        for call in ha_ws_client.async_send_command.call_args_list
        if call.args[0].get("type") == WSType.SUPERVISOR_EVENT
        and call.args[0].get("data", {}).get("event") == "issue_removed"
    ]
    assert len(ws_events) == 1
    assert ws_events[0]["data"]["data"]["type"] == legacy_issue_type


@pytest.mark.parametrize(
    "issue_type",
    [
        IssueType.DEPRECATED_APP,
        IssueType.DEPRECATED_ARCH_APP,
        IssueType.DETACHED_APP_MISSING,
        IssueType.DETACHED_APP_REMOVED,
    ],
)
async def test_ws_resolution_issue_events_v2(
    coresys: CoreSys, ha_ws_client: AsyncMock, issue_type: str
):
    """Test WS issue events use new names when SUPERVISOR_WEBSOCKET_V2_API is enabled."""
    coresys.config.set_feature_flag(FeatureFlag.SUPERVISOR_WEBSOCKET_V2_API, True)

    coresys.resolution.add_issue(Issue(issue_type, ContextType.ADDON, reference="test"))
    await asyncio.sleep(0)

    ws_events = [
        call.args[0]
        for call in ha_ws_client.async_send_command.call_args_list
        if call.args[0].get("type") == WSType.SUPERVISOR_EVENT
        and call.args[0].get("data", {}).get("event") == "issue_changed"
    ]
    assert len(ws_events) == 1
    assert ws_events[0]["data"]["data"]["type"] == issue_type

    # After dismissing, the issue_removed event should also use new name
    ha_ws_client.async_send_command.reset_mock()
    issue = coresys.resolution.issues[0]
    coresys.resolution.dismiss_issue(issue)
    await asyncio.sleep(0)

    ws_events = [
        call.args[0]
        for call in ha_ws_client.async_send_command.call_args_list
        if call.args[0].get("type") == WSType.SUPERVISOR_EVENT
        and call.args[0].get("data", {}).get("event") == "issue_removed"
    ]
    assert len(ws_events) == 1
    assert ws_events[0]["data"]["data"]["type"] == issue_type


@pytest.mark.parametrize(
    ("check_slug", "legacy_slug"),
    [
        ("app_pwned", "addon_pwned"),
        ("deprecated_app", "deprecated_addon"),
        ("deprecated_arch_app", "deprecated_arch_addon"),
        ("detached_app_missing", "detached_addon_missing"),
        ("detached_app_removed", "detached_addon_removed"),
    ],
)
async def test_api_resolution_check_run_v1_accepts_legacy_names(
    api_client: TestClient,
    check_slug: str,
    legacy_slug: str,
):
    """Test v1 check run endpoint translates legacy check slugs to new ones."""
    # V1 should accept legacy slug and translate it to new slug
    resp = await api_client.post(f"/resolution/check/{legacy_slug}/run")
    assert resp.status == 200

    # V1 should also accept new slug directly
    resp = await api_client.post(f"/resolution/check/{check_slug}/run")
    assert resp.status == 200


@pytest.mark.parametrize(
    ("check_slug", "legacy_slug"),
    [
        ("app_pwned", "addon_pwned"),
        ("deprecated_app", "deprecated_addon"),
        ("deprecated_arch_app", "deprecated_arch_addon"),
        ("detached_app_missing", "detached_addon_missing"),
        ("detached_app_removed", "detached_addon_removed"),
    ],
)
async def test_api_resolution_check_run_v2_accepts_new_names(
    api_client_v2: TestClient, check_slug: str, legacy_slug: str
):
    """Test v2 check run endpoint accepts new check slugs and rejects legacy ones."""
    # V2 should accept new slug
    resp = await api_client_v2.post(f"/v2/resolution/check/{check_slug}/run")
    assert resp.status == 200

    # V2 should NOT accept legacy slug
    resp = await api_client_v2.post(f"/v2/resolution/check/{legacy_slug}/run")
    assert resp.status == HTTPStatus.NOT_FOUND


@pytest.mark.parametrize(
    ("check_slug", "legacy_slug"),
    [
        ("app_pwned", "addon_pwned"),
        ("deprecated_app", "deprecated_addon"),
        ("deprecated_arch_app", "deprecated_arch_addon"),
        ("detached_app_missing", "detached_addon_missing"),
        ("detached_app_removed", "detached_addon_removed"),
    ],
)
async def test_api_resolution_check_options_v1_accepts_legacy_names(
    api_client: TestClient,
    check_slug: str,
    legacy_slug: str,
):
    """Test v1 check options endpoint translates legacy check slugs to new ones."""
    # V1 should accept legacy slug and translate it to new slug
    resp = await api_client.post(
        f"/resolution/check/{legacy_slug}/options", json={"enabled": False}
    )
    assert resp.status == 200

    # V1 should also accept new slug directly
    resp = await api_client.post(
        f"/resolution/check/{check_slug}/options", json={"enabled": True}
    )
    assert resp.status == 200


@pytest.mark.parametrize(
    ("check_slug", "legacy_slug"),
    [
        ("app_pwned", "addon_pwned"),
        ("deprecated_app", "deprecated_addon"),
        ("deprecated_arch_app", "deprecated_arch_addon"),
        ("detached_app_missing", "detached_addon_missing"),
        ("detached_app_removed", "detached_addon_removed"),
    ],
)
async def test_api_resolution_check_options_v2_accepts_new_names(
    api_client_v2: TestClient, check_slug: str, legacy_slug: str
):
    """Test v2 check options endpoint accepts new check slugs and rejects legacy ones."""
    # V2 should accept new slug
    resp = await api_client_v2.post(
        f"/v2/resolution/check/{check_slug}/options", json={"enabled": False}
    )
    assert resp.status == 200

    resp = await api_client_v2.post(
        f"/v2/resolution/check/{check_slug}/options", json={"enabled": True}
    )
    assert resp.status == 200

    # V2 should NOT accept legacy slug
    resp = await api_client_v2.post(
        f"/v2/resolution/check/{legacy_slug}/options", json={"enabled": False}
    )
    assert resp.status == HTTPStatus.NOT_FOUND
