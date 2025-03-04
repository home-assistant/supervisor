"""Test check free space fixup."""

# pylint: disable=import-error,protected-access
from unittest.mock import MagicMock, PropertyMock, patch

import pytest

from supervisor.backups.const import BackupType
from supervisor.const import CoreState
from supervisor.coresys import CoreSys
from supervisor.resolution.checks.free_space import CheckFreeSpace
from supervisor.resolution.const import IssueType, SuggestionType


@pytest.fixture(name="suggestion")
async def fixture_suggestion(
    coresys: CoreSys, request: pytest.FixtureRequest
) -> SuggestionType | None:
    """Set up test for suggestion."""
    if request.param == SuggestionType.CLEAR_FULL_BACKUP:
        backup = MagicMock()
        backup.sys_type = BackupType.FULL
        with patch.object(
            type(coresys.backups),
            "list_backups",
            new=PropertyMock(return_value=[backup, backup, backup]),
        ):
            yield SuggestionType.CLEAR_FULL_BACKUP
    else:
        yield request.param


async def test_base(coresys: CoreSys):
    """Test check basics."""
    free_space = CheckFreeSpace(coresys)
    assert free_space.slug == "free_space"
    assert free_space.enabled


@pytest.mark.parametrize(
    "suggestion",
    [None, SuggestionType.CLEAR_FULL_BACKUP],
    indirect=True,
)
async def test_check(coresys: CoreSys, suggestion: SuggestionType | None):
    """Test check."""
    free_space = CheckFreeSpace(coresys)
    await coresys.core.set_state(CoreState.RUNNING)

    assert len(coresys.resolution.issues) == 0

    with patch("shutil.disk_usage", return_value=(42, 42, 2 * (1024.0**3))):
        await free_space.run_check()

    assert len(coresys.resolution.issues) == 0

    with patch("shutil.disk_usage", return_value=(1, 1, 1)):
        await free_space.run_check()

    assert coresys.resolution.issues[-1].type == IssueType.FREE_SPACE

    if suggestion:
        assert coresys.resolution.suggestions[-1].type == suggestion
    else:
        assert len(coresys.resolution.suggestions) == 0


async def test_approve(coresys: CoreSys):
    """Test check."""
    free_space = CheckFreeSpace(coresys)
    await coresys.core.set_state(CoreState.RUNNING)

    with patch("shutil.disk_usage", return_value=(1, 1, 1)):
        assert await free_space.approve_check()

    with patch("shutil.disk_usage", return_value=(42, 42, 2 * (1024.0**3))):
        assert not await free_space.approve_check()


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
            await coresys.core.set_state(state)
            await free_space()
            check.assert_called_once()
            check.reset_mock()

        for state in should_not_run:
            await coresys.core.set_state(state)
            await free_space()
            check.assert_not_called()
            check.reset_mock()
