"""Evaluation class for docker version."""
from typing import List

from ...const import CoreState
from ..const import UnsupportedReason
from .base import EvaluateBase


class EvaluateDockerVersion(EvaluateBase):
    """Evaluate Docker version."""

    @property
    def reason(self) -> UnsupportedReason:
        """Return a UnsupportedReason enum."""
        return UnsupportedReason.DOCKER_VERSION

    @property
    def on_failure(self) -> str:
        """Return a string that is printed when self.evaluate is False."""
        return f"Docker version '{self.sys_docker.info.version}' is not supported by the Supervisor!"

    @property
    def states(self) -> List[CoreState]:
        """Return a list of valid states when this evaluation can run."""
        return [CoreState.INITIALIZE]

    async def evaluate(self):
        """Run evaluation."""
        return not self.sys_docker.info.supported_version
