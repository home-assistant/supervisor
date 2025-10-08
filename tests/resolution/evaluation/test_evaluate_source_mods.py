"""Test evaluation base."""

# pylint: disable=import-error,protected-access
from unittest.mock import patch

from supervisor.const import CoreState
from supervisor.coresys import CoreSys
from supervisor.resolution.evaluations.source_mods import EvaluateSourceMods


async def test_evaluation(coresys: CoreSys):
    """Test evaluation - CodeNotary removed."""
    sourcemods = EvaluateSourceMods(coresys)
    await coresys.core.set_state(CoreState.RUNNING)

    # CodeNotary checking removed, evaluation always returns False now
    assert sourcemods.reason not in coresys.resolution.unsupported
    await sourcemods()
    assert sourcemods.reason not in coresys.resolution.unsupported


async def test_did_run(coresys: CoreSys):
    """Test that the evaluation ran as expected."""
    sourcemods = EvaluateSourceMods(coresys)
    should_run = sourcemods.states
    should_not_run = [state for state in CoreState if state not in should_run]
    assert len(should_run) != 0
    assert len(should_not_run) != 0

    with patch(
        "supervisor.resolution.evaluations.source_mods.EvaluateSourceMods.evaluate",
        return_value=None,
    ) as evaluate:
        for state in should_run:
            await coresys.core.set_state(state)
            await sourcemods()
            evaluate.assert_called_once()
            evaluate.reset_mock()

        for state in should_not_run:
            await coresys.core.set_state(state)
            await sourcemods()
            evaluate.assert_not_called()
            evaluate.reset_mock()


async def test_evaluation_error(coresys: CoreSys):
    """Test error reading file during evaluation - CodeNotary removed."""
    sourcemods = EvaluateSourceMods(coresys)
    await coresys.core.set_state(CoreState.RUNNING)

    # CodeNotary checking removed, evaluation always returns False now
    assert sourcemods.reason not in coresys.resolution.unsupported
    await sourcemods()
    assert sourcemods.reason not in coresys.resolution.unsupported
