"""Test evaluation base."""
# pylint: disable=import-error,protected-access
from unittest.mock import patch

from supervisor.const import CoreState
from supervisor.coresys import CoreSys
from supervisor.resolution.checks.free_space import CheckFreeSpace
from supervisor.resolution.const import IssueType


async def test_check(coresys: CoreSys):
    """Test check."""
    free_space = CheckFreeSpace(coresys)
    coresys.core.state = CoreState.RUNNING

    assert len(coresys.resolution.issues) == 0

    with patch("shutil.disk_usage", return_value=(42, 42, 2 * (1024.0 ** 3))):
        await free_space.run_check()

    assert len(coresys.resolution.issues) == 0

    with patch("shutil.disk_usage", return_value=(1, 1, 1)):
        await free_space.run_check()

    assert coresys.resolution.issues[-1].type == IssueType.FREE_SPACE


async def test_did_run(coresys: CoreSys):
    """Test that the check ran as expected."""
    free_space = CheckFreeSpace(coresys)
    should_run = free_space.states
    should_not_run = [state for state in CoreState if state not in should_run]
    assert len(should_run) != 0
    assert len(should_not_run) != 0

    with patch(
        "supervisor.resolution.checks.free_space.CheckFreeSpace.run_check",
        return_value=None,
    ) as check:
        for state in should_run:
            coresys.core.state = state
            await free_space()
            check.assert_called_once()
            check.reset_mock()

        for state in should_not_run:
            coresys.core.state = state
            await free_space()
            check.assert_not_called()
            check.reset_mock()
