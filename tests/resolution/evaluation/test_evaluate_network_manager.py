"""Test evaluation base."""
# pylint: disable=import-error,protected-access
from unittest.mock import patch

from supervisor.const import CoreState
from supervisor.coresys import CoreSys
from supervisor.resolution.evaluations.network_manager import EvaluateNetworkManager


async def test_evaluation(coresys: CoreSys):
    """Test evaluation."""
    network_manager = EvaluateNetworkManager(coresys)
    coresys.core.state = CoreState.RUNNING

    assert network_manager.reason not in coresys.resolution.unsupported

    coresys.dbus.network.is_connected = False
    await network_manager()
    assert network_manager.reason in coresys.resolution.unsupported

    coresys.dbus.network.is_connected = True
    await network_manager()
    assert network_manager.reason not in coresys.resolution.unsupported


async def test_did_run(coresys: CoreSys):
    """Test that the evaluation ran as expected."""
    network_manager = EvaluateNetworkManager(coresys)
    should_run = network_manager.states
    should_not_run = [state for state in CoreState if state not in should_run]
    assert len(should_run) != 0
    assert len(should_not_run) != 0

    with patch(
        "supervisor.resolution.evaluations.network_manager.EvaluateNetworkManager.evaluate",
        return_value=None,
    ) as evaluate:
        for state in should_run:
            coresys.core.state = state
            await network_manager()
            evaluate.assert_called_once()
            evaluate.reset_mock()

        for state in should_not_run:
            coresys.core.state = state
            await network_manager()
            evaluate.assert_not_called()
            evaluate.reset_mock()
