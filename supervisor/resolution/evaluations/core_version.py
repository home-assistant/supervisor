"""Evaluation class for Core version."""

from datetime import datetime, timedelta
import logging

from awesomeversion import (
    AwesomeVersion,
    AwesomeVersionException,
    AwesomeVersionStrategy,
)

from ...const import CoreState
from ...coresys import CoreSys
from ...homeassistant.const import LANDINGPAGE
from ..const import UnsupportedReason
from .base import EvaluateBase

_LOGGER: logging.Logger = logging.getLogger(__name__)


def setup(coresys: CoreSys) -> EvaluateBase:
    """Initialize evaluation-setup function."""
    return EvaluateCoreVersion(coresys)


class EvaluateCoreVersion(EvaluateBase):
    """Evaluate the Home Assistant Core version."""

    @property
    def reason(self) -> UnsupportedReason:
        """Return a UnsupportedReason enum."""
        return UnsupportedReason.CORE_VERSION

    @property
    def on_failure(self) -> str:
        """Return a string that is printed when self.evaluate is True."""
        return f"Home Assistant Core version '{self.sys_homeassistant.version}' is more than 2 years old!"

    @property
    def states(self) -> list[CoreState]:
        """Return a list of valid states when this evaluation can run."""
        return [CoreState.RUNNING, CoreState.SETUP]

    async def evaluate(self) -> bool:
        """Run evaluation."""
        if not (current := self.sys_homeassistant.version):
            return False

        # Skip evaluation for landingpage version
        if current == LANDINGPAGE:
            return False

        try:
            # Calculate if the current version was released more than 2 years ago
            # Home Assistant releases happen monthly, so approximately 24 versions per 2 years
            # However, we'll be more precise and check based on actual version numbers
            # Home Assistant uses CalVer versioning scheme like 2024.1, 2024.2, etc.

            # Calculate 2 years ago from now
            two_years_ago = datetime.now() - timedelta(days=730)  # 2 years = 730 days
            cutoff_year = two_years_ago.year
            cutoff_month = two_years_ago.month

            # Create a cutoff version based on the date 2 years ago
            cutoff_version = AwesomeVersion(
                f"{cutoff_year}.{cutoff_month}",
                ensure_strategy=AwesomeVersionStrategy.CALVER,
            )

            # Compare current version with the cutoff
            return current < cutoff_version

        except AwesomeVersionException as err:
            # This is run regularly, avoid log spam by logging at debug level
            _LOGGER.debug(
                "Failed to parse Home Assistant version '%s' or cutoff version '%s': %s",
                current,
                cutoff_version,
                err,
            )
            # Consider non-parseable versions as unsupported
            return True
