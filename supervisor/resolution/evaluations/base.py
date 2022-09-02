"""Baseclass for system evaluations."""
from abc import ABC, abstractmethod
import logging

from ...const import CoreState
from ...coresys import CoreSys, CoreSysAttributes
from ..const import UnsupportedReason

_LOGGER: logging.Logger = logging.getLogger(__name__)


class EvaluateBase(ABC, CoreSysAttributes):
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
                self.sys_resolution.dismiss_unsupported(self.reason)

    @abstractmethod
    async def evaluate(self) -> bool:
        """Run evaluation, return true if system fails."""

    @property
    @abstractmethod
    def reason(self) -> UnsupportedReason:
        """Return a UnsupportedReason enum."""

    @property
    def slug(self) -> str:
        """Return the check slug."""
        return self.__class__.__module__.rsplit(".", maxsplit=1)[-1]

    @property
    @abstractmethod
    def on_failure(self) -> str:
        """Return a string that is printed when system fails this evaluation."""

    @property
    def states(self) -> list[CoreState]:
        """Return a list of valid states when this evaluation can run."""
        return []
