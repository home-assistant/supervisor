"""Init file for Hass.io secrets RESTful API."""
import asyncio
from typing import Awaitable, Dict

from aiohttp import web

from .utils import api_process
from ..const import ATTR_NAME, ATTR_VALUE
from ..coresys import CoreSysAttributes

SECRET = "secret"


class APISecrets(CoreSysAttributes):
    """Handle RESTful API for secrets functions."""

    @api_process
    async def secret(self, request: web.Request) -> Dict[str, str]:
        """Return secret data."""
        name = request.match_info.get(SECRET)
        return {ATTR_NAME: name, ATTR_VALUE: self.sys_secrets.get(name)}

    @api_process
    def reload(self, request: web.Request) -> Awaitable[None]:
        """Reload secret data."""
        return asyncio.shield(self.sys_secrets.reload())
