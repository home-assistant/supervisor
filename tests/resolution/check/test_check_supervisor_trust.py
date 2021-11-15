"""Test Check Supervisor trust."""
# pylint: disable=import-error,protected-access
from unittest.mock import AsyncMock, patch

from supervisor.const import SupervisorState
from supervisor.coresys import CoreSys
from supervisor.exceptions import CodeNotaryError, CodeNotaryUntrusted
from supervisor.resolution.checks.supervisor_trust import CheckSupervisorTrust
from supervisor.resolution.const import IssueType, UnhealthyReason


async def test_base(coresys: CoreSys):
    """Test check basics."""
    supervisor_trust = CheckSupervisorTrust(coresys)
    assert supervisor_trust.slug == "supervisor_trust"
    assert supervisor_trust.enabled


async def test_check(coresys: CoreSys):
    """Test check."""
    supervisor_trust = CheckSupervisorTrust(coresys)
    coresys.core.state = SupervisorState.RUNNING

    assert len(coresys.resolution.issues) == 0

    coresys.supervisor.check_trust = AsyncMock(side_effect=CodeNotaryError)
    await supervisor_trust.run_check()
    assert coresys.supervisor.check_trust.called

    coresys.supervisor.check_trust = AsyncMock(return_value=None)
    await supervisor_trust.run_check()
    assert coresys.supervisor.check_trust.called

    assert len(coresys.resolution.issues) == 0

    coresys.supervisor.check_trust = AsyncMock(side_effect=CodeNotaryUntrusted)
    await supervisor_trust.run_check()
    assert coresys.supervisor.check_trust.called

    assert len(coresys.resolution.issues) == 1
    assert coresys.resolution.issues[-1].type == IssueType.TRUST

    assert UnhealthyReason.UNTRUSTED in coresys.resolution.unhealthy


async def test_approve(coresys: CoreSys):
    """Test check."""
    supervisor_trust = CheckSupervisorTrust(coresys)
    coresys.core.state = SupervisorState.RUNNING

    coresys.supervisor.check_trust = AsyncMock(side_effect=CodeNotaryUntrusted)
    assert await supervisor_trust.approve_check()

    coresys.supervisor.check_trust = AsyncMock(return_value=None)
    assert not await supervisor_trust.approve_check()


async def test_with_global_disable(coresys: CoreSys, caplog):
    """Test when pwned is globally disabled."""
    coresys.security.content_trust = False
    supervisor_trust = CheckSupervisorTrust(coresys)
    coresys.core.state = SupervisorState.RUNNING

    assert len(coresys.resolution.issues) == 0
    coresys.security.verify_own_content = AsyncMock(side_effect=CodeNotaryUntrusted)
    await supervisor_trust.run_check()
    assert not coresys.security.verify_own_content.called
    assert (
        "Skipping supervisor_trust, content_trust is globally disabled" in caplog.text
    )


async def test_did_run(coresys: CoreSys):
    """Test that the check ran as expected."""
    supervisor_trust = CheckSupervisorTrust(coresys)
    should_run = supervisor_trust.states
    should_not_run = [state for state in SupervisorState if state not in should_run]
    assert len(should_run) != 0
    assert len(should_not_run) != 0

    with patch(
        "supervisor.resolution.checks.supervisor_trust.CheckSupervisorTrust.run_check",
        return_value=None,
    ) as check:
        for state in should_run:
            coresys.core.state = state
            await supervisor_trust()
            check.assert_called_once()
            check.reset_mock()

        for state in should_not_run:
            coresys.core.state = state
            await supervisor_trust()
            check.assert_not_called()
            check.reset_mock()
