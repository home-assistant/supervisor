"""Handle REST API for resoulution."""
from typing import Any, Dict

from aiohttp import web

from ..const import ATTR_ISSUES, ATTR_SUGGESTIONS, ATTR_UNSUPPORTED
from ..coresys import CoreSysAttributes
from ..exceptions import APIError
from ..resolution.const import Suggestion
from .utils import api_process


class APIResoulution(CoreSysAttributes):
    """Handle REST API for resoulution."""

    @api_process
    async def base(self, request: web.Request) -> Dict[str, Any]:
        """Return network information."""
        return {
            ATTR_UNSUPPORTED: self.sys_resolution.unsupported,
            ATTR_SUGGESTIONS: self.sys_resolution.suggestions,
            ATTR_ISSUES: self.sys_resolution.issues,
        }

    @api_process
    async def apply_suggestion(self, request: web.Request) -> None:
        """Apply suggestion."""
        try:
            suggestion = Suggestion(request.match_info.get("suggestion"))
            await self.sys_resolution.apply_suggestion(suggestion)
        except ValueError:
            raise APIError("Suggestion is not valid") from None

    @api_process
    async def dismiss_suggestion(self, request: web.Request) -> None:
        """Dismiss suggestion."""
        try:
            suggestion = Suggestion(request.match_info.get("suggestion"))
            await self.sys_resolution.dismiss_suggestion(suggestion)
        except ValueError:
            raise APIError("Suggestion is not valid") from None
