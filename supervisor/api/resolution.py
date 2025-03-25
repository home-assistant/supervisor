"""Handle REST API for resoulution."""

import asyncio
from collections.abc import Awaitable
from typing import Any

from aiohttp import web
import attr
import voluptuous as vol

from ..const import (
    ATTR_AUTO,
    ATTR_CHECKS,
    ATTR_ENABLED,
    ATTR_ISSUES,
    ATTR_SLUG,
    ATTR_SUGGESTIONS,
    ATTR_UNHEALTHY,
    ATTR_UNSUPPORTED,
)
from ..coresys import CoreSysAttributes
from ..exceptions import APINotFound, ResolutionNotFound
from ..resolution.checks.base import CheckBase
from ..resolution.data import Issue, Suggestion
from .utils import api_process, api_validate

SCHEMA_CHECK_OPTIONS = vol.Schema({vol.Optional(ATTR_ENABLED): bool})


class APIResoulution(CoreSysAttributes):
    """Handle REST API for resoulution."""

    def _extract_issue(self, request: web.Request) -> Issue:
        """Extract issue from request or raise."""
        try:
            return self.sys_resolution.get_issue(request.match_info["issue"])
        except ResolutionNotFound:
            raise APINotFound("The supplied UUID is not a valid issue") from None

    def _extract_suggestion(self, request: web.Request) -> Suggestion:
        """Extract suggestion from request or raise."""
        try:
            return self.sys_resolution.get_suggestion(request.match_info["suggestion"])
        except ResolutionNotFound:
            raise APINotFound("The supplied UUID is not a valid suggestion") from None

    def _extract_check(self, request: web.Request) -> CheckBase:
        """Extract check from request or raise."""
        try:
            return self.sys_resolution.check.get(request.match_info["check"])
        except ResolutionNotFound:
            raise APINotFound("The supplied check slug is not available") from None

    def _generate_suggestion_information(self, suggestion: Suggestion):
        """Generate suggestion information for response."""
        resp = attr.asdict(suggestion)
        resp[ATTR_AUTO] = bool(
            [
                fix
                for fix in self.sys_resolution.fixup.fixes_for_suggestion(suggestion)
                if fix.auto
            ]
        )
        return resp

    @api_process
    async def info(self, request: web.Request) -> dict[str, Any]:
        """Return resolution information."""
        return {
            ATTR_UNSUPPORTED: self.sys_resolution.unsupported,
            ATTR_UNHEALTHY: self.sys_resolution.unhealthy,
            ATTR_SUGGESTIONS: [
                self._generate_suggestion_information(suggestion)
                for suggestion in self.sys_resolution.suggestions
            ],
            ATTR_ISSUES: [attr.asdict(issue) for issue in self.sys_resolution.issues],
            ATTR_CHECKS: [
                {ATTR_ENABLED: check.enabled, ATTR_SLUG: check.slug}
                for check in self.sys_resolution.check.all_checks
            ],
        }

    @api_process
    async def apply_suggestion(self, request: web.Request) -> None:
        """Apply suggestion."""
        suggestion = self._extract_suggestion(request)
        await self.sys_resolution.apply_suggestion(suggestion)

    @api_process
    async def dismiss_suggestion(self, request: web.Request) -> None:
        """Dismiss suggestion."""
        suggestion = self._extract_suggestion(request)
        self.sys_resolution.dismiss_suggestion(suggestion)

    @api_process
    async def suggestions_for_issue(self, request: web.Request) -> dict[str, Any]:
        """Return suggestions that fix an issue."""
        issue = self._extract_issue(request)
        return {
            ATTR_SUGGESTIONS: [
                self._generate_suggestion_information(suggestion)
                for suggestion in self.sys_resolution.suggestions_for_issue(issue)
            ]
        }

    @api_process
    async def dismiss_issue(self, request: web.Request) -> None:
        """Dismiss issue."""
        issue = self._extract_issue(request)
        self.sys_resolution.dismiss_issue(issue)

    @api_process
    def healthcheck(self, request: web.Request) -> Awaitable[None]:
        """Run backend healthcheck."""
        return asyncio.shield(self.sys_resolution.healthcheck())

    @api_process
    async def options_check(self, request: web.Request) -> None:
        """Set options for check."""
        body = await api_validate(SCHEMA_CHECK_OPTIONS, request)
        check = self._extract_check(request)

        # Apply options
        if ATTR_ENABLED in body:
            check.enabled = body[ATTR_ENABLED]

        await self.sys_resolution.save_data()

    @api_process
    async def run_check(self, request: web.Request) -> None:
        """Execute a backend check."""
        check = self._extract_check(request)
        await check()
