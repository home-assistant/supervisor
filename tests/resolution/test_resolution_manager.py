"""Tests for resolution manager."""

import asyncio
from typing import Any
from unittest.mock import AsyncMock, patch

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

    coresys.resolution.add_unsupported_reason(UnsupportedReason.OS)
    assert not coresys.core.supported


def test_properies_unhealthy(coresys: CoreSys):
    """Test resolution manager properties unhealthy."""
    assert coresys.core.healthy

    coresys.resolution.add_unhealthy_reason(UnhealthyReason.SUPERVISOR)
    assert not coresys.core.healthy


@pytest.mark.asyncio
async def test_resolution_dismiss_suggestion(coresys: CoreSys):
    """Test resolution manager suggestion apply api."""
    coresys.resolution.add_suggestion(
        clear_backup := Suggestion(SuggestionType.CLEAR_FULL_BACKUP, ContextType.SYSTEM)
    )

    assert coresys.resolution.suggestions[-1].type == SuggestionType.CLEAR_FULL_BACKUP
    coresys.resolution.dismiss_suggestion(clear_backup)
    assert clear_backup not in coresys.resolution.suggestions

    with pytest.raises(ResolutionError):
        coresys.resolution.dismiss_suggestion(clear_backup)


@pytest.mark.asyncio
async def test_resolution_apply_suggestion(coresys: CoreSys):
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

    await coresys.resolution.apply_suggestion(clear_backup)
    await coresys.resolution.apply_suggestion(create_backup)

    assert mock_backups.called
    assert mock_health.called

    assert clear_backup not in coresys.resolution.suggestions
    assert create_backup not in coresys.resolution.suggestions

    with pytest.raises(ResolutionError):
        await coresys.resolution.apply_suggestion(clear_backup)


@pytest.mark.asyncio
async def test_resolution_dismiss_issue(coresys: CoreSys):
    """Test resolution manager issue apply api."""
    coresys.resolution.add_issue(
        updated_failed := Issue(IssueType.UPDATE_FAILED, ContextType.SYSTEM)
    )

    assert coresys.resolution.issues[-1].type == IssueType.UPDATE_FAILED
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

    assert coresys.resolution.issues[-1].type == IssueType.UPDATE_ROLLBACK
    assert coresys.resolution.issues[-1].context == ContextType.CORE
    assert coresys.resolution.issues[-1].reference == "slug"

    assert coresys.resolution.suggestions[-1].type == SuggestionType.EXECUTE_REPAIR
    assert coresys.resolution.suggestions[-1].context == ContextType.CORE


@pytest.mark.asyncio
async def test_resolution_dismiss_unsupported(coresys: CoreSys):
    """Test resolution manager dismiss unsupported reason."""
    coresys.resolution.add_unsupported_reason(UnsupportedReason.SOFTWARE)

    coresys.resolution.dismiss_unsupported(UnsupportedReason.SOFTWARE)
    assert UnsupportedReason.SOFTWARE not in coresys.resolution.unsupported

    with pytest.raises(ResolutionError):
        coresys.resolution.dismiss_unsupported(UnsupportedReason.SOFTWARE)


async def test_suggestions_for_issue(coresys: CoreSys):
    """Test getting suggestions that fix an issue."""
    coresys.resolution.add_issue(
        corrupt_repo := Issue(
            IssueType.CORRUPT_REPOSITORY, ContextType.STORE, "test_repo"
        )
    )

    # Unrelated suggestions don't appear
    coresys.resolution.add_suggestion(
        Suggestion(SuggestionType.EXECUTE_RESET, ContextType.SUPERVISOR)
    )
    coresys.resolution.add_suggestion(
        Suggestion(SuggestionType.EXECUTE_REMOVE, ContextType.STORE, "other_repo")
    )

    assert coresys.resolution.suggestions_for_issue(corrupt_repo) == set()

    # Related suggestions do
    coresys.resolution.add_suggestion(
        execute_remove := Suggestion(
            SuggestionType.EXECUTE_REMOVE, ContextType.STORE, "test_repo"
        )
    )
    coresys.resolution.add_suggestion(
        execute_reset := Suggestion(
            SuggestionType.EXECUTE_RESET, ContextType.STORE, "test_repo"
        )
    )

    assert coresys.resolution.suggestions_for_issue(corrupt_repo) == {
        execute_reset,
        execute_remove,
    }


async def test_issues_for_suggestion(coresys: CoreSys):
    """Test getting issues fixed by a suggestion."""
    coresys.resolution.add_suggestion(
        execute_reset := Suggestion(
            SuggestionType.EXECUTE_RESET, ContextType.STORE, "test_repo"
        )
    )

    # Unrelated issues don't appear
    coresys.resolution.add_issue(Issue(IssueType.FATAL_ERROR, ContextType.CORE))
    coresys.resolution.add_issue(
        Issue(IssueType.CORRUPT_REPOSITORY, ContextType.STORE, "other_repo")
    )

    assert coresys.resolution.issues_for_suggestion(execute_reset) == set()

    # Related issues do
    coresys.resolution.add_issue(
        fatal_error := Issue(IssueType.FATAL_ERROR, ContextType.STORE, "test_repo")
    )
    coresys.resolution.add_issue(
        corrupt_repo := Issue(
            IssueType.CORRUPT_REPOSITORY, ContextType.STORE, "test_repo"
        )
    )

    assert coresys.resolution.issues_for_suggestion(execute_reset) == {
        fatal_error,
        corrupt_repo,
    }


