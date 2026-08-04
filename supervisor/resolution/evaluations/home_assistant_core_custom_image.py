"""Evaluation class for Core image."""

from ...const import CoreState
from ...coresys import CoreSys
from ..const import UnsupportedReason
from .base import EvaluateBase


def setup(coresys: CoreSys) -> EvaluateBase:
    """Initialize evaluation-setup function."""
    return EvaluateHomeAssistantCoreCustomImage(coresys)


class EvaluateHomeAssistantCoreCustomImage(EvaluateBase):
    """Evaluate the Home Assistant Core image."""

    @property
    def reason(self) -> UnsupportedReason:
        """Return a UnsupportedReason enum."""
        return UnsupportedReason.HOME_ASSISTANT_CORE_CUSTOM_IMAGE

    @property
    def on_failure(self) -> str:
        """Return a string that is printed when self.evaluate is True."""
        return f"Home Assistant Core is using the non-default image '{self.sys_homeassistant.image}'!"

    @property
    def states(self) -> list[CoreState]:
        """Return a list of valid states when this evaluation can run."""
        return [CoreState.RUNNING, CoreState.SETUP]

    async def evaluate(self) -> bool:
        """Run evaluation."""
        return self.sys_homeassistant.image != self.sys_homeassistant.default_image
