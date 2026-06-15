"""Helper to fix missing image for app."""

import logging

from ...coresys import CoreSys
from ...exceptions import (
    DockerBuildError,
    DockerNoSpaceOnDevice,
    DockerRegistryAuthError,
    DockerRegistryRateLimitExceeded,
    ResolutionFixupError,
)
from ..const import ContextType, IssueType, SuggestionType
from ..data import Suggestion
from .base import FixupBase

_LOGGER: logging.Logger = logging.getLogger(__name__)
MAX_AUTO_ATTEMPTS = 5


def setup(coresys: CoreSys) -> FixupBase:
    """Check setup function."""
    return FixupAppExecuteRepair(coresys)


class FixupAppExecuteRepair(FixupBase):
    """Storage class for fixup."""

    def __init__(self, coresys: CoreSys) -> None:
        """Initialize the app execute repair fixup class."""
        super().__init__(coresys)
        self.attempts = 0

    async def process_fixup(self, suggestion: Suggestion) -> None:
        """Pull the apps image."""
        if not suggestion.reference:
            return

        app = self.sys_apps.get_local_only(suggestion.reference)
        if not app:
            _LOGGER.info(
                "Cannot repair app %s as it is not installed, dismissing suggestion",
                suggestion.reference,
            )
            return

        if await app.instance.exists():
            _LOGGER.info(
                "App %s does not need repair, dismissing suggestion",
                suggestion.reference,
            )
            return

        if app.is_detached and app.need_build:
            # No store source to rebuild from; the repair cannot succeed. The
            # detached-app check surfaces a remove suggestion instead.
            _LOGGER.warning(
                "Cannot repair app %s as it is detached from its store and "
                "needs a local build, dismissing suggestion",
                suggestion.reference,
            )
            return

        _LOGGER.info("Installing image for app %s", suggestion.reference)
        self.attempts += 1
        try:
            await app.instance.install(app.version)
        except (
            DockerBuildError,
            DockerNoSpaceOnDevice,
            DockerRegistryAuthError,
            DockerRegistryRateLimitExceeded,
        ) as err:
            # These failures won't be resolved by an immediate retry (broken
            # Dockerfile or unavailable base/builder image; disk full; bad
            # credentials; registry rate limit). Surface as a fixup error so
            # FixupBase swallows it without a Sentry event. The repair stays
            # available for manual retry once the underlying cause is fixed.
            _LOGGER.warning("Cannot repair app %s: %s", suggestion.reference, err)
            raise ResolutionFixupError from err

    @property
    def suggestion(self) -> SuggestionType:
        """Return a SuggestionType enum."""
        return SuggestionType.EXECUTE_REPAIR

    @property
    def context(self) -> ContextType:
        """Return a ContextType enum."""
        return ContextType.ADDON

    @property
    def issues(self) -> list[IssueType]:
        """Return a IssueType enum list."""
        return [IssueType.MISSING_IMAGE]

    @property
    def auto(self) -> bool:
        """Return if a fixup can be apply as auto fix."""
        return self.attempts < MAX_AUTO_ATTEMPTS
