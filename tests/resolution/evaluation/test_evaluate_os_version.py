"""Test OS Version evaluation."""

from unittest.mock import PropertyMock, patch

from awesomeversion import AwesomeVersion
import pytest

from supervisor.const import CoreState
from supervisor.coresys import CoreSys
from supervisor.os.manager import OSManager
from supervisor.resolution.evaluations.os_version import EvaluateOSVersion


@pytest.mark.parametrize(
    "current,latest,expected",
    [
        ("10.0", "15.0", True),  # 5 major behind, should be unsupported
        ("10.0", "14.0", False),  # 4 major behind, should be supported
        ("10.2", "11.0", False),  # 1 major behind, supported
        ("10.4", "10.5", False),  # same major, supported
        ("10.5", "10.5", False),  # up to date, supported
        ("10.5", "10.6", False),  # same major, supported
        ("10.0", "13.3", False),  # 3 major behind, supported
        (None, "15.0", False),  # No current version info, check skipped
        ("2.0", None, False),  # No latest version info, check skipped
        (
            "9ccda431973acf17e4221850b08f3280b723df8d",
            "15.0",
            False,
        ),  # Dev setup running on a commit hash, check skipped
    ],
)
@pytest.mark.usefixtures("os_available")
async def test_os_version_evaluation(
    coresys: CoreSys, current: str | None, latest: str | None, expected: bool
):
    """Test evaluation logic on versions."""
    evaluation = EvaluateOSVersion(coresys)
    await coresys.core.set_state(CoreState.RUNNING)
    with (
        patch.object(
            OSManager,
            "version",
            new=PropertyMock(return_value=current and AwesomeVersion(current)),
        ),
        patch.object(
            OSManager,
            "latest_version",
            new=PropertyMock(return_value=latest and AwesomeVersion(latest)),
        ),
    ):
        assert evaluation.reason not in coresys.resolution.unsupported
        await evaluation()
        assert (evaluation.reason in coresys.resolution.unsupported) is expected


async def test_did_run(coresys: CoreSys):
    """Test that the evaluation ran as expected."""
    evaluation = EvaluateOSVersion(coresys)
    should_run = evaluation.states
    should_not_run = [state for state in CoreState if state not in should_run]
    assert len(should_run) != 0
    assert len(should_not_run) != 0

    with patch(
        "supervisor.resolution.evaluations.os_version.EvaluateOSVersion.evaluate",
        return_value=None,
    ) as evaluate:
        for state in should_run:
            await coresys.core.set_state(state)
            await evaluation()
            evaluate.assert_called_once()
            evaluate.reset_mock()

        for state in should_not_run:
            await coresys.core.set_state(state)
            await evaluation()
            evaluate.assert_not_called()
            evaluate.reset_mock()
