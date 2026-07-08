"""Test fixup clearing a conflicting app port mapping."""

import pytest

from supervisor.apps.app import App
from supervisor.coresys import CoreSys
from supervisor.resolution.const import ContextType, IssueType, SuggestionType
from supervisor.resolution.data import Issue
from supervisor.resolution.fixups.app_clear_port_config import FixupAppClearPortConfig


@pytest.mark.usefixtures("tmp_supervisor_data")
async def test_fixup_clears_conflicting_port(coresys: CoreSys, install_app_ssh: App):
    """Test the conflicting port mapping is cleared and persisted."""
    app = install_app_ssh
    app.persist["network"] = {"22/tcp": 2222}
    assert app.ports == {"22/tcp": 2222}

    fixup = FixupAppClearPortConfig(coresys)
    assert not fixup.auto

    coresys.resolution.add_issue(
        Issue(
            IssueType.APP_PORT_CONFLICT,
            ContextType.ADDON,
            reference=app.slug,
            reference_extra={"port": 2222},
        ),
        suggestions=[SuggestionType.CLEAR_PORT_CONFIG],
    )

    await fixup()

    # The conflicting mapping must be cleared in the persisted config, not just
    # in a throwaway copy returned by the getter.
    assert app.ports == {"22/tcp": None}
    assert app.persist["network"] == {"22/tcp": None}
    assert coresys.resolution.issues == []
    assert coresys.resolution.suggestions == []
