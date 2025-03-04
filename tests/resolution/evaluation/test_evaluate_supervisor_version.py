"""Test evaluate supervisor version."""

from unittest.mock import PropertyMock, patch

from supervisor.const import CoreState
from supervisor.coresys import CoreSys
from supervisor.resolution.evaluations.supervisor_version import (
    EvaluateSupervisorVersion,
)


async def test_evaluation(coresys: CoreSys):
    """Test evaluation."""
    need_update_mock = PropertyMock()
    with patch.object(type(coresys.supervisor), "need_update", new=need_update_mock):
        supervisor_version = EvaluateSupervisorVersion(coresys)
        await coresys.core.set_state(CoreState.RUNNING)
        need_update_mock.return_value = False

        # Only unsupported if out of date and auto update is off
        assert supervisor_version.reason not in coresys.resolution.unsupported
        need_update_mock.return_value = True
        await supervisor_version()
        assert supervisor_version.reason not in coresys.resolution.unsupported

        coresys.updater.auto_update = False
        await supervisor_version()
        assert supervisor_version.reason in coresys.resolution.unsupported


async def test_did_run(coresys: CoreSys):
    """Test that the evaluation ran as expected."""
    supervisor_version = EvaluateSupervisorVersion(coresys)
    should_run = supervisor_version.states
    should_not_run = [state for state in CoreState if state not in should_run]
    assert len(should_run) != 0
    assert len(should_not_run) != 0

    with patch(
        "supervisor.resolution.evaluations.supervisor_version.EvaluateSupervisorVersion.evaluate",
        return_value=None,
    ) as evaluate:
        for state in should_run:
            await coresys.core.set_state(state)
            await supervisor_version()
            evaluate.assert_called_once()
            evaluate.reset_mock()

        for state in should_not_run:
            await coresys.core.set_state(state)
            await supervisor_version()
            evaluate.assert_not_called()
            evaluate.reset_mock()
