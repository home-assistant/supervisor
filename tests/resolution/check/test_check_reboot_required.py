"""Test check for reboot required."""

from datetime import timedelta
from unittest.mock import patch

import pytest

from supervisor.const import CoreState
from supervisor.coresys import CoreSys
from supervisor.hardware.helper import HwHelper
from supervisor.resolution.checks.reboot_required import CheckRebootRequired
from supervisor.resolution.const import ContextType, IssueType, SuggestionType
from supervisor.resolution.data import Issue, Suggestion
from supervisor.utils.dt import utcnow

REBOOT_REQUIRED = Issue(IssueType.REBOOT_REQUIRED, ContextType.SYSTEM)
EXECUTE_REBOOT = Suggestion(SuggestionType.EXECUTE_REBOOT, ContextType.SYSTEM)


@pytest.fixture(name="reboot_required_issue")
def fixture_reboot_required_issue(coresys: CoreSys) -> Issue:
    """Add a reboot required issue."""
    coresys.resolution.add_issue(REBOOT_REQUIRED, [SuggestionType.EXECUTE_REBOOT])
    return REBOOT_REQUIRED


async def test_base(coresys: CoreSys):
    """Test check basics."""
    reboot_required = CheckRebootRequired(coresys)
    assert reboot_required.slug == "reboot_required"
    assert reboot_required.enabled


@pytest.mark.usefixtures("reboot_required_issue")
async def test_run_check_does_not_create_issue(coresys: CoreSys):
    """Test the check cannot detect a pending reboot by itself."""
    coresys.resolution.dismiss_issue(REBOOT_REQUIRED)

    await CheckRebootRequired(coresys).run_check()

    assert coresys.resolution.issues == []
    assert coresys.resolution.suggestions == []


@pytest.mark.parametrize(
    ("boot_offset", "expected"),
    [
        pytest.param(timedelta(0), True, id="supervisor_restart"),
        pytest.param(timedelta(hours=1), False, id="host_reboot"),
    ],
)
async def test_approve(
    coresys: CoreSys,
    reboot_required_issue: Issue,
    boot_offset: timedelta,
    expected: bool,
):
    """Test issue is only kept while the host has not rebooted since."""
    stored_boot = utcnow()
    coresys.config.last_boot = stored_boot

    with patch.object(HwHelper, "last_boot", return_value=stored_boot + boot_offset):
        assert (
            await CheckRebootRequired(coresys).approve_check(reboot_required_issue)
            is expected
        )


async def test_approve_unknown_boot_time(
    coresys: CoreSys, reboot_required_issue: Issue, caplog: pytest.LogCaptureFixture
):
    """Test issue is kept when the last boot time cannot be determined."""
    with patch.object(HwHelper, "last_boot", return_value=None):
        assert await CheckRebootRequired(coresys).approve_check(reboot_required_issue)

    assert "Can't determine last boot time, keeping issue" in caplog.text


@pytest.mark.parametrize(
    ("state", "boot_offset", "expected_issues", "expected_suggestions"),
    [
        pytest.param(
            CoreState.SETUP, timedelta(hours=1), [], [], id="setup_host_reboot"
        ),
        pytest.param(
            CoreState.SETUP,
            timedelta(0),
            [REBOOT_REQUIRED],
            [EXECUTE_REBOOT],
            id="setup_supervisor_restart",
        ),
        pytest.param(
            CoreState.RUNNING,
            timedelta(hours=1),
            [REBOOT_REQUIRED],
            [EXECUTE_REBOOT],
            id="running_not_checked",
        ),
    ],
)
@pytest.mark.usefixtures("reboot_required_issue")
async def test_check(
    coresys: CoreSys,
    state: CoreState,
    boot_offset: timedelta,
    expected_issues: list[Issue],
    expected_suggestions: list[Suggestion],
):
    """Test check dismisses the issue on Supervisor startup after a host reboot."""
    stored_boot = utcnow()
    coresys.config.last_boot = stored_boot
    await coresys.core.set_state(state)

    with patch.object(HwHelper, "last_boot", return_value=stored_boot + boot_offset):
        await CheckRebootRequired(coresys)()

    assert coresys.resolution.issues == expected_issues
    assert coresys.resolution.suggestions == expected_suggestions
