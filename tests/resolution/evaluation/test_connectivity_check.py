"""Test connectivity check evaluation."""

from unittest.mock import PropertyMock, patch

from supervisor.const import CoreState
from supervisor.coresys import CoreSys
from supervisor.resolution.evaluations.connectivity_check import (
    EvaluateConnectivityCheck,
)


async def test_evaluation(coresys: CoreSys):
    """Test evaluation."""
    connectivity_check = EvaluateConnectivityCheck(coresys)
    await coresys.core.set_state(CoreState.RUNNING)

    assert connectivity_check.reason not in coresys.resolution.unsupported

    with patch.object(
        type(coresys.dbus.network),
        "connectivity_enabled",
        new=PropertyMock(return_value=False),
    ) as connectivity_enabled:
        await connectivity_check()
        assert connectivity_check.reason in coresys.resolution.unsupported

        connectivity_enabled.return_value = True
        await connectivity_check()
        assert connectivity_check.reason not in coresys.resolution.unsupported

        connectivity_enabled.return_value = None
        await connectivity_check()
        assert connectivity_check.reason not in coresys.resolution.unsupported


async def test_did_run(coresys: CoreSys):
    """Test that the evaluation ran as expected."""
    connectivity_check = EvaluateConnectivityCheck(coresys)
    should_run = connectivity_check.states
    should_not_run = [state for state in CoreState if state not in should_run]
    assert len(should_run) != 0
    assert len(should_not_run) != 0

    with patch(
        "supervisor.resolution.evaluations.connectivity_check.EvaluateConnectivityCheck.evaluate",
        return_value=False,
    ) as evaluate:
        for state in should_run:
            await coresys.core.set_state(state)
            await connectivity_check()
            evaluate.assert_called_once()
            evaluate.reset_mock()

        for state in should_not_run:
            await coresys.core.set_state(state)
            await connectivity_check()
            evaluate.assert_not_called()
            evaluate.reset_mock()
