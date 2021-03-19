"""Test evaluation base."""
# pylint: disable=import-error,protected-access
from unittest.mock import patch

from supervisor.const import CoreState
from supervisor.coresys import CoreSys
from supervisor.resolution.evaluations.content_trust import EvaluateContentTrust


async def test_evaluation(coresys: CoreSys):
    """Test evaluation."""
    job_conditions = EvaluateContentTrust(coresys)
    coresys.core.state = CoreState.SETUP

    await job_conditions()
    assert job_conditions.reason not in coresys.resolution.unsupported

    coresys.config.content_trust = False
    await job_conditions()
    assert job_conditions.reason in coresys.resolution.unsupported


async def test_did_run(coresys: CoreSys):
    """Test that the evaluation ran as expected."""
    job_conditions = EvaluateContentTrust(coresys)
    should_run = job_conditions.states
    should_not_run = [state for state in CoreState if state not in should_run]
    assert len(should_run) != 0
    assert len(should_not_run) != 0

    with patch(
        "supervisor.resolution.evaluations.content_trust.EvaluateContentTrust.evaluate",
        return_value=None,
    ) as evaluate:
        for state in should_run:
            coresys.core.state = state
            await job_conditions()
            evaluate.assert_called_once()
            evaluate.reset_mock()

        for state in should_not_run:
            coresys.core.state = state
            await job_conditions()
            evaluate.assert_not_called()
            evaluate.reset_mock()
