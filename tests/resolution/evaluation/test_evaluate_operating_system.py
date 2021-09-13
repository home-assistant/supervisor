"""Test evaluation base."""
# pylint: disable=import-error,protected-access
from unittest.mock import MagicMock, patch

from supervisor.const import CoreState
from supervisor.coresys import CoreSys
from supervisor.resolution.evaluations.operating_system import (
    SUPPORTED_OS,
    EvaluateOperatingSystem,
)


async def test_evaluation(coresys: CoreSys):
    """Test evaluation."""
    operating_system = EvaluateOperatingSystem(coresys)
    coresys.core.state = CoreState.SETUP

    assert operating_system.reason not in coresys.resolution.unsupported

    coresys.host._info = MagicMock(operating_system="unsupported")
    await operating_system()
    assert operating_system.reason in coresys.resolution.unsupported

    coresys.os._available = True
    await operating_system()
    assert operating_system.reason not in coresys.resolution.unsupported
    coresys.os._available = False

    coresys.host._info = MagicMock(operating_system=SUPPORTED_OS[0])
    await operating_system()
    assert operating_system.reason not in coresys.resolution.unsupported


async def test_did_run(coresys: CoreSys):
    """Test that the evaluation ran as expected."""
    operating_system = EvaluateOperatingSystem(coresys)
    should_run = operating_system.states
    should_not_run = [state for state in CoreState if state not in should_run]
    assert len(should_run) != 0
    assert len(should_not_run) != 0

    with patch(
        "supervisor.resolution.evaluations.operating_system.EvaluateOperatingSystem.evaluate",
        return_value=None,
    ) as evaluate:
        for state in should_run:
            coresys.core.state = state
            await operating_system()
            evaluate.assert_called_once()
            evaluate.reset_mock()

        for state in should_not_run:
            coresys.core.state = state
            await operating_system()
            evaluate.assert_not_called()
            evaluate.reset_mock()
