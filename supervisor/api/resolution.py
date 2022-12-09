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
from ..exceptions import APIError, ResolutionNotFound
from ..resolution.data import Suggestion
from .utils import api_process, api_validate

SCHEMA_CHECK_OPTIONS = vol.Schema({vol.Optional(ATTR_ENABLED): bool})


class APIResoulution(CoreSysAttributes):
    """Handle REST API for resoulution."""

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
        try:
            suggestion = self.sys_resolution.get_suggestion(
                request.match_info.get("suggestion")
            )
            await self.sys_resolution.apply_suggestion(suggestion)
        except ResolutionNotFound:
            raise APIError("The supplied UUID is not a valid suggestion") from None

    @api_process
    async def dismiss_suggestion(self, request: web.Request) -> None:
        """Dismiss suggestion."""
        try:
            suggestion = self.sys_resolution.get_suggestion(
                request.match_info.get("suggestion")
            )
            self.sys_resolution.dismiss_suggestion(suggestion)
        except ResolutionNotFound:
            raise APIError("The supplied UUID is not a valid suggestion") from None

    @api_process
    async def suggestions_for_issue(self, request: web.Request) -> dict[str, Any]:
        """Return suggestions that fix an issue."""
        try:
            issue = self.sys_resolution.get_issue(request.match_info.get("issue"))
            return {
                ATTR_SUGGESTIONS: [
                    self._generate_suggestion_information(suggestion)
                    for suggestion in self.sys_resolution.suggestions_for_issue(issue)
                ]
            }
        except ResolutionNotFound:
            raise APIError("The supplied UUID is not a valid issue") from None

    @api_process
    async def dismiss_issue(self, request: web.Request) -> None:
        """Dismiss issue."""
        try:
            issue = self.sys_resolution.get_issue(request.match_info.get("issue"))
            self.sys_resolution.dismiss_issue(issue)
        except ResolutionNotFound:
            raise APIError("The supplied UUID is not a valid issue") from None

    @api_process
    def healthcheck(self, request: web.Request) -> Awaitable[None]:
        """Run backend healthcheck."""
        return asyncio.shield(self.sys_resolution.healthcheck())

    @api_process
    async def options_check(self, request: web.Request) -> None:
        """Set options for check."""
        body = await api_validate(SCHEMA_CHECK_OPTIONS, request)

        try:
            check = self.sys_resolution.check.get(request.match_info.get("check"))
        except ResolutionNotFound:
            raise APIError("The supplied check slug is not available") from None

        # Apply options
        if ATTR_ENABLED in body:
            check.enabled = body[ATTR_ENABLED]

        self.sys_resolution.save_data()

    @api_process
    async def run_check(self, request: web.Request) -> None:
        """Execute a backend check."""
        try:
            check = self.sys_resolution.check.get(request.match_info.get("check"))
        except ResolutionNotFound:
            raise APIError("The supplied check slug is not available") from None

        await check()
