"""Test fixup clearing a conflicting app port mapping."""

from unittest.mock import AsyncMock, patch

import pytest

from supervisor.apps.app import App
from supervisor.const import ATTR_PORTS
from supervisor.coresys import CoreSys
from supervisor.exceptions import AppUnknownError
from supervisor.resolution.const import ContextType, IssueType, SuggestionType
from supervisor.resolution.data import Issue
from supervisor.resolution.fixups.app_clear_port_config import FixupAppClearPortConfig


def _add_conflict_suggestion(coresys: CoreSys, slug: str, port: int) -> None:
    """Register a port conflict issue with a clear-port-config suggestion."""
    coresys.resolution.add_issue(
        Issue(
            IssueType.APP_PORT_CONFLICT,
            ContextType.ADDON,
            reference=slug,
            reference_extra={"port": port},
        ),
        suggestions=[SuggestionType.CLEAR_PORT_CONFIG, SuggestionType.EXECUTE_START],
    )


@pytest.mark.usefixtures("tmp_supervisor_data")
async def test_fixup_clears_conflicting_port(coresys: CoreSys, install_app_ssh: App):
    """Test the conflicting port mapping is cleared and persisted."""
    app = install_app_ssh
    app.persist["network"] = {"22/tcp": 2222}
    assert app.ports == {"22/tcp": 2222}

    fixup = FixupAppClearPortConfig(coresys)
    assert not fixup.auto

    _add_conflict_suggestion(coresys, app.slug, 2222)
    with patch.object(App, "start", new=AsyncMock()) as start:
        await fixup()
        start.assert_awaited_once()

    # The conflicting mapping must be cleared in the persisted config, not just
    # in a throwaway copy returned by the getter.
    assert app.ports == {"22/tcp": None}
    assert app.persist["network"] == {"22/tcp": None}
    assert coresys.resolution.issues == []
    assert coresys.resolution.suggestions == []


@pytest.mark.usefixtures("tmp_supervisor_data")
async def test_fixup_persists_only_the_cleared_port(
    coresys: CoreSys, install_app_ssh: App
):
    """Test clearing one port doesn't freeze the other config defaults."""
    app = install_app_ssh
    # Multi-port app: 80/tcp published by config default, 22/tcp mapped by user
    app.data[ATTR_PORTS] = {"22/tcp": None, "80/tcp": 80, "443/tcp": None}
    app.persist["network"] = {"22/tcp": 2222}
    assert app.ports == {"22/tcp": 2222, "80/tcp": 80, "443/tcp": None}

    _add_conflict_suggestion(coresys, app.slug, 80)
    with patch.object(App, "start", new=AsyncMock()) as start:
        await FixupAppClearPortConfig(coresys)()
        start.assert_awaited_once()

    # Only the existing user override and the cleared port are persisted; the
    # untouched config defaults stay out of the user config so future config
    # changes to them keep applying.
    assert app.persist["network"] == {"22/tcp": 2222, "80/tcp": None}
    assert app.ports == {"22/tcp": 2222, "80/tcp": None, "443/tcp": None}
    assert coresys.resolution.issues == []
    assert coresys.resolution.suggestions == []


@pytest.mark.usefixtures("tmp_supervisor_data")
async def test_fixup_resolves_issue_if_start_fails(
    coresys: CoreSys, install_app_ssh: App
):
    """Test issue is resolved even if restart fails after clearing mapping."""
    app = install_app_ssh
    app.persist["network"] = {"22/tcp": 2222}

    _add_conflict_suggestion(coresys, app.slug, 2222)

    with patch.object(
        App,
        "start",
        new=AsyncMock(side_effect=AppUnknownError(app=app.slug)),
    ) as start:
        await FixupAppClearPortConfig(coresys)()
        start.assert_awaited_once()

    assert app.persist["network"] == {"22/tcp": None}
    assert coresys.resolution.issues == []
    assert coresys.resolution.suggestions == []
