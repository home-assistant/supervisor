"""Test check."""
# pylint: disable=import-error,protected-access
from unittest.mock import patch

import pytest

from supervisor.const import CoreState
from supervisor.coresys import CoreSys
from supervisor.exceptions import ResolutionNotFound
from supervisor.resolution.const import IssueType
from supervisor.resolution.validate import get_valid_modules


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
    coresys.security.content_trust = False

    with patch("shutil.disk_usage", return_value=(1, 1, 1)):
        await coresys.resolution.check.check_system()

    assert coresys.resolution.issues[-1].type == IssueType.FREE_SPACE


async def test_if_check_cleanup_issue(coresys: CoreSys):
    """Test check for setup."""
    coresys.core.state = CoreState.RUNNING
    coresys.security.content_trust = False

    with patch("shutil.disk_usage", return_value=(1, 1, 1)):
        await coresys.resolution.check.check_system()

    assert coresys.resolution.issues[-1].type == IssueType.FREE_SPACE

    with patch("shutil.disk_usage", return_value=(42, 42, 2 * (1024.0**3))):
        await coresys.resolution.check.check_system()

    assert len(coresys.resolution.issues) == 0


async def test_enable_disable_checks(coresys: CoreSys):
    """Test enable and disable check."""
    coresys.core.state = CoreState.RUNNING
    free_space = coresys.resolution.check.get("free_space")

    # Ensure the check was enabled
    assert free_space.enabled

    free_space.enabled = False
    assert not free_space.enabled

    with patch(
        "supervisor.resolution.checks.free_space.CheckFreeSpace.run_check",
        return_value=False,
    ) as free_space:
        await coresys.resolution.check.check_system()
        free_space.assert_not_called()

    free_space.enabled = True
    assert free_space.enabled


async def test_get_checks(coresys: CoreSys):
    """Test get check with slug."""

    with pytest.raises(ResolutionNotFound):
        coresys.resolution.check.get("does_not_exsist")

    assert coresys.resolution.check.get("free_space")


def test_dynamic_check_loader(coresys: CoreSys):
    """Test dynamic check loader, this ensures that all checks have defined a setup function."""
    coresys.resolution.check._load()
    for check in get_valid_modules("checks"):
        assert check in coresys.resolution.check._checks
