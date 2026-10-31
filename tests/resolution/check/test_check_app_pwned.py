"""Test Check App Pwned."""

# pylint: disable=import-error,protected-access
from unittest.mock import AsyncMock, patch

from supervisor.const import AppState, CoreState
from supervisor.coresys import CoreSys
from supervisor.exceptions import PwnedConnectivityError, PwnedSecret
from supervisor.resolution.checks.app_pwned import CheckAppPwned
from supervisor.resolution.const import ContextType, IssueType, SuggestionType
from supervisor.resolution.data import Issue


class FakeApp:
    """Fake App for tests."""

    slug = "my_test"
    state = AppState.STARTED
    is_installed = True

    def __init__(self) -> None:
        """Initialize fake app."""
        self.pwned: dict[str, str] = {}


async def verify_pwned(secret: str) -> None:
    """Treat the hash "pwned" as compromised."""
    if secret == "pwned":
        raise PwnedSecret


async def test_base(coresys: CoreSys):
    """Test check basics."""
    app_pwned = CheckAppPwned(coresys)
    assert app_pwned.slug == "app_pwned"
    assert app_pwned.enabled


async def test_check(coresys: CoreSys):
    """Test check."""
    coresys.security.pwned = True
    app_pwned = CheckAppPwned(coresys)
    await coresys.core.set_state(CoreState.RUNNING)

    app = FakeApp()
    coresys.apps.local[app.slug] = app

    assert len(coresys.resolution.issues) == 0

    coresys.security.verify_secret = AsyncMock(side_effect=PwnedSecret)
    await app_pwned.run_check.__wrapped__(app_pwned)
    assert not coresys.security.verify_secret.called

    app.pwned = {"password": "123456"}
    coresys.security.verify_secret = AsyncMock(return_value=None)
    await app_pwned.run_check.__wrapped__(app_pwned)
    assert coresys.security.verify_secret.called

    assert len(coresys.resolution.issues) == 0

    app.pwned = {
        "logins[1].password": "pwned",
        "logins[0].password": "pwned",
        "mqtt.password": "safe",
    }
    coresys.security.verify_secret = AsyncMock(side_effect=verify_pwned)
    await app_pwned.run_check.__wrapped__(app_pwned)
    assert coresys.security.verify_secret.call_count == 2

    assert len(coresys.resolution.issues) == 1
    assert coresys.resolution.issues[-1].type == IssueType.PWNED
    assert coresys.resolution.issues[-1].reference == app.slug
    assert coresys.resolution.issues[-1].reference_extra == {
        "options": ["logins[0].password", "logins[1].password"]
    }
    assert coresys.resolution.suggestions[-1].type == SuggestionType.EXECUTE_STOP
    assert coresys.resolution.suggestions[-1].reference == app.slug


async def test_approve(coresys: CoreSys, supervisor_internet):
    """Test check."""
    app_pwned = CheckAppPwned(coresys)
    await coresys.core.set_state(CoreState.RUNNING)

    app = FakeApp()
    coresys.apps.local[app.slug] = app
    app.pwned = {"password": "pwned"}
    issue = Issue(
        IssueType.PWNED,
        ContextType.ADDON,
        reference=app.slug,
        reference_extra={"options": ["password"]},
    )

    coresys.security.verify_secret = AsyncMock(side_effect=verify_pwned)
    assert await app_pwned.approve_check(issue)

    coresys.security.verify_secret = AsyncMock(side_effect=PwnedConnectivityError)
    assert await app_pwned.approve_check(issue)

    coresys.security.verify_secret = AsyncMock(return_value=None)
    assert not await app_pwned.approve_check(issue)


async def test_approve_options_changed(coresys: CoreSys, supervisor_internet):
    """Test issue is refreshed in place when the set of pwned options changed."""
    app_pwned = CheckAppPwned(coresys)
    await coresys.core.set_state(CoreState.RUNNING)

    app = FakeApp()
    coresys.apps.local[app.slug] = app
    app.pwned = {"logins[0].password": "pwned", "logins[1].password": "safe"}
    coresys.security.verify_secret = AsyncMock(side_effect=verify_pwned)

    coresys.resolution.create_issue(
        IssueType.PWNED,
        ContextType.ADDON,
        reference=app.slug,
        reference_extra={"options": ["logins[0].password", "logins[1].password"]},
    )
    issue = coresys.resolution.issues[0]

    # One option is still pwned: keep the issue, listing only the current option
    assert await app_pwned.approve_check(issue)
    assert len(coresys.resolution.issues) == 1
    assert coresys.resolution.issues[0].reference_extra == {
        "options": ["logins[0].password"]
    }


async def test_remaining_warning_survives_throttled_check(
    coresys: CoreSys, supervisor_internet
):
    """Test a remaining pwned option keeps its issue when run_check is throttled."""
    app_pwned = CheckAppPwned(coresys)
    await coresys.core.set_state(CoreState.RUNNING)

    app = FakeApp()
    coresys.apps.local[app.slug] = app
    app.pwned = {"logins[0].password": "pwned", "logins[1].password": "safe"}
    coresys.security.verify_secret = AsyncMock(side_effect=verify_pwned)

    coresys.resolution.create_issue(
        IssueType.PWNED,
        ContextType.ADDON,
        reference=app.slug,
        reference_extra={"options": ["logins[0].password", "logins[1].password"]},
    )

    # run_check is throttled (no-op); the healthcheck must still keep the warning
    # for the option that is still compromised, with a refreshed list
    with patch.object(CheckAppPwned, "run_check", AsyncMock()):
        await app_pwned()

    assert len(coresys.resolution.issues) == 1
    assert coresys.resolution.issues[0].reference_extra == {
        "options": ["logins[0].password"]
    }


async def test_with_global_disable(coresys: CoreSys):
    """Test when pwned is globally disabled."""
    coresys.security.pwned = False
    app_pwned = CheckAppPwned(coresys)
    await coresys.core.set_state(CoreState.RUNNING)

    app = FakeApp()
    coresys.apps.local[app.slug] = app

    assert len(coresys.resolution.issues) == 0
    coresys.security.verify_secret = AsyncMock(side_effect=PwnedSecret)
    await app_pwned.run_check.__wrapped__(app_pwned)
    assert not coresys.security.verify_secret.called


async def test_did_run(coresys: CoreSys):
    """Test that the check ran as expected."""
    app_pwned = CheckAppPwned(coresys)
    should_run = app_pwned.states
    should_not_run = [state for state in CoreState if state not in should_run]
    assert len(should_run) != 0
    assert len(should_not_run) != 0

    with patch(
        "supervisor.resolution.checks.app_pwned.CheckAppPwned.run_check",
        return_value=None,
    ) as check:
        for state in should_run:
            await coresys.core.set_state(state)
            await app_pwned()
            check.assert_called_once()
            check.reset_mock()

        for state in should_not_run:
            await coresys.core.set_state(state)
            await app_pwned()
            check.assert_not_called()
            check.reset_mock()
