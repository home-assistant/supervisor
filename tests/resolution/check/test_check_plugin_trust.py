"""Test Check Plugin trust."""
# pylint: disable=import-error,protected-access
from unittest.mock import AsyncMock, patch

from supervisor.const import CoreState
from supervisor.coresys import CoreSys
from supervisor.exceptions import CodeNotaryError, CodeNotaryUntrusted
from supervisor.resolution.checks.plugin_trust import CheckPluginTrust
from supervisor.resolution.const import IssueType, UnhealthyReason


async def test_base(coresys: CoreSys):
    """Test check basics."""
    plugin_trust = CheckPluginTrust(coresys)
    assert plugin_trust.slug == "plugin_trust"
    assert plugin_trust.enabled


async def test_check(coresys: CoreSys):
    """Test check."""
    plugin_trust = CheckPluginTrust(coresys)
    coresys.core.state = CoreState.RUNNING

    assert len(coresys.resolution.issues) == 0

    coresys.plugins.audio.check_trust = AsyncMock(side_effect=CodeNotaryError)
    coresys.plugins.dns.check_trust = AsyncMock(side_effect=CodeNotaryError)
    coresys.plugins.cli.check_trust = AsyncMock(side_effect=CodeNotaryError)
    coresys.plugins.multicast.check_trust = AsyncMock(side_effect=CodeNotaryError)
    coresys.plugins.observer.check_trust = AsyncMock(side_effect=CodeNotaryError)

    await plugin_trust.run_check()
    assert coresys.plugins.audio.check_trust.called
    assert coresys.plugins.dns.check_trust.called
    assert coresys.plugins.cli.check_trust.called
    assert coresys.plugins.multicast.check_trust.called
    assert coresys.plugins.observer.check_trust.called

    coresys.plugins.audio.check_trust = AsyncMock(return_value=None)
    coresys.plugins.dns.check_trust = AsyncMock(return_value=None)
    coresys.plugins.cli.check_trust = AsyncMock(return_value=None)
    coresys.plugins.multicast.check_trust = AsyncMock(return_value=None)
    coresys.plugins.observer.check_trust = AsyncMock(return_value=None)

    await plugin_trust.run_check()
    assert coresys.plugins.audio.check_trust.called
    assert coresys.plugins.dns.check_trust.called
    assert coresys.plugins.cli.check_trust.called
    assert coresys.plugins.multicast.check_trust.called
    assert coresys.plugins.observer.check_trust.called

    assert len(coresys.resolution.issues) == 0

    coresys.plugins.audio.check_trust = AsyncMock(side_effect=CodeNotaryUntrusted)
    coresys.plugins.dns.check_trust = AsyncMock(side_effect=CodeNotaryUntrusted)
    coresys.plugins.cli.check_trust = AsyncMock(side_effect=CodeNotaryUntrusted)
    coresys.plugins.multicast.check_trust = AsyncMock(side_effect=CodeNotaryUntrusted)
    coresys.plugins.observer.check_trust = AsyncMock(side_effect=CodeNotaryUntrusted)

    await plugin_trust.run_check()
    assert coresys.plugins.audio.check_trust.called
    assert coresys.plugins.dns.check_trust.called
    assert coresys.plugins.cli.check_trust.called
    assert coresys.plugins.multicast.check_trust.called
    assert coresys.plugins.observer.check_trust.called

    assert len(coresys.resolution.issues) == 5
    assert coresys.resolution.issues[-1].type == IssueType.TRUST

    assert UnhealthyReason.UNTRUSTED in coresys.resolution.unhealthy


async def test_approve(coresys: CoreSys):
    """Test check."""
    plugin_trust = CheckPluginTrust(coresys)
    coresys.core.state = CoreState.RUNNING

    coresys.plugins.audio.check_trust = AsyncMock(side_effect=CodeNotaryUntrusted)
    assert await plugin_trust.approve_check(reference="audio")

    coresys.plugins.audio.check_trust = AsyncMock(return_value=None)
    assert not await plugin_trust.approve_check(reference="audio")


async def test_with_global_disable(coresys: CoreSys, caplog):
    """Test when pwned is globally disabled."""
    coresys.security.content_trust = False
    plugin_trust = CheckPluginTrust(coresys)
    coresys.core.state = CoreState.RUNNING

    assert len(coresys.resolution.issues) == 0
    coresys.security.verify_own_content = AsyncMock(side_effect=CodeNotaryUntrusted)
    await plugin_trust.run_check()
    assert not coresys.security.verify_own_content.called
    assert "Skipping plugin_trust, content_trust is globally disabled" in caplog.text


async def test_did_run(coresys: CoreSys):
    """Test that the check ran as expected."""
    plugin_trust = CheckPluginTrust(coresys)
    should_run = plugin_trust.states
    should_not_run = [state for state in CoreState if state not in should_run]
    assert len(should_run) != 0
    assert len(should_not_run) != 0

    with patch(
        "supervisor.resolution.checks.plugin_trust.CheckPluginTrust.run_check",
        return_value=None,
    ) as check:
        for state in should_run:
            coresys.core.state = state
            await plugin_trust()
            check.assert_called_once()
            check.reset_mock()

        for state in should_not_run:
            coresys.core.state = state
            await plugin_trust()
            check.assert_not_called()
            check.reset_mock()
