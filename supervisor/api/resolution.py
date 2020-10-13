"""Handle REST API for resoulution."""
from typing import Any, Dict

from aiohttp import web

from ..const import ATTR_UNSUPPORTED
from ..coresys import CoreSysAttributes
from .utils import api_process


class APIResoulution(CoreSysAttributes):
    """Handle REST API for resoulution."""

    @api_process
    async def base(self, request: web.Request) -> Dict[str, Any]:
        """Return network information."""
        return {ATTR_UNSUPPORTED: self.sys_resolution.unsupported}
