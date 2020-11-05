"""Test evaluation base."""
# pylint: disable=import-error,protected-access
from unittest.mock import patch

from supervisor.const import CoreState
from supervisor.coresys import CoreSys
from supervisor.resolution.evaluations.privileged import EvaluatePrivileged


async def test_evaluation(coresys: CoreSys):
    """Test evaluation."""
    privileged = EvaluatePrivileged(coresys)
    coresys.core.state = CoreState.INITIALIZE

    assert privileged.reason not in coresys.resolution.unsupported

    coresys.supervisor.instance._meta = {"HostConfig": {"Privileged": False}}
    await privileged()
    assert privileged.reason in coresys.resolution.unsupported

    coresys.supervisor.instance._meta = {"HostConfig": {"Privileged": True}}
    await privileged()
    assert privileged.reason not in coresys.resolution.unsupported


async def test_did_run(coresys: CoreSys):
    """Test that the evaluation ran as expected."""
    privileged = EvaluatePrivileged(coresys)
    should_run = privileged.states
    should_not_run = [state for state in CoreState if state not in should_run]
    assert len(should_run) != 0
    assert len(should_not_run) != 0

    with patch(
        "supervisor.resolution.evaluations.privileged.EvaluatePrivileged.evaluate",
        return_value=None,
    ) as evaluate:
        for state in should_run:
            coresys.core.state = state
            await privileged()
            evaluate.assert_called_once()
            evaluate.reset_mock()

        for state in should_not_run:
            coresys.core.state = state
            await privileged()
            evaluate.assert_not_called()
            evaluate.reset_mock()
