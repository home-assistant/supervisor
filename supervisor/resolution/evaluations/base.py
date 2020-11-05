"""Baseclass for system evaluations."""
import logging
from typing import List

from ...const import CoreState
from ...coresys import CoreSys, CoreSysAttributes
from ..const import UnsupportedReason

_LOGGER: logging.Logger = logging.getLogger(__name__)


class EvaluateBase(CoreSysAttributes):
    """Baseclass for evaluation."""

    def __init__(self, coresys: CoreSys) -> None:
        """Initialize the evaluation class."""
        self.coresys = coresys

    async def __call__(self) -> None:
        """Execute the evaluation."""
        if self.sys_core.state not in self.states:
            return
        if await self.evaluate():
            if self.reason not in self.sys_resolution.unsupported:
                self.sys_resolution.unsupported = self.reason
                _LOGGER.warning(
                    "%s (more-info: https://www.home-assistant.io/more-info/unsupported/%s)",
                    self.on_failure,
                    self.reason.value,
                )
        else:
            if self.reason in self.sys_resolution.unsupported:
                _LOGGER.info("Clearing %s as reason for unsupported", self.reason)
                await self.sys_resolution.dismiss_unsupported(self.reason)

    async def evaluate(self):
        """Run evaluation."""
        raise NotImplementedError

    @property
    def reason(self) -> UnsupportedReason:
        """Return a UnsupportedReason enum."""
        raise NotImplementedError

    @property
    def on_failure(self) -> str:
        """Return a string that is printed when self.evaluate is False."""
        raise NotImplementedError

    @property
    def states(self) -> List[CoreState]:
        """Return a list of valid states when this evaluation can run."""
        return []
