"""Evaluation class for OS version."""

from awesomeversion import AwesomeVersion, AwesomeVersionException

from ...const import CoreState
from ...coresys import CoreSys
from ..const import UnsupportedReason
from .base import EvaluateBase


def setup(coresys: CoreSys) -> EvaluateBase:
    """Initialize evaluation-setup function."""
    return EvaluateOSVersion(coresys)


class EvaluateOSVersion(EvaluateBase):
    """Evaluate the OS version."""

    @property
    def reason(self) -> UnsupportedReason:
        """Return a UnsupportedReason enum."""
        return UnsupportedReason.OS_VERSION

    @property
    def on_failure(self) -> str:
        """Return a string that is printed when self.evaluate is True."""
        return f"OS version '{self.sys_os.version}' is more than 4 versions behind the latest '{self.sys_os.latest_version}'!"

    @property
    def states(self) -> list[CoreState]:
        """Return a list of valid states when this evaluation can run."""
        # Technically there's no reason to run this after STARTUP as update requires
        # a reboot. But if network is down we won't have latest version info then.
        return [CoreState.RUNNING, CoreState.STARTUP]

    async def evaluate(self) -> bool:
        """Run evaluation."""
        if (
            not self.sys_os.available
            or not (current := self.sys_os.version)
            or not (latest := self.sys_os.latest_version)
            or not latest.major
        ):
            return False

        # If current is more than 4 major versions behind latest, mark as unsupported
        last_supported_version = AwesomeVersion(f"{int(latest.major) - 4}.0")
        try:
            return current < last_supported_version
        except AwesomeVersionException:
            return True
