"""Test Check Addon Pwned."""
# pylint: disable=import-error,protected-access
from unittest.mock import AsyncMock, patch

from supervisor.const import AddonState, CoreState
from supervisor.coresys import CoreSys
from supervisor.resolution.checks.addon_pwned import CheckAddonPwned
from supervisor.resolution.const import IssueType, SuggestionType


class TestAddon:
    """Test Addon."""

    slug = "my_test"
    pwned = set()
    state = AddonState.STARTED
    is_installed = True


async def test_base(coresys: CoreSys):
    """Test check basics."""
    addon_pwned = CheckAddonPwned(coresys)
    assert addon_pwned.slug == "addon_pwned"
    assert addon_pwned.enabled


async def test_check(coresys: CoreSys):
    """Test check."""
    addon_pwned = CheckAddonPwned(coresys)
    coresys.core.state = CoreState.RUNNING

    addon = TestAddon()
    coresys.addons.local[addon.slug] = addon

    assert len(coresys.resolution.issues) == 0

    with patch(
        "supervisor.resolution.checks.addon_pwned.check_pwned_password",
        AsyncMock(return_value=True),
    ) as mock:
        await addon_pwned.run_check.__wrapped__(addon_pwned)
        assert not mock.called

    addon.pwned.add("123456")
    with patch(
        "supervisor.resolution.checks.addon_pwned.check_pwned_password",
        AsyncMock(return_value=False),
    ) as mock:
        await addon_pwned.run_check.__wrapped__(addon_pwned)
        assert mock.called

    assert len(coresys.resolution.issues) == 0

    with patch(
        "supervisor.resolution.checks.addon_pwned.check_pwned_password",
        AsyncMock(return_value=True),
    ) as mock:
        await addon_pwned.run_check.__wrapped__(addon_pwned)
        assert mock.called

    assert len(coresys.resolution.issues) == 1
    assert coresys.resolution.issues[-1].type == IssueType.PWNED
    assert coresys.resolution.issues[-1].reference == addon.slug
    assert coresys.resolution.suggestions[-1].type == SuggestionType.EXECUTE_STOP
    assert coresys.resolution.suggestions[-1].reference == addon.slug


async def test_approve(coresys: CoreSys):
    """Test check."""
    addon_pwned = CheckAddonPwned(coresys)
    coresys.core.state = CoreState.RUNNING

    addon = TestAddon()
    coresys.addons.local[addon.slug] = addon
    addon.pwned.add("123456")

    with patch(
        "supervisor.resolution.checks.addon_pwned.check_pwned_password",
        AsyncMock(return_value=True),
    ):
        assert await addon_pwned.approve_check(reference=addon.slug)

    with patch(
        "supervisor.resolution.checks.addon_pwned.check_pwned_password",
        AsyncMock(return_value=False),
    ):
        assert not await addon_pwned.approve_check(reference=addon.slug)

    addon.is_installed = False
    with patch(
        "supervisor.resolution.checks.addon_pwned.check_pwned_password",
        AsyncMock(return_value=True),
    ):
        assert not await addon_pwned.approve_check(reference=addon.slug)


async def test_did_run(coresys: CoreSys):
    """Test that the check ran as expected."""
    addon_pwned = CheckAddonPwned(coresys)
    should_run = addon_pwned.states
    should_not_run = [state for state in CoreState if state not in should_run]
    assert len(should_run) != 0
    assert len(should_not_run) != 0

    with patch(
        "supervisor.resolution.checks.addon_pwned.CheckAddonPwned.run_check",
        return_value=None,
    ) as check:
        for state in should_run:
            coresys.core.state = state
            await addon_pwned()
            check.assert_called_once()
            check.reset_mock()

        for state in should_not_run:
            coresys.core.state = state
            await addon_pwned()
            check.assert_not_called()
            check.reset_mock()
