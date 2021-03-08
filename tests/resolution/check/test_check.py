"""Test check."""
# pylint: disable=import-error,protected-access
from unittest.mock import patch

import pytest

from supervisor.const import CoreState
from supervisor.coresys import CoreSys
from supervisor.exceptions import ResolutionError
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


async def test_if_check_cleanup_issue(coresys: CoreSys):
    """Test check for setup."""
    coresys.core.state = CoreState.RUNNING

    with patch("shutil.disk_usage", return_value=(1, 1, 1)):
        await coresys.resolution.check.check_system()

    assert coresys.resolution.issues[-1].type == IssueType.FREE_SPACE

    with patch("shutil.disk_usage", return_value=(42, 42, 2 * (1024.0 ** 3))):
        await coresys.resolution.check.check_system()

    assert len(coresys.resolution.issues) == 0


async def test_enable_disable_checks(coresys: CoreSys):
    """Test enable and disable check."""
    coresys.core.state = CoreState.RUNNING
    # Ensure the check was enabled
    assert coresys.resolution.check._get_check("free_space").enabled

    coresys.resolution.check.disable("free_space")
    assert not coresys.resolution.check._get_check("free_space").enabled

    with patch(
        "supervisor.resolution.checks.free_space.CheckFreeSpace.run_check",
        return_value=False,
    ) as free_space:
        await coresys.resolution.check.check_system()
        free_space.assert_not_called()

    coresys.resolution.check.enable("free_space")
    assert coresys.resolution.check._get_check("free_space").enabled

    with pytest.raises(ResolutionError):
        coresys.resolution.check.enable("does_not_exsist")

    with pytest.raises(ResolutionError):
        coresys.resolution.check.disable("core_security")
