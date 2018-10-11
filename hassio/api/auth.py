"""Init file for Hass.io auth/SSO RESTful API."""
import logging
import json

from aiohttp import BasicAuth
from aiohttp.hdrs import CONTENT_TYPE, AUTHORIZATION

from .utils import api_process
from ..const import REQUEST_FROM, CONTENT_TYPE_JSON
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

    def async _process_json_auth(self, request, addon):
        """Process login with json reuqest."""
        data = await request.json()

        username = data.get('username') or data.get('user')
        password = data.get('password')

        return await self.sys_auth.check_login(addon, username, password)

    def _process_post_auth(self, request, addon):
        """Process login with post variable reuqest.
        
        Return a coroutine.
        """

    @api_process
    async def auth(self, request):
        """Process login request."""
        addon = request[REQUEST_FROM]

        if not addon.with_login_backend:
            raise APIForbidden("Can't use Home Assistant auth!")

        # BasicAuth
        if AUTHORIZATION in request.headers:
            return await _process_basic_auth(self, request)

        # Json
        if request.headers[CONTENT_TYPE] == CONTENT_TYPE_JSON:
            return await _process_json_auth(self, request)
 
