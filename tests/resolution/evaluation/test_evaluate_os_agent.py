"""Test evaluation base."""
# pylint: disable=import-error,protected-access
from unittest.mock import MagicMock, patch

from supervisor.const import SupervisorState
from supervisor.coresys import CoreSys
from supervisor.host.const import HostFeature
from supervisor.resolution.evaluations.os_agent import EvaluateOSAgent


async def test_evaluation(coresys: CoreSys):
    """Test evaluation."""
    agent = EvaluateOSAgent(coresys)
    coresys.core.state = SupervisorState.SETUP

    assert agent.reason not in coresys.resolution.unsupported

    coresys._host = MagicMock()

    coresys.host.features = [HostFeature.HOSTNAME]
    await agent()
    assert agent.reason in coresys.resolution.unsupported

    coresys.host.features = [
        HostFeature.OS_AGENT,
    ]
    await agent()
    assert agent.reason not in coresys.resolution.unsupported


async def test_did_run(coresys: CoreSys):
    """Test that the evaluation ran as expected."""
    agent = EvaluateOSAgent(coresys)
    should_run = agent.states
    should_not_run = [state for state in SupervisorState if state not in should_run]
    assert len(should_run) != 0
    assert len(should_not_run) != 0

    with patch(
        "supervisor.resolution.evaluations.os_agent.EvaluateOSAgent.evaluate",
        return_value=None,
    ) as evaluate:
        for state in should_run:
            coresys.core.state = state
            await agent()
            evaluate.assert_called_once()
            evaluate.reset_mock()

        for state in should_not_run:
            coresys.core.state = state
            await agent()
            evaluate.assert_not_called()
            evaluate.reset_mock()
