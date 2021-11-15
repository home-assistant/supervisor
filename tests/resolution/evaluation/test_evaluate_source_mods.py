"""Test evaluation base."""
# pylint: disable=import-error,protected-access
from unittest.mock import AsyncMock, patch

from supervisor.const import SupervisorState
from supervisor.coresys import CoreSys
from supervisor.exceptions import CodeNotaryError, CodeNotaryUntrusted
from supervisor.resolution.evaluations.source_mods import EvaluateSourceMods


async def test_evaluation(coresys: CoreSys):
    """Test evaluation."""
    sourcemods = EvaluateSourceMods(coresys)
    coresys.core.state = SupervisorState.RUNNING

    assert sourcemods.reason not in coresys.resolution.unsupported
    coresys.security.verify_own_content = AsyncMock(side_effect=CodeNotaryUntrusted)
    await sourcemods()
    assert sourcemods.reason in coresys.resolution.unsupported

    coresys.security.verify_own_content = AsyncMock(side_effect=CodeNotaryError)
    await sourcemods()
    assert sourcemods.reason not in coresys.resolution.unsupported

    coresys.security.verify_own_content = AsyncMock()
    await sourcemods()
    assert sourcemods.reason not in coresys.resolution.unsupported


async def test_did_run(coresys: CoreSys):
    """Test that the evaluation ran as expected."""
    sourcemods = EvaluateSourceMods(coresys)
    should_run = sourcemods.states
    should_not_run = [state for state in SupervisorState if state not in should_run]
    assert len(should_run) != 0
    assert len(should_not_run) != 0

    with patch(
        "supervisor.resolution.evaluations.source_mods.EvaluateSourceMods.evaluate",
        return_value=None,
    ) as evaluate:
        for state in should_run:
            coresys.core.state = state
            await sourcemods()
            evaluate.assert_called_once()
            evaluate.reset_mock()

        for state in should_not_run:
            coresys.core.state = state
            await sourcemods()
            evaluate.assert_not_called()
            evaluate.reset_mock()
