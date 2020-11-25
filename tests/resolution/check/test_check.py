"""Test check."""
# pylint: disable=import-error
from unittest.mock import patch

from supervisor.const import CoreState
from supervisor.coresys import CoreSys
from supervisor.resolution.const import IssueType


async def test_check_setup(coresys: CoreSys):
    """Test check for setup."""
    coresys.core.state = CoreState.SETUP
    with patch(
        "supervisor.resolution.checks.free_space.CheckFreeSpace.run_check",
        return_value=False,
    ) as free_space:
        await coresys.resolution.check.check_system()
        free_space.assert_not_called()


async def test_check_running(coresys: CoreSys):
    """Test check for setup."""
    coresys.core.state = CoreState.RUNNING
    with patch(
        "supervisor.resolution.checks.free_space.CheckFreeSpace.run_check",
        return_value=False,
    ) as free_space:
        await coresys.resolution.check.check_system()
        free_space.assert_called_once()


async def test_if_check_make_issue(coresys: CoreSys):
    """Test check for setup."""
    coresys.core.state = CoreState.RUNNING

    with patch("shutil.disk_usage", return_value=(1, 1, 1)):
        await coresys.resolution.check.check_system()

    assert coresys.resolution.issues[-1].type == IssueType.FREE_SPACE
