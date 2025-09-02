"""Evaluation class for Core version."""

from datetime import datetime, timedelta

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
        if not (current := self.sys_homeassistant.version) or not (
            latest := self.sys_homeassistant.latest_version
        ):
            return False

        # Skip evaluation for landingpage version
        if current == LANDINGPAGE:
            return False

        try:
            # Calculate if the current version was released more than 2 years ago
            # Home Assistant releases happen monthly, so approximately 24 versions per 2 years
            # However, we'll be more precise and check based on actual version numbers
            # Home Assistant follows a versioning scheme like 2024.1, 2024.2, etc.

            # Extract year from current version
            current_year = int(str(current).split(".")[0])

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

        except (AwesomeVersionException, ValueError, IndexError):
            # If we can't parse the version format, fall back to conservative approach
            # Consider unsupported if current is significantly behind latest
            try:
                # If latest version is from current year and current is from 2+ years ago
                latest_year = int(str(latest).split(".")[0])
                current_year = int(str(current).split(".")[0])
                return (latest_year - current_year) >= 2
            except (ValueError, IndexError):
                return False
