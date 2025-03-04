"""Test core version check."""

# pylint: disable=import-error,protected-access
from datetime import timedelta
from unittest.mock import patch

from supervisor.backups.backup import Backup
from supervisor.const import ATTR_DATE, CoreState
from supervisor.coresys import CoreSys
from supervisor.resolution.checks.backups import CheckBackups
from supervisor.resolution.const import IssueType
from supervisor.utils.dt import utcnow


async def test_base(coresys: CoreSys):
    """Test check basics."""
    core_security = CheckBackups(coresys)
    assert core_security.slug == "backups"
    assert core_security.enabled


async def test_check_no_backups(coresys: CoreSys):
    """Test check creates issue with no backups."""
    backups = CheckBackups(coresys)
    await coresys.core.set_state(CoreState.RUNNING)

    assert len(coresys.resolution.issues) == 0
    await backups.run_check()
    assert coresys.resolution.issues[-1].type == IssueType.NO_CURRENT_BACKUP
    assert await backups.approve_check()


async def test_check_only_partial_backups(
    coresys: CoreSys, mock_partial_backup: Backup
):
    """Test check creates issue with only partial backups."""
    backups = CheckBackups(coresys)
    await coresys.core.set_state(CoreState.RUNNING)

    assert len(coresys.resolution.issues) == 0
    await backups.run_check()
    assert coresys.resolution.issues[-1].type == IssueType.NO_CURRENT_BACKUP
    assert await backups.approve_check()


async def test_check_with_backup(coresys: CoreSys, mock_full_backup: Backup):
    """Test check only creates issue if full backup not current."""
    backups = CheckBackups(coresys)
    await coresys.core.set_state(CoreState.RUNNING)

    assert len(coresys.resolution.issues) == 0
    await backups.run_check()
    assert len(coresys.resolution.issues) == 0
    assert not await backups.approve_check()

    mock_full_backup._data[ATTR_DATE] = (utcnow() - timedelta(days=30)).isoformat()
    await backups.run_check()
    assert coresys.resolution.issues[-1].type == IssueType.NO_CURRENT_BACKUP
    assert await backups.approve_check()


async def test_did_run(coresys: CoreSys):
    """Test that the check ran as expected."""
    backups = CheckBackups(coresys)
    should_run = backups.states
    should_not_run = [state for state in CoreState if state not in should_run]
    assert len(should_run) != 0
    assert len(should_not_run) != 0

    with patch(
        "supervisor.resolution.checks.backups.CheckBackups.run_check",
        return_value=False,
    ) as check:
        for state in should_run:
            await coresys.core.set_state(state)
            await backups()
            check.assert_called_once()
            check.reset_mock()

        for state in should_not_run:
            await coresys.core.set_state(state)
            await backups()
            check.assert_not_called()
            check.reset_mock()
