"""Test DNS server evaluation."""

from unittest.mock import patch

from supervisor.const import CoreState
from supervisor.coresys import CoreSys
from supervisor.resolution.const import ContextType, IssueType
from supervisor.resolution.evaluations.dns_server import EvaluateDNSServer


async def test_evaluation(coresys: CoreSys):
    """Test evaluation."""
    dns_server = EvaluateDNSServer(coresys)
    await coresys.core.set_state(CoreState.RUNNING)

    assert dns_server.reason not in coresys.resolution.unsupported
    assert coresys.plugins.dns.fallback is True
    assert len(coresys.resolution.issues) == 0

    await dns_server()
    assert dns_server.reason not in coresys.resolution.unsupported

    coresys.plugins.dns.fallback = False
    await dns_server()
    assert dns_server.reason not in coresys.resolution.unsupported

    coresys.plugins.dns.fallback = True
    coresys.resolution.create_issue(
        IssueType.DNS_SERVER_FAILED,
        ContextType.DNS_SERVER,
        reference="dns://192.168.30.1",
    )
    await dns_server()
    assert dns_server.reason not in coresys.resolution.unsupported

    coresys.plugins.dns.fallback = False
    await dns_server()
    assert dns_server.reason in coresys.resolution.unsupported


async def test_did_run(coresys: CoreSys):
    """Test that the evaluation ran as expected."""
    dns_server = EvaluateDNSServer(coresys)
    should_run = [CoreState.RUNNING]
    should_not_run = [state for state in CoreState if state not in should_run]
    assert len(should_run) != 0
    assert len(should_not_run) != 0

    with patch.object(EvaluateDNSServer, "evaluate", return_value=None) as evaluate:
        for state in should_run:
            await coresys.core.set_state(state)
            await dns_server()
            evaluate.assert_called_once()
            evaluate.reset_mock()

        for state in should_not_run:
            await coresys.core.set_state(state)
            await dns_server()
            evaluate.assert_not_called()
            evaluate.reset_mock()
