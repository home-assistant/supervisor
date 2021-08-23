"""Test Check Addon Pwned."""
# pylint: disable=import-error,protected-access
from unittest.mock import AsyncMock, patch

from supervisor.const import CoreState
from supervisor.coresys import CoreSys
from supervisor.exceptions import CodeNotaryError, CodeNotaryUntrusted
from supervisor.resolution.checks.system_trust import CheckSystemTrust
from supervisor.resolution.const import IssueType, UnhealthyReason


async def test_base(coresys: CoreSys):
    """Test check basics."""
    system_trust = CheckSystemTrust(coresys)
    assert system_trust.slug == "system_trust"
    assert system_trust.enabled


async def test_check(coresys: CoreSys):
    """Test check."""
    system_trust = CheckSystemTrust(coresys)
    coresys.core.state = CoreState.RUNNING

    assert len(coresys.resolution.issues) == 0

    coresys.supervisor.check_trust = AsyncMock(side_effect=CodeNotaryError)
    coresys.homeassistant.core.check_trust = AsyncMock(side_effect=CodeNotaryError)
    await system_trust.run_check()
    assert coresys.supervisor.check_trust.called
    assert coresys.homeassistant.core.check_trust.called

    coresys.supervisor.check_trust = AsyncMock(return_value=None)
    coresys.homeassistant.core.check_trust = AsyncMock(return_value=None)
    await system_trust.run_check()
    assert coresys.supervisor.check_trust.called
    assert coresys.homeassistant.core.check_trust.called

    assert len(coresys.resolution.issues) == 0

    coresys.supervisor.check_trust = AsyncMock(side_effect=CodeNotaryUntrusted)
    coresys.homeassistant.core.check_trust = AsyncMock(side_effect=CodeNotaryUntrusted)
    await system_trust.run_check()
    assert coresys.supervisor.check_trust.called
    assert coresys.homeassistant.core.check_trust.called

    assert len(coresys.resolution.issues) == 2
    assert coresys.resolution.issues[0].type == IssueType.TRUST
    assert coresys.resolution.issues[0].reference == "supervisor"
    assert coresys.resolution.issues[1].type == IssueType.TRUST
    assert coresys.resolution.issues[1].reference == "core"

    assert UnhealthyReason.UNTRUSTED in coresys.resolution.unhealthy


async def test_approve(coresys: CoreSys):
    """Test check."""
    system_trust = CheckSystemTrust(coresys)
    coresys.core.state = CoreState.RUNNING

    coresys.supervisor.check_trust = AsyncMock(side_effect=CodeNotaryUntrusted)
    coresys.homeassistant.core.check_trust = AsyncMock(side_effect=CodeNotaryUntrusted)
    assert await system_trust.approve_check(reference="core")
    assert await system_trust.approve_check(reference="supervisor")

    coresys.supervisor.check_trust = AsyncMock(return_value=None)
    coresys.homeassistant.core.check_trust = AsyncMock(return_value=None)
    assert not await system_trust.approve_check(reference="core")
    assert not await system_trust.approve_check(reference="supervisor")


async def test_with_global_disable(coresys: CoreSys, caplog):
    """Test when pwned is globally disabled."""
    coresys.security.content_trust = False
    system_trust = CheckSystemTrust(coresys)
    coresys.core.state = CoreState.RUNNING

    assert len(coresys.resolution.issues) == 0
    coresys.security.verify_own_content = AsyncMock(side_effect=CodeNotaryUntrusted)
    await system_trust.run_check()
    assert not coresys.security.verify_own_content.called
    assert "Skipping system_trust, content_trust is globally disabled" in caplog.text


async def test_did_run(coresys: CoreSys):
    """Test that the check ran as expected."""
    system_trust = CheckSystemTrust(coresys)
    should_run = system_trust.states
    should_not_run = [state for state in CoreState if state not in should_run]
    assert len(should_run) != 0
    assert len(should_not_run) != 0

    with patch(
        "supervisor.resolution.checks.system_trust.CheckSystemTrust.run_check",
        return_value=None,
    ) as check:
        for state in should_run:
            coresys.core.state = state
            await system_trust()
            check.assert_called_once()
            check.reset_mock()

        for state in should_not_run:
            coresys.core.state = state
            await system_trust()
            check.assert_not_called()
            check.reset_mock()
