"""Test core version check."""
# pylint: disable=import-error,protected-access
from pathlib import Path
from unittest.mock import patch

from awesomeversion import AwesomeVersion

from supervisor.const import CoreState
from supervisor.coresys import CoreSys
from supervisor.resolution.checks.core_security import CheckCoreSecurity
from supervisor.resolution.const import IssueType


async def test_check(coresys: CoreSys, tmp_path):
    """Test check."""
    with patch("supervisor.config.CoreConfig.path_homeassistant", tmp_path):
        core_security = CheckCoreSecurity(coresys)
        coresys.core.state = CoreState.RUNNING

        assert len(coresys.resolution.issues) == 0

        coresys.homeassistant._data["version"] = AwesomeVersion("2021.12.1")
        await core_security.run_check()
        assert len(coresys.resolution.issues) == 0

        coresys.homeassistant._data["version"] = AwesomeVersion("landingpage")
        await core_security.run_check()
        assert len(coresys.resolution.issues) == 0

        coresys.homeassistant._data["version"] = AwesomeVersion(None)
        await core_security.run_check()
        assert len(coresys.resolution.issues) == 0

        coresys.homeassistant._data["version"] = AwesomeVersion("2021.1.2")
        await core_security.run_check()
        assert len(coresys.resolution.issues) == 0

        Path(coresys.config.path_homeassistant, "custom_components").mkdir(parents=True)
        await core_security.run_check()

        assert coresys.resolution.issues[-1].type == IssueType.SECURITY


async def test_approve(coresys: CoreSys, tmp_path):
    """Test check."""
    with patch("supervisor.config.CoreConfig.path_homeassistant", tmp_path):
        core_security = CheckCoreSecurity(coresys)
        coresys.core.state = CoreState.RUNNING
        coresys.homeassistant._data["version"] = None
        assert await core_security.approve_check()

        coresys.homeassistant._data["version"] = AwesomeVersion("2021.1.3")
        assert not await core_security.approve_check()

        coresys.homeassistant._data["version"] = AwesomeVersion("2021.1.2")
        assert not await core_security.approve_check()

        Path(coresys.config.path_homeassistant, "custom_components").mkdir(parents=True)
        assert await core_security.approve_check()


async def test_did_run(coresys: CoreSys):
    """Test that the check ran as expected."""
    core_security = CheckCoreSecurity(coresys)
    should_run = core_security.states
    should_not_run = [state for state in CoreState if state not in should_run]
    assert len(should_run) != 0
    assert len(should_not_run) != 0

    with patch(
        "supervisor.resolution.checks.core_security.CheckCoreSecurity.run_check",
        return_value=None,
    ) as check:
        for state in should_run:
            coresys.core.state = state
            await core_security()
            check.assert_called_once()
            check.reset_mock()

        for state in should_not_run:
            coresys.core.state = state
            await core_security()
            check.assert_not_called()
            check.reset_mock()
