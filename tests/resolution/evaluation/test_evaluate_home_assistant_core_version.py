"""Test Core Version evaluation."""

from unittest.mock import PropertyMock, patch

from awesomeversion import AwesomeVersion
import pytest

from supervisor.const import CoreState
from supervisor.coresys import CoreSys
from supervisor.homeassistant.const import LANDINGPAGE
from supervisor.homeassistant.module import HomeAssistant
from supervisor.resolution.evaluations.home_assistant_core_version import (
    EvaluateHomeAssistantCoreVersion,
)


@pytest.mark.parametrize(
    "current,latest,expected",
    [
        ("2022.1.0", "2024.12.0", True),  # More than 24 months behind, unsupported
        ("2023.1.0", "2024.12.0", False),  # Less than 24 months behind, supported
        ("2024.1.0", "2024.12.0", False),  # Recent version, supported
        ("2024.12.0", "2024.12.0", False),  # Same as latest, supported
        ("2024.11.0", "2024.12.0", False),  # 1 month behind, supported
        (
            "2022.12.0",
            "2024.12.0",
            False,
        ),  # Exactly 24 months behind, supported (boundary)
        ("2022.11.0", "2024.12.0", True),  # More than 24 months behind, unsupported
        ("2021.6.0", "2024.12.0", True),  # Very old version, unsupported
        ("0.116.4", "2024.12.0", True),  # Old version scheme, should be unsupported
        ("0.118.1", "2024.12.0", True),  # Old version scheme, should be unsupported
        ("landingpage", "2024.12.0", False),  # Landingpage version, should be supported
        (None, "2024.12.0", False),  # No current version info, check skipped
        ("2024.1.0", None, False),  # No latest version info, check skipped
    ],
)
async def test_core_version_evaluation(
    coresys: CoreSys, current: str | None, latest: str | None, expected: bool
):
    """Test evaluation logic on Core versions."""
    evaluation = EvaluateHomeAssistantCoreVersion(coresys)
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
            new=PropertyMock(return_value=latest and AwesomeVersion(latest)),
        ),
    ):
        assert evaluation.reason not in coresys.resolution.unsupported
        await evaluation()
        assert (evaluation.reason in coresys.resolution.unsupported) is expected


async def test_core_version_evaluation_no_latest(coresys: CoreSys):
    """Test evaluation when no latest version is available."""
    evaluation = EvaluateHomeAssistantCoreVersion(coresys)
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
        # Without latest version info, evaluation should be skipped (not run)
        assert evaluation.reason not in coresys.resolution.unsupported


async def test_core_version_invalid_format(coresys: CoreSys):
    """Test evaluation with invalid version format."""
    evaluation = EvaluateHomeAssistantCoreVersion(coresys)
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
        # Invalid/non-parseable versions should be marked as unsupported
        assert evaluation.reason in coresys.resolution.unsupported


async def test_core_version_landingpage(coresys: CoreSys):
    """Test evaluation with landingpage version."""
    evaluation = EvaluateHomeAssistantCoreVersion(coresys)
    await coresys.core.set_state(CoreState.RUNNING)

    with (
        patch.object(
            HomeAssistant,
            "version",
            new=PropertyMock(return_value=LANDINGPAGE),
        ),
        patch.object(
            HomeAssistant,
            "latest_version",
            new=PropertyMock(return_value=AwesomeVersion("2024.12.0")),
        ),
    ):
        assert evaluation.reason not in coresys.resolution.unsupported
        await evaluation()
        # Landingpage should never be marked as unsupported
        assert evaluation.reason not in coresys.resolution.unsupported


async def test_did_run(coresys: CoreSys):
    """Test that the evaluation ran as expected."""
    evaluation = EvaluateHomeAssistantCoreVersion(coresys)
    should_run = evaluation.states
    should_not_run = [state for state in CoreState if state not in should_run]
    assert len(should_run) != 0
    assert len(should_not_run) != 0

    with patch(
        "supervisor.resolution.evaluations.home_assistant_core_version.EvaluateHomeAssistantCoreVersion.evaluate",
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
