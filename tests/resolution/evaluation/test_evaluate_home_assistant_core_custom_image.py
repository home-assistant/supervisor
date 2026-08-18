"""Test Core image evaluation."""

from unittest.mock import patch

import pytest

from supervisor.const import CoreState
from supervisor.coresys import CoreSys
from supervisor.resolution.evaluations.home_assistant_core_custom_image import (
    EvaluateHomeAssistantCoreCustomImage,
)


@pytest.mark.parametrize(
    ("image", "expected"),
    [
        (None, False),  # Unset, default image is used
        ("ghcr.io/home-assistant/qemux86-64-homeassistant", False),  # Default image
        ("myorg/qemux86-64-homeassistant", True),  # Fork on another registry
        ("ghcr.io/myorg/qemux86-64-homeassistant", True),  # Fork on same registry
    ],
)
async def test_core_image_evaluation(
    coresys: CoreSys, image: str | None, expected: bool
):
    """Test evaluation logic on Core image."""
    evaluation = EvaluateHomeAssistantCoreCustomImage(coresys)
    await coresys.core.set_state(CoreState.RUNNING)

    coresys.homeassistant.set_image(image)

    assert evaluation.reason not in coresys.resolution.unsupported
    await evaluation()
    assert (evaluation.reason in coresys.resolution.unsupported) is expected


async def test_core_image_evaluation_resolves(coresys: CoreSys):
    """Test the unsupported state is removed when the image is set back."""
    evaluation = EvaluateHomeAssistantCoreCustomImage(coresys)
    await coresys.core.set_state(CoreState.RUNNING)

    coresys.homeassistant.set_image("myorg/qemux86-64-homeassistant")
    await evaluation()
    assert evaluation.reason in coresys.resolution.unsupported

    coresys.homeassistant.set_image(None)
    await evaluation()
    assert evaluation.reason not in coresys.resolution.unsupported


async def test_did_run(coresys: CoreSys):
    """Test that the evaluation ran as expected."""
    evaluation = EvaluateHomeAssistantCoreCustomImage(coresys)
    should_run = evaluation.states
    should_not_run = [state for state in CoreState if state not in should_run]
    assert len(should_run) != 0
    assert len(should_not_run) != 0

    with patch(
        "supervisor.resolution.evaluations.home_assistant_core_custom_image.EvaluateHomeAssistantCoreCustomImage.evaluate",
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
