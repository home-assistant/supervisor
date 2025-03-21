"""Evaluation class for Content Trust."""

import errno
import logging
from pathlib import Path

from ...const import CoreState
from ...coresys import CoreSys
from ...exceptions import CodeNotaryError, CodeNotaryUntrusted
from ...utils.codenotary import calc_checksum_path_sourcecode
from ..const import ContextType, IssueType, UnhealthyReason, UnsupportedReason
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
        """Return a string that is printed when self.evaluate is True."""
        return "System detect unauthorized source code modifications."

    @property
    def states(self) -> list[CoreState]:
        """Return a list of valid states when this evaluation can run."""
        return [CoreState.RUNNING]

    async def evaluate(self) -> bool:
        """Run evaluation."""
        if not self.sys_security.content_trust:
            _LOGGER.warning("Disabled content-trust, skipping evaluation")
            return False

        # Calculate sume of the sourcecode
        try:
            checksum = await self.sys_run_in_executor(
                calc_checksum_path_sourcecode, _SUPERVISOR_SOURCE
            )
        except OSError as err:
            if err.errno == errno.EBADMSG:
                self.sys_resolution.add_unhealthy_reason(
                    UnhealthyReason.OSERROR_BAD_MESSAGE
                )

            self.sys_resolution.create_issue(
                IssueType.CORRUPT_FILESYSTEM, ContextType.SYSTEM
            )
            _LOGGER.error("Can't calculate checksum of source code: %s", err)
            return False

        # Validate checksum
        try:
            await self.sys_security.verify_own_content(checksum)
        except CodeNotaryUntrusted:
            return True
        except CodeNotaryError:
            pass

        return False
