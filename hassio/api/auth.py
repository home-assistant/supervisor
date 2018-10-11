"""Init file for Hass.io auth/SSO RESTful API."""
import logging
import json

from aiohttp import BasicAuth
from aiohttp.hdrs import CONTENT_TYPE, AUTHORIZATION

from .utils import api_process
from ..const import REQUEST_FROM, CONTENT_TYPE_JSON, CONTENT_TYPE_URL
from ..coresys import CoreSysAttributes
from ..exceptions import APIError, APIForbidden

_LOGGER = logging.getLogger(__name__)


class APIAuth(CoreSysAttributes):
    """Handle RESTful API for auth functions."""

    def _process_basic_auth(self, request, addon):
        """Process login request with basic auth.
        
        Return a coroutine.
        """
        auth = BasicAuth.decode(request.headers[AUTHORIZATION])
        return self.sys_auth.check_login(addon, auth.login, auth.password)

    def _process_dict_auth(self, request, addon, data):
        """Process login with dict data.
        
        Return a coroutine.
        """
        username = data.get('username') or data.get('user')
        password = data.get('password')

        return self.sys_auth.check_login(addon, username, password)

    @api_process
    async def auth(self, request):
        """Process login request."""
        addon = request[REQUEST_FROM]

        if not addon.with_login_backend:
            raise APIForbidden("Can't use Home Assistant auth!")

        # BasicAuth
        if AUTHORIZATION in request.headers:
            return await _process_basic_auth(self, request, addon)

        # Json
        if request.headers[CONTENT_TYPE] == CONTENT_TYPE_JSON:
            data = await request.json()
            return await _process_dict_auth(self, request, addon, data)
 
        # URL encoded
        if request.headers[CONTENT_TYPE] == CONTENT_TYPE_URL:
            data = await request.post()
            return await _process_dict_auth(self, request, addon, data)

        raise APIError("Auth method not detected!")
