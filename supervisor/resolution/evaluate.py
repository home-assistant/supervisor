"""Helpers to evaluate the system."""
from importlib import import_module
import logging

from ..coresys import CoreSys, CoreSysAttributes
from ..exceptions import ResolutionNotFound
from .const import UnhealthyReason, UnsupportedReason
from .evaluations.base import EvaluateBase
from .validate import get_valid_modules

_LOGGER: logging.Logger = logging.getLogger(__name__)

UNHEALTHY = [
    UnsupportedReason.CONTAINER,
    UnsupportedReason.DOCKER_VERSION,
    UnsupportedReason.LXC,
    UnsupportedReason.PRIVILEGED,
]


class ResolutionEvaluation(CoreSysAttributes):
    """Evaluation class for resolution."""

    def __init__(self, coresys: CoreSys) -> None:
        """Initialize the evaluation class."""
        self.coresys = coresys
        self.cached_images: set[str] = set()
        self._evalutions: dict[str, EvaluateBase] = {}

        self._load()

    @property
    def all_evaluations(self) -> list[EvaluateBase]:
        """Return all list of all checks."""
        return list(self._evalutions.values())

    def _load(self):
        """Load all checks."""
        package = f"{__package__}.evaluations"
        for module in get_valid_modules("evaluations"):
            check_module = import_module(f"{package}.{module}")
            check = check_module.setup(self.coresys)
            self._evalutions[check.slug] = check

    def get(self, slug: str) -> EvaluateBase:
        """Return check based on slug."""
        if slug in self._evalutions:
            return self._evalutions[slug]

        raise ResolutionNotFound(f"Check with slug {slug} not found!")

    async def evaluate_system(self) -> None:
        """Evaluate the system."""
        _LOGGER.info("Starting system evaluation with state %s", self.sys_core.state)

        for evaluation in self.all_evaluations:
            try:
                await evaluation()
            except Exception as err:  # pylint: disable=broad-except
                _LOGGER.warning(
                    "Error during processing %s: %s", evaluation.reason, err
                )
                self.sys_capture_exception(err)

        if any(reason in self.sys_resolution.unsupported for reason in UNHEALTHY):
            self.sys_resolution.unhealthy = UnhealthyReason.DOCKER

        _LOGGER.info("System evaluation complete")
