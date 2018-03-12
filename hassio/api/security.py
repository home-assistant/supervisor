"""Handle security part of this API."""
import logging
import re

from aiohttp.web import middleware
from aiohttp.web_exceptions import HTTPUnauthorized

from ..const import HEADER_TOKEN, REQUEST_FROM
from ..coresys import CoreSysAttributes

_LOGGER = logging.getLogger(__name__)

NO_SECURITY_CHECK = set((
    re.compile(r"^/homeassistant/api/.*$"),
    re.compile(r"^/homeassistant/websocket$"),
    re.compile(r"^/supervisor/ping$"),
))


class SecurityMiddleware(CoreSysAttributes):
    """Security middleware functions."""

    def __init__(self, coresys):
        """Initialize security middleware."""
        self.coresys = coresys

    @middleware
    async def token_validation(self, request, handler):
        """Check security access of this layer."""
        hassio_token = request.headers.get(HEADER_TOKEN)

        # Ignore security check
        for rule in NO_SECURITY_CHECK:
            if rule.match(request.path):
                _LOGGER.debug("Passthrough %s", request.path)
                return await handler(request)

        # Need to be removed later
        if not hassio_token:
            _LOGGER.warning("Invalid token for access %s", request.path)
            request[REQUEST_FROM] = 'UNKNOWN'
            return await handler(request)

        # Home-Assistant
        if hassio_token == self._homeassistant.uuid:
            _LOGGER.debug("%s access from Home-Assistant", request.path)
            request[REQUEST_FROM] = 'homeassistant'
            return await handler(request)

        # Add-on
        addon = self._addons.from_uuid(hassio_token)
        if addon:
            _LOGGER.info("%s access from %s", request.path, addon.slug)
            request[REQUEST_FROM] = addon.slug
            return await handler(request)

        raise HTTPUnauthorized()
