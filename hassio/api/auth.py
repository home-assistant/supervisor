"""Init file for Hass.io auth/SSO RESTful API."""
import logging

from .utils import api_process
from ..const import REQUEST_FROM
from ..coresys import CoreSysAttributes
from ..exceptions import APIError, APIForbidden

_LOGGER = logging.getLogger(__name__)


class APIAuth(CoreSysAttributes):
    """Handle RESTful API for auth functions."""

    async def _process_basic_auth(self, request):
        """Process login request with basic auth."""

    async def _process_json_auth(self, request):
        """Process login with json reuqest."""

    async def _process_post_auth(self, request):
        """Process login with post variable reuqest."""

    @api_process
    async def auth(self, request):
        """Process login request."""
        addon = request[REQUEST_FROM]

        if not addon.with_login_backend:
            raise APIForbidden("Can't use Home Assistant auth!")

        if Authorization
