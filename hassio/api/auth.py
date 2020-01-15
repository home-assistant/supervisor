"""Init file for Hass.io auth/SSO RESTful API."""
import asyncio
import logging
from typing import Dict

from aiohttp import BasicAuth
from aiohttp.web_exceptions import HTTPUnauthorized
from aiohttp.hdrs import CONTENT_TYPE, AUTHORIZATION, WWW_AUTHENTICATE
import voluptuous as vol

from .utils import api_process, api_validate
from ..const import (
    REQUEST_FROM,
    CONTENT_TYPE_JSON,
    CONTENT_TYPE_URL,
    ATTR_PASSWORD,
    ATTR_USERNAME,
)
from ..coresys import CoreSysAttributes
from ..exceptions import APIForbidden

_LOGGER: logging.Logger = logging.getLogger(__name__)

SCHEMA_PASSWORD_RESET = vol.Schema(
    {
        vol.Required(ATTR_USERNAME): vol.Coerce(str),
        vol.Required(ATTR_PASSWORD): vol.Coerce(str),
    }
)


class APIAuth(CoreSysAttributes):
    """Handle RESTful API for auth functions."""

    def _process_basic(self, request, addon):
        """Process login request with basic auth.

        Return a coroutine.
        """
        auth = BasicAuth.decode(request.headers[AUTHORIZATION])
        return self.sys_auth.check_login(addon, auth.login, auth.password)

    def _process_dict(self, request, addon, data):
        """Process login with dict data.

        Return a coroutine.
        """
        username = data.get("username") or data.get("user")
        password = data.get("password")

        return self.sys_auth.check_login(addon, username, password)

    @api_process
    async def auth(self, request):
        """Process login request."""
        addon = request[REQUEST_FROM]

        if not addon.access_auth_api:
            raise APIForbidden("Can't use Home Assistant auth!")

        # BasicAuth
        if AUTHORIZATION in request.headers:
            return await self._process_basic(request, addon)

        # Json
        if request.headers.get(CONTENT_TYPE) == CONTENT_TYPE_JSON:
            data = await request.json()
            return await self._process_dict(request, addon, data)

        # URL encoded
        if request.headers.get(CONTENT_TYPE) == CONTENT_TYPE_URL:
            data = await request.post()
            return await self._process_dict(request, addon, data)

        raise HTTPUnauthorized(
            headers={WWW_AUTHENTICATE: 'Basic realm="Hass.io Authentication"'}
        )

    @api_process
    async def reset(self, request):
        """Process reset password request."""
        body: Dict[str, str] = await api_validate(SCHEMA_PASSWORD_RESET, request)
        return asyncio.shield(self.sys_auth.change_password(body[ATTR_USERNAME], body[ATTR_PASSWORD]))