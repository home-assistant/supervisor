"""Handle REST API for resoulution."""
import asyncio
from typing import Any, Awaitable, Dict

from aiohttp import web
import attr

from ..const import (
    ATTR_CHECKS,
    ATTR_ENABLED,
    ATTR_ISSUES,
    ATTR_NAME,
    ATTR_SUGGESTIONS,
    ATTR_UNHEALTHY,
    ATTR_UNSUPPORTED,
    REQUEST_FROM,
)
from ..coresys import CoreSysAttributes
from ..exceptions import APIError, ResolutionError, ResolutionNotFound
from .utils import api_process


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
                {ATTR_ENABLED: check.enabled, ATTR_NAME: check.name}
                for check in self.sys_resolution.check.all_checks
                if check.can_disable
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
    async def enable_check(self, request: web.Request) -> None:
        """Enable check."""
        if request[REQUEST_FROM] != self.sys_homeassistant:
            raise APIError(
                "Access to this endpoint is only allowed from Home Assistant"
            )

        try:
            self.sys_resolution.check.enable(request.match_info.get("check"))
        except ResolutionError as err:
            raise APIError(err) from err

    @api_process
    async def disable_check(self, request: web.Request) -> None:
        """Disable check."""
        if request[REQUEST_FROM] != self.sys_homeassistant:
            raise APIError(
                "Access to this endpoint is only allowed from Home Assistant"
            )

        try:
            self.sys_resolution.check.disable(request.match_info.get("check"))
        except ResolutionError as err:
            raise APIError(err) from err
