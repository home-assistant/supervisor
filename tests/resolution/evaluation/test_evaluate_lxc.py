"""Test evaluation base."""
# pylint: disable=import-error,protected-access
from pathlib import Path
from unittest.mock import patch

from supervisor.const import SupervisorState
from supervisor.coresys import CoreSys
from supervisor.resolution.evaluations.lxc import EvaluateLxc


async def test_evaluation(coresys: CoreSys):
    """Test evaluation."""
    lxc = EvaluateLxc(coresys)
    coresys.core.state = SupervisorState.INITIALIZE

    assert lxc.reason not in coresys.resolution.unsupported

    with patch.object(Path, "exists") as mock_exists:
        mock_exists.return_value = True
        await lxc()
    assert lxc.reason in coresys.resolution.unsupported

    with patch.object(Path, "exists") as mock_exists:
        mock_exists.return_value = False
        await lxc()
    assert lxc.reason not in coresys.resolution.unsupported


async def test_did_run(coresys: CoreSys):
    """Test that the evaluation ran as expected."""
    lxc = EvaluateLxc(coresys)
    should_run = lxc.states
    should_not_run = [state for state in SupervisorState if state not in should_run]
    assert len(should_run) != 0
    assert len(should_not_run) != 0

    with patch(
        "supervisor.resolution.evaluations.lxc.EvaluateLxc.evaluate",
        return_value=None,
    ) as evaluate:
        for state in should_run:
            coresys.core.state = state
            await lxc()
            evaluate.assert_called_once()
            evaluate.reset_mock()

        for state in should_not_run:
            coresys.core.state = state
            await lxc()
            evaluate.assert_not_called()
            evaluate.reset_mock()