def _supervisor_event_message(event: str, data: dict[str, Any]) -> dict[str, Any]:
    """Make mock supervisor event message for ha websocket."""
    return {
        "type": "supervisor/event",
        "data": {
            "event": event,
            "data": data,
        },
    }


async def test_events_on_issue_changes(
    coresys: CoreSys, supervisor_internet, ha_ws_client: AsyncMock
):
    """Test events fired when an issue changes."""
    # Creating an issue with a suggestion should fire exactly one issue changed event
    assert coresys.resolution.issues == []
    assert coresys.resolution.suggestions == []
    coresys.resolution.create_issue(
        IssueType.CORRUPT_REPOSITORY,
        ContextType.STORE,
        "test_repo",
        [SuggestionType.EXECUTE_RESET],
    )
    await asyncio.sleep(0)

    assert len(coresys.resolution.issues) == 1
    assert len(coresys.resolution.suggestions) == 1
    issue = coresys.resolution.issues[0]
    suggestion = coresys.resolution.suggestions[0]
    issue_expected = {
        "type": "corrupt_repository",
        "context": "store",
        "reference": "test_repo",
        "uuid": issue.uuid,
    }
    suggestion_expected = {
        "type": "execute_reset",
        "context": "store",
        "reference": "test_repo",
        "uuid": suggestion.uuid,
    }
    assert _supervisor_event_message(
        "issue_changed", issue_expected | {"suggestions": [suggestion_expected]}
    ) in [call.args[0] for call in ha_ws_client.async_send_command.call_args_list]

    # Adding a suggestion that fixes the issue changes it
    ha_ws_client.async_send_command.reset_mock()
    coresys.resolution.add_suggestion(
        execute_remove := Suggestion(
            SuggestionType.EXECUTE_REMOVE, ContextType.STORE, "test_repo"
        )
    )
    await asyncio.sleep(0)
    messages = [
        call.args[0]
        for call in ha_ws_client.async_send_command.call_args_list
        if call.args[0].get("data", {}).get("event") == "issue_changed"
    ]
    assert len(messages) == 1
    sent_data = messages[0]
    assert sent_data["type"] == "supervisor/event"
    assert sent_data["data"]["event"] == "issue_changed"
    assert sent_data["data"]["data"].items() >= issue_expected.items()
    assert len(sent_data["data"]["data"]["suggestions"]) == 2
    assert suggestion_expected in sent_data["data"]["data"]["suggestions"]
    assert {
        "type": "execute_remove",
        "context": "store",
        "reference": "test_repo",
        "uuid": execute_remove.uuid,
    } in sent_data["data"]["data"]["suggestions"]

    # Removing a suggestion that fixes the issue changes it again
    ha_ws_client.async_send_command.reset_mock()
    coresys.resolution.dismiss_suggestion(execute_remove)
    await asyncio.sleep(0)
    assert _supervisor_event_message(
        "issue_changed", issue_expected | {"suggestions": [suggestion_expected]}
    ) in [call.args[0] for call in ha_ws_client.async_send_command.call_args_list]

    # Applying a suggestion should only fire an issue removed event
    ha_ws_client.async_send_command.reset_mock()
    with patch("shutil.disk_usage", return_value=(42, 42, 2 * (1024.0**3))):
        await coresys.resolution.apply_suggestion(suggestion)

    await asyncio.sleep(0)
    assert _supervisor_event_message("issue_removed", issue_expected) in [
        call.args[0] for call in ha_ws_client.async_send_command.call_args_list
    ]


async def test_resolution_apply_suggestion_multiple_copies(coresys: CoreSys):
    """Test resolution manager applies correct suggestion when has multiple that differ by reference."""
    coresys.resolution.add_suggestion(
        remove_store_1 := Suggestion(
            SuggestionType.EXECUTE_REMOVE, ContextType.STORE, "repo_1"
        )
    )
    coresys.resolution.add_suggestion(
        remove_store_2 := Suggestion(
            SuggestionType.EXECUTE_REMOVE, ContextType.STORE, "repo_2"
        )
    )
    coresys.resolution.add_suggestion(
        remove_store_3 := Suggestion(
            SuggestionType.EXECUTE_REMOVE, ContextType.STORE, "repo_3"
        )
    )

    await coresys.resolution.apply_suggestion(remove_store_2)

    assert remove_store_1 in coresys.resolution.suggestions
    assert remove_store_2 not in coresys.resolution.suggestions
    assert remove_store_3 in coresys.resolution.suggestions


