"""Test evaluations."""

from unittest.mock import Mock

from supervisor.const import CoreState
from supervisor.coresys import CoreSys


async def test_evaluate_system_error(coresys: CoreSys, capture_exception: Mock):
    """Test error while evaluating system."""
    await coresys.core.set_state(CoreState.RUNNING)

    await coresys.resolution.evaluate.evaluate_system()

    capture_exception.assert_not_called()
