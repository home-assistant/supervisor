"""Test evaluation base."""
# pylint: disable=import-error,protected-access
from unittest.mock import patch

from supervisor.const import CoreState
from supervisor.coresys import CoreSys
from supervisor.resolution.evaluations.dbus import EvaluateDbus


async def test_evaluation(coresys: CoreSys):
    """Test evaluation."""
    dbus = EvaluateDbus(coresys)
    coresys.core.state = CoreState.INITIALIZE

    assert dbus.reason not in coresys.resolution.unsupported

    with patch("pathlib.Path.exists", return_value=False):
        await dbus()
        assert dbus.reason in coresys.resolution.unsupported

    with patch("pathlib.Path.exists", return_value=True):
        await dbus()
        assert dbus.reason not in coresys.resolution.unsupported


async def test_did_run(coresys: CoreSys):
    """Test that the evaluation ran as expected."""
    dbus = EvaluateDbus(coresys)
    should_run = dbus.states
    should_not_run = [state for state in CoreState if state not in should_run]
    assert len(should_run) != 0
    assert len(should_not_run) != 0

    with patch(
        "supervisor.resolution.evaluations.dbus.EvaluateDbus.evaluate",
        return_value=None,
    ) as evaluate:
        for state in should_run:
            coresys.core.state = state
            await dbus()
            evaluate.assert_called_once()
            evaluate.reset_mock()

        for state in should_not_run:
            coresys.core.state = state
            await dbus()
            evaluate.assert_not_called()
            evaluate.reset_mock()