async def test_events_on_unsupported_changed(coresys: CoreSys):
    """Test events fired when unsupported changes."""
    with patch.object(
        type(coresys.homeassistant.websocket), "async_send_message"
    ) as send_message:
        # Marking system as unsupported tells HA
        assert coresys.resolution.unsupported == []
        coresys.resolution.add_unsupported_reason(UnsupportedReason.CONNECTIVITY_CHECK)
        await asyncio.sleep(0)
        assert coresys.resolution.unsupported == [UnsupportedReason.CONNECTIVITY_CHECK]
        send_message.assert_called_once_with(
            _supervisor_event_message(
                "supported_changed",
                {"supported": False, "unsupported_reasons": ["connectivity_check"]},
            )
        )

        # Adding the same reason again does nothing
        send_message.reset_mock()
        coresys.resolution.add_unsupported_reason(UnsupportedReason.CONNECTIVITY_CHECK)
        await asyncio.sleep(0)
        assert coresys.resolution.unsupported == [UnsupportedReason.CONNECTIVITY_CHECK]
        send_message.assert_not_called()

        # Adding and removing additional reasons tells HA unsupported reasons changed
        coresys.resolution.add_unsupported_reason(UnsupportedReason.JOB_CONDITIONS)
        await asyncio.sleep(0)
        assert coresys.resolution.unsupported == [
            UnsupportedReason.CONNECTIVITY_CHECK,
            UnsupportedReason.JOB_CONDITIONS,
        ]
        send_message.assert_called_once_with(
            _supervisor_event_message(
                "supported_changed",
                {
                    "supported": False,
                    "unsupported_reasons": ["connectivity_check", "job_conditions"],
                },
            )
        )

        send_message.reset_mock()
        coresys.resolution.dismiss_unsupported(UnsupportedReason.CONNECTIVITY_CHECK)
        await asyncio.sleep(0)
        assert coresys.resolution.unsupported == [UnsupportedReason.JOB_CONDITIONS]
        send_message.assert_called_once_with(
            _supervisor_event_message(
                "supported_changed",
                {"supported": False, "unsupported_reasons": ["job_conditions"]},
            )
        )

        # Dismissing all unsupported reasons tells HA its supported again
        send_message.reset_mock()
        coresys.resolution.dismiss_unsupported(UnsupportedReason.JOB_CONDITIONS)
        await asyncio.sleep(0)
        assert coresys.resolution.unsupported == []
        send_message.assert_called_once_with(
            _supervisor_event_message(
                "supported_changed", {"supported": True, "unsupported_reasons": None}
            )
        )


async def test_events_on_unhealthy_changed(coresys: CoreSys):
    """Test events fired when unhealthy changes."""
    with patch.object(
        type(coresys.homeassistant.websocket), "async_send_message"
    ) as send_message:
        # Marking system as unhealthy tells HA
        assert coresys.resolution.unhealthy == []
        coresys.resolution.add_unhealthy_reason(UnhealthyReason.DOCKER)
        await asyncio.sleep(0)
        assert coresys.resolution.unhealthy == [UnhealthyReason.DOCKER]
        send_message.assert_called_once_with(
            _supervisor_event_message(
                "health_changed",
                {"healthy": False, "unhealthy_reasons": ["docker"]},
            )
        )

        # Adding the same reason again does nothing
        send_message.reset_mock()
        coresys.resolution.add_unhealthy_reason(UnhealthyReason.DOCKER)
        await asyncio.sleep(0)
        assert coresys.resolution.unhealthy == [UnhealthyReason.DOCKER]
        send_message.assert_not_called()

        # Adding an additional reason tells HA unhealthy reasons changed
        coresys.resolution.add_unhealthy_reason(UnhealthyReason.UNTRUSTED)
        await asyncio.sleep(0)
        assert coresys.resolution.unhealthy == [
            UnhealthyReason.DOCKER,
            UnhealthyReason.UNTRUSTED,
        ]
        send_message.assert_called_once_with(
            _supervisor_event_message(
                "health_changed",
                {"healthy": False, "unhealthy_reasons": ["docker", "untrusted"]},
            )
        )


async def test_dismiss_issue_removes_orphaned_suggestions(coresys: CoreSys):
    """Test dismissing an issue also removes any suggestions which have been orphaned."""
    with patch.object(
        type(coresys.homeassistant.websocket), "async_send_message"
    ) as send_message:
        coresys.resolution.create_issue(
            IssueType.MOUNT_FAILED,
            ContextType.MOUNT,
            "test",
            [SuggestionType.EXECUTE_RELOAD, SuggestionType.EXECUTE_REMOVE],
        )
        await asyncio.sleep(0)
        assert len(coresys.resolution.issues) == 1
        assert len(coresys.resolution.suggestions) == 2
        send_message.assert_called_once()
        send_message.reset_mock()

        issue = coresys.resolution.issues[0]
        coresys.resolution.dismiss_issue(issue)
        await asyncio.sleep(0)

        # The issue and both suggestions should be dismissed as they are now orphaned
        assert coresys.resolution.issues == []
        assert coresys.resolution.suggestions == []

        # Only one message should fire to tell HA the issue was removed
        send_message.assert_called_once_with(
            _supervisor_event_message(
                "issue_removed",
                {
                    "type": "mount_failed",
                    "context": "mount",
                    "reference": "test",
                    "uuid": issue.uuid,
                },
            )
        )
