"""Test Check App Pwned."""

# pylint: disable=import-error,protected-access
from unittest.mock import AsyncMock, patch

from supervisor.const import AppState, CoreState
from supervisor.coresys import CoreSys
from supervisor.exceptions import PwnedSecret
from supervisor.resolution.checks.addon_pwned import CheckAppPwned
from supervisor.resolution.const import IssueType, SuggestionType


class FakeApp:
    """Fake App for tests."""

    slug = "my_test"
    pwned = set()
    state = AppState.STARTED
    is_installed = True


async def test_base(coresys: CoreSys):
    """Test check basics."""
    app_pwned = CheckAppPwned(coresys)
    assert app_pwned.slug == "addon_pwned"
    assert app_pwned.enabled


async def test_check(coresys: CoreSys):
    """Test check."""
    app_pwned = CheckAppPwned(coresys)
    await coresys.core.set_state(CoreState.RUNNING)

    app = FakeApp()
    coresys.apps.local[app.slug] = app

    assert len(coresys.resolution.issues) == 0

    coresys.security.verify_secret = AsyncMock(side_effect=PwnedSecret)
    await app_pwned.run_check.__wrapped__(app_pwned)
    assert not coresys.security.verify_secret.called

    app.pwned.add("123456")
    coresys.security.verify_secret = AsyncMock(return_value=None)
    await app_pwned.run_check.__wrapped__(app_pwned)
    assert coresys.security.verify_secret.called

    assert len(coresys.resolution.issues) == 0

    coresys.security.verify_secret = AsyncMock(side_effect=PwnedSecret)
    await app_pwned.run_check.__wrapped__(app_pwned)
    assert coresys.security.verify_secret.called

    assert len(coresys.resolution.issues) == 1
    assert coresys.resolution.issues[-1].type == IssueType.PWNED
    assert coresys.resolution.issues[-1].reference == app.slug
    assert coresys.resolution.suggestions[-1].type == SuggestionType.EXECUTE_STOP
    assert coresys.resolution.suggestions[-1].reference == app.slug


async def test_approve(coresys: CoreSys, supervisor_internet):
    """Test check."""
    app_pwned = CheckAppPwned(coresys)
    await coresys.core.set_state(CoreState.RUNNING)

    app = FakeApp()
    coresys.apps.local[app.slug] = app
    app.pwned.add("123456")

    coresys.security.verify_secret = AsyncMock(side_effect=PwnedSecret)
    assert await app_pwned.approve_check(reference=app.slug)

    coresys.security.verify_secret = AsyncMock(return_value=None)
    assert not await app_pwned.approve_check(reference=app.slug)


async def test_with_global_disable(coresys: CoreSys, caplog):
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
    assert "Skipping addon_pwned, pwned is globally disabled" in caplog.text


async def test_did_run(coresys: CoreSys):
    """Test that the check ran as expected."""
    app_pwned = CheckAppPwned(coresys)
    should_run = app_pwned.states
    should_not_run = [state for state in CoreState if state not in should_run]
    assert len(should_run) != 0
    assert len(should_not_run) != 0

    with patch(
        "supervisor.resolution.checks.addon_pwned.CheckAppPwned.run_check",
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
