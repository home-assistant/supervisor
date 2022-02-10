"""Evaluation class for Content Trust."""
import logging
from pathlib import Path

from ...const import CoreState
from ...coresys import CoreSys
from ...exceptions import CodeNotaryError, CodeNotaryUntrusted
from ...utils.codenotary import calc_checksum_path_sourcecode
from ..const import UnsupportedReason
from .base import EvaluateBase

_SUPERVISOR_SOURCE = Path("/usr/src/supervisor/supervisor")
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
    def states(self) -> list[CoreState]:
        """Return a list of valid states when this evaluation can run."""
        return [CoreState.RUNNING]

    async def evaluate(self) -> None:
        """Run evaluation."""
        if not self.sys_security.content_trust:
            _LOGGER.warning("Disabled content-trust, skipping evaluation")
            return

        # Calculate sume of the sourcecode
        checksum = await self.sys_run_in_executor(
            calc_checksum_path_sourcecode, _SUPERVISOR_SOURCE
        )

        try:
            await self.sys_security.verify_own_content(checksum)
        except CodeNotaryUntrusted:
            return True
        except CodeNotaryError:
            pass

        return False
