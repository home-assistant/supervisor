"""Evaluation class for restart policy."""

from supervisor.docker.const import RestartPolicy
from supervisor.docker.interface import DockerInterface

from ...const import CoreState
from ...coresys import CoreSys
from ..const import UnsupportedReason
from .base import EvaluateBase


def setup(coresys: CoreSys) -> EvaluateBase:
    """Initialize evaluation-setup function."""
    return EvaluateRestartPolicy(coresys)


class EvaluateRestartPolicy(EvaluateBase):
    """Evaluate restart policy of containers."""

    def __init__(self, coresys: CoreSys) -> None:
        """Initialize the evaluation class."""
        super().__init__(coresys)
        self.coresys = coresys
        self._containers: list[str] = []

    @property
    def reason(self) -> UnsupportedReason:
        """Return a UnsupportedReason enum."""
        return UnsupportedReason.RESTART_POLICY

    @property
    def on_failure(self) -> str:
        """Return a string that is printed when self.evaluate is True."""
        return f"Found containers with unsupported restart policy: {self._containers}"

    @property
    def states(self) -> list[CoreState]:
        """Return a list of valid states when this evaluation can run."""
        return [CoreState.RUNNING]

    @property
    def no_restart_expected(self) -> set[DockerInterface]:
        """Docker interfaces where no restart is expected policy."""
        return {
            self.sys_supervisor.instance,
            self.sys_homeassistant.core.instance,
            *{
                plug.instance
                for plug in self.sys_plugins.all_plugins
                if plug != self.sys_plugins.observer
            },
            *{addon.instance for addon in self.sys_addons.installed},
        }

    @property
    def always_restart_expected(self) -> set[DockerInterface]:
        """Docker interfaces where always restart is expected policy."""
        return {self.sys_plugins.observer.instance}

    async def evaluate(self) -> bool:
        """Run evaluation, return true if system fails."""
        self._containers = {
            instance.name
            for instance in self.no_restart_expected
            if instance.restart_policy and instance.restart_policy != RestartPolicy.NO
        } | {
            instance.name
            for instance in self.always_restart_expected
            if instance.restart_policy
            and instance.restart_policy != RestartPolicy.ALWAYS
        }

        return len(self._containers) > 0
