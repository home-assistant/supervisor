"""Handle REST API for resoulution."""
from typing import Any, Dict

from aiohttp import web
import attr

from ..const import ATTR_ISSUES, ATTR_SUGGESTIONS, ATTR_UNHEALTHY, ATTR_UNSUPPORTED
from ..coresys import CoreSysAttributes
from ..exceptions import APIError, ResolutionNotFound
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
