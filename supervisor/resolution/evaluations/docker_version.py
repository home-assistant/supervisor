"""Evaluation class for docker version."""

from awesomeversion import AwesomeVersion, AwesomeVersionCompareException

from ...const import CoreState
from ...coresys import CoreSys
from ..const import UnsupportedReason
from .base import EvaluateBase


def setup(coresys: CoreSys) -> EvaluateBase:
    """Initialize evaluation-setup function."""
    return EvaluateDockerVersion(coresys)


class EvaluateDockerVersion(EvaluateBase):
    """Evaluate Docker version."""

    def __init__(self, coresys):
        """Initialize check with known bad versions of docker."""
        super().__init__(coresys)
        self.min_supported_version = AwesomeVersion("20.10.1")
        self.broken_versions = {
            AwesomeVersion(
                "25.0.0"
            ): "network IP range evaluation is overly strict and does not allow supervisor/observer/etc to bind intended IPs;\n See: https://github.com/moby/moby/issues/47120.\nDowngrade to 24 or upgrade to 25.0.1+ if released"
        }
        self.specific_reason = "it seems to be missing or malformed?"

    @property
    def reason(self) -> UnsupportedReason:
        """Return a UnsupportedReason enum."""
        return UnsupportedReason.DOCKER_VERSION

    @property
    def on_failure(self) -> str:
        """Return a string that is printed when self.evaluate is True."""
        return f"Docker version '{self.sys_docker.info.version}' is not supported by the Supervisor!: {self.specific_reason}"

    @property
    def states(self) -> list[CoreState]:
        """Return a list of valid states when this evaluation can run."""
        return [CoreState.INITIALIZE]

    async def evaluate(self):
        """Run evaluation."""
        try:
            if self.sys_docker.info.version < self.min_supported_version:
                self.specific_reason = "It is much too old. Please upgrade."
                return True

            for bad_version, why_bad in self.broken_versions.items():
                if self.sys_docker.info.version == bad_version:
                    self.specific_reason = why_bad
                    return True
        except AwesomeVersionCompareException:
            return True

        return False
