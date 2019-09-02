"""Handle security part of this API."""
import logging
import re

from aiohttp.web import middleware
from aiohttp.web_exceptions import HTTPUnauthorized, HTTPForbidden

from ..const import (
    HEADER_TOKEN,
    REQUEST_FROM,
    ROLE_ADMIN,
    ROLE_DEFAULT,
    ROLE_HOMEASSISTANT,
    ROLE_MANAGER,
    ROLE_BACKUP,
)
from ..coresys import CoreSysAttributes

_LOGGER: logging.Logger = logging.getLogger(__name__)

# fmt: off

# Block Anytime
BLACKLIST = re.compile(
    r"^(?:"
    r"|/homeassistant/api/hassio/.*"
    r")$"
)

# Free to call or have own security concepts
NO_SECURITY_CHECK = re.compile(
    r"^(?:"
    r"|/homeassistant/api/.*"
    r"|/homeassistant/websocket"
    r"|/supervisor/ping"
    r")$"
)

# Can called by every add-on
ADDONS_API_BYPASS = re.compile(
    r"^(?:"
    r"|/addons/self/(?!security|update)[^/]+"
    r"|/info"
    r"|/hardware/trigger"
    r"|/services.*"
    r"|/discovery.*"
    r"|/auth"
    r")$"
)

# Policy role add-on API access
ADDONS_ROLE_ACCESS = {
    ROLE_DEFAULT: re.compile(
        r"^(?:"
        r"|/[^/]+/info"
        r"|/addons"
        r")$"
    ),
    ROLE_HOMEASSISTANT: re.compile(
        r"^(?:"
        r"|/homeassistant/.+"
        r")$"
    ),
    ROLE_BACKUP: re.compile(
        r"^(?:"
        r"|/snapshots.*"
        r")$"
    ),
    ROLE_MANAGER: re.compile(
        r"^(?:"
        r"|/dns/.*"
        r"|/homeassistant/.+"
        r"|/host/.+"
        r"|/hardware/.+"
        r"|/hassos/.+"
        r"|/supervisor/.+"
        r"|/addons(?:/[^/]+/(?!security).+|/reload)?"
        r"|/snapshots.*"
        r")$"
    ),
    ROLE_ADMIN: re.compile(
        r".*"
    ),
}

# fmt: off


class SecurityMiddleware(CoreSysAttributes):
    """Security middleware functions."""

    def __init__(self, coresys):
        """Initialize security middleware."""
        self.coresys = coresys

    @middleware
    async def token_validation(self, request, handler):
        """Check security access of this layer."""
        request_from = None
        hassio_token = request.headers.get(HEADER_TOKEN)

        # Blacklist
        if BLACKLIST.match(request.path):
            _LOGGER.warning("%s is blacklisted!", request.path)
            raise HTTPForbidden()

        # Ignore security check
        if NO_SECURITY_CHECK.match(request.path):
            _LOGGER.debug("Passthrough %s", request.path)
            return await handler(request)

        # Not token
        if not hassio_token:
            _LOGGER.warning("No API token provided for %s", request.path)
            raise HTTPUnauthorized()

        # Home-Assistant
        if hassio_token == self.sys_homeassistant.hassio_token:
            _LOGGER.debug("%s access from Home Assistant", request.path)
            request_from = self.sys_homeassistant

        # Host
        if hassio_token == self.sys_machine_id:
            _LOGGER.debug("%s access from Host", request.path)
            request_from = self.sys_host

        # Add-on
        addon = None
        if hassio_token and not request_from:
            addon = self.sys_addons.from_token(hassio_token)

        # Check Add-on API access
        if addon and ADDONS_API_BYPASS.match(request.path):
            _LOGGER.debug("Passthrough %s from %s", request.path, addon.slug)
            request_from = addon
        elif addon and addon.access_hassio_api:
            # Check Role
            if ADDONS_ROLE_ACCESS[addon.hassio_role].match(request.path):
                _LOGGER.info("%s access from %s", request.path, addon.slug)
                request_from = addon
            else:
                _LOGGER.warning("%s no role for %s", request.path, addon.slug)

        if request_from:
            request[REQUEST_FROM] = request_from
            return await handler(request)

        _LOGGER.error("Invalid token for access %s", request.path)
        raise HTTPForbidden()
