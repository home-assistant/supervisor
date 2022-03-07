"""Test evaluate systemd-resolved."""

from unittest.mock import PropertyMock, patch

from supervisor.const import CoreState
from supervisor.coresys import CoreSys
from supervisor.resolution.evaluations.resolved import EvaluateResolved


async def test_evaluation(coresys: CoreSys):
    """Test evaluation."""
    resolved = EvaluateResolved(coresys)
    coresys.core.state = CoreState.SETUP

    assert resolved.reason not in coresys.resolution.unsupported

    with patch.object(
        type(coresys.dbus.resolved), "is_connected", PropertyMock(return_value=False)
    ):
        await resolved()
        assert resolved.reason in coresys.resolution.unsupported

    await resolved()
    assert resolved.reason not in coresys.resolution.unsupported


async def test_did_run(coresys: CoreSys):
    """Test that the evaluation ran as expected."""
    resolved = EvaluateResolved(coresys)
    should_run = resolved.states
    should_not_run = [state for state in CoreState if state not in should_run]
    assert len(should_run) != 0
    assert len(should_not_run) != 0

    with patch(
        "supervisor.resolution.evaluations.resolved.EvaluateResolved.evaluate",
        return_value=None,
    ) as evaluate:
        for state in should_run:
            coresys.core.state = state
            await resolved()
            evaluate.assert_called_once()
            evaluate.reset_mock()

        for state in should_not_run:
            coresys.core.state = state
            await resolved()
            evaluate.assert_not_called()
            evaluate.reset_mock()
