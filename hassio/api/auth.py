"""Init file for Hass.io auth/SSO RESTful API."""
import logging

from .utils import api_process
from ..const import REQUEST_FROM
from ..coresys import CoreSysAttributes
from ..exceptions import APIError, APIForbidden

_LOGGER = logging.getLogger(__name__)


class APIAuth(CoreSysAttributes):
    """Handle RESTful API for auth functions."""
    
    async _process_basic_auth(self):
        """Process login request w

    @api_process
    async def auth(self, request):
        """Process login request."""
        addon = request[REQUEST_FROM]

        if not addon.with_login_backend:
            raise APIForbidden("Can't use Home Assistant auth!")
