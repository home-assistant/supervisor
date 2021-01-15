"""Test core version check."""
# pylint: disable=import-error,protected-access
from unittest.mock import patch

from supervisor.const import CoreState
from supervisor.coresys import CoreSys
from supervisor.resolution.checks.core_version import CheckCoreVersion
from supervisor.resolution.const import IssueType


async def test_check(coresys: CoreSys, tmp_path):
    """Test check."""
    core_version = CheckCoreVersion(coresys)
    coresys.core.state = CoreState.RUNNING

    assert len(coresys.resolution.issues) == 0

    coresys.homeassistant._data["version"] = "2021.12.1"
    await core_version.run_check()
    assert len(coresys.resolution.issues) == 0

    coresys.homeassistant._data["version"] = "2021.1.2"
    await core_version.run_check()
    assert len(coresys.resolution.issues) == 0

    with patch("supervisor.resolution.checks.core_version.CC_PATH", tmp_path):
        await core_version.run_check()

    assert coresys.resolution.issues[-1].type == IssueType.VERSION


async def test_approve(coresys: CoreSys, tmp_path):
    """Test check."""
    core_version = CheckCoreVersion(coresys)
    coresys.core.state = CoreState.RUNNING
    coresys.homeassistant._data["version"] = None
    assert await core_version.approve_check()

    coresys.homeassistant._data["version"] = "2021.1.3"
    assert not await core_version.approve_check()

    coresys.homeassistant._data["version"] = "2021.1.2"
    assert not await core_version.approve_check()

    with patch("supervisor.resolution.checks.core_version.CC_PATH", tmp_path):
        assert await core_version.approve_check()


async def test_did_run(coresys: CoreSys):
    """Test that the check ran as expected."""
    core_version = CheckCoreVersion(coresys)
    should_run = core_version.states
    should_not_run = [state for state in CoreState if state not in should_run]
    assert len(should_run) != 0
    assert len(should_not_run) != 0

    with patch(
        "supervisor.resolution.checks.core_version.CheckCoreVersion.run_check",
        return_value=None,
    ) as check:
        for state in should_run:
            coresys.core.state = state
            await core_version()
            check.assert_called_once()
            check.reset_mock()

        for state in should_not_run:
            coresys.core.state = state
            await core_version()
            check.assert_not_called()
            check.reset_mock()
