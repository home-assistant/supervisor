"""Evaluation class for Content Trust."""
import logging
from pathlib import Path
from typing import List

from ...const import CoreState
from ...coresys import CoreSys
from ...exceptions import CodeNotaryError, CodeNotaryUntrusted
from ..const import UnsupportedReason
from .base import EvaluateBase

_SUPERVISOR_SOURCE = Path("/usr/src/supervisor")
_LOGGER: logging.Logger = logging.getLogger(__name__)


def setup(coresys: CoreSys) -> EvaluateBase:
    """Initialize evaluation-setup function."""
    return EvaluateSourceMods(coresys)


class EvaluateSourceMods(EvaluateBase):
    """Evaluate supervisor source modifications."""

    @property
    def reason(self) -> UnsupportedReason:
        """Return a UnsupportedReason enum."""
        return UnsupportedReason.SOURCE_MODS

    @property
    def on_failure(self) -> str:
        """Return a string that is printed when self.evaluate is False."""
        return "System detect unauthorized source code modifications."

    @property
    def states(self) -> List[CoreState]:
        """Return a list of valid states when this evaluation can run."""
        return [CoreState.RUNNING]

    async def evaluate(self) -> None:
        """Run evaluation."""
        if not self.sys_config.content_trust:
            _LOGGER.warning("Disabled content-trust, skipping evaluation")
            return

        try:
            await self.sys_verify_content(path=_SUPERVISOR_SOURCE)
        except CodeNotaryUntrusted:
            return True
        except CodeNotaryError:
            pass

        return False
