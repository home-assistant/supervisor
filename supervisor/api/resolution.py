"""Handle REST API for resoulution."""
import asyncio
from typing import Any, Awaitable, Dict

from aiohttp import web
import attr
import voluptuous as vol

from ..const import (
    ATTR_CHECKS,
    ATTR_ENABLED,
    ATTR_ISSUES,
    ATTR_SLUG,
    ATTR_SUGGESTIONS,
    ATTR_UNHEALTHY,
    ATTR_UNSUPPORTED,
)
from ..coresys import CoreSysAttributes
from ..exceptions import APIError, ResolutionError, ResolutionNotFound
from .utils import api_process, api_validate, require_home_assistant

SCHEMA_CHECK_OPTIONS = vol.Schema({vol.Required(ATTR_ENABLED): bool})


class APIResoulution(CoreSysAttributes):
    """Handle REST API for resoulution."""

    @api_process
    async def info(self, request: web.Request) -> Dict[str, Any]:
        """Return network information."""
        return {
            ATTR_UNSUPPORTED: self.sys_resolution.unsupported,
            ATTR_UNHEALTHY: self.sys_resolution.unhealthy,
            ATTR_SUGGESTIONS: [
                attr.asdict(suggestion)
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
    @require_home_assistant
    async def check_options(self, request: web.Request) -> None:
        """Set check options."""
        body = await api_validate(SCHEMA_CHECK_OPTIONS, request)

        try:
            if body[ATTR_ENABLED]:
                self.sys_resolution.check.enable(request.match_info.get("check"))
            else:
                self.sys_resolution.check.disable(request.match_info.get("check"))
        except ResolutionError as err:
            raise APIError(err) from err
