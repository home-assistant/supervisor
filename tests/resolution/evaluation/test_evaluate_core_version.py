"""Test Core Version evaluation."""

from datetime import datetime
from unittest.mock import PropertyMock, patch

from awesomeversion import AwesomeVersion
import pytest

from supervisor.const import CoreState
from supervisor.coresys import CoreSys
from supervisor.homeassistant.module import HomeAssistant
from supervisor.resolution.evaluations.core_version import EvaluateCoreVersion


@pytest.mark.parametrize(
    "current,expected",
    [
        ("2022.1.0", True),  # More than 2 years old, should be unsupported
        ("2023.12.0", False),  # Less than 2 years old, should be supported
        (f"{datetime.now().year}.1", False),  # Current year, supported
        (f"{datetime.now().year - 1}.12", False),  # 1 year old, supported
        (f"{datetime.now().year - 2}.1", True),  # 2 years old, unsupported
        (f"{datetime.now().year - 3}.1", True),  # 3 years old, unsupported
        ("2021.6.0", True),  # Very old version, unsupported
        (None, False),  # No current version info, check skipped
    ],
)
async def test_core_version_evaluation(
    coresys: CoreSys, current: str | None, expected: bool
):
    """Test evaluation logic on Core versions."""
    evaluation = EvaluateCoreVersion(coresys)
    await coresys.core.set_state(CoreState.RUNNING)

    with (
        patch.object(
            HomeAssistant,
            "version",
            new=PropertyMock(return_value=current and AwesomeVersion(current)),
        ),
        patch.object(
            HomeAssistant,
            "latest_version",
            new=PropertyMock(
                return_value=AwesomeVersion("2024.12.0")
            ),  # Mock latest version
        ),
    ):
        assert evaluation.reason not in coresys.resolution.unsupported
        await evaluation()
        assert (evaluation.reason in coresys.resolution.unsupported) is expected


async def test_core_version_evaluation_no_latest(coresys: CoreSys):
    """Test evaluation when no latest version is available."""
    evaluation = EvaluateCoreVersion(coresys)
    await coresys.core.set_state(CoreState.RUNNING)

    with (
        patch.object(
            HomeAssistant,
            "version",
            new=PropertyMock(return_value=AwesomeVersion("2022.1.0")),
        ),
        patch.object(
            HomeAssistant,
            "latest_version",
            new=PropertyMock(return_value=None),
        ),
    ):
        assert evaluation.reason not in coresys.resolution.unsupported
        await evaluation()
        assert evaluation.reason not in coresys.resolution.unsupported


async def test_core_version_invalid_format(coresys: CoreSys):
    """Test evaluation with invalid version format."""
    evaluation = EvaluateCoreVersion(coresys)
    await coresys.core.set_state(CoreState.RUNNING)

    with (
        patch.object(
            HomeAssistant,
            "version",
            new=PropertyMock(return_value=AwesomeVersion("invalid.version")),
        ),
        patch.object(
            HomeAssistant,
            "latest_version",
            new=PropertyMock(return_value=AwesomeVersion("2024.12.0")),
        ),
    ):
        assert evaluation.reason not in coresys.resolution.unsupported
        await evaluation()
        # Should handle gracefully and not mark as unsupported
        assert evaluation.reason not in coresys.resolution.unsupported


async def test_did_run(coresys: CoreSys):
    """Test that the evaluation ran as expected."""
    evaluation = EvaluateCoreVersion(coresys)
    should_run = evaluation.states
    should_not_run = [state for state in CoreState if state not in should_run]
    assert len(should_run) != 0
    assert len(should_not_run) != 0

    with patch(
        "supervisor.resolution.evaluations.core_version.EvaluateCoreVersion.evaluate",
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
