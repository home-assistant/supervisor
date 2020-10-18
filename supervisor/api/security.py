"""Handle security part of this API."""
import logging
import re

from aiohttp.web import Request, RequestHandler, Response, middleware
from aiohttp.web_exceptions import HTTPForbidden, HTTPUnauthorized

from ..const import (
    REQUEST_FROM,
    ROLE_ADMIN,
    ROLE_BACKUP,
    ROLE_DEFAULT,
    ROLE_HOMEASSISTANT,
    ROLE_MANAGER,
    CoreState,
)
from ..coresys import CoreSys, CoreSysAttributes
from .utils import api_return_error, excract_supervisor_token

_LOGGER: logging.Logger = logging.getLogger(__name__)

# fmt: off

# Block Anytime
BLACKLIST = re.compile(
    r"^(?:"
    r"|/homeassistant/api/hassio/.*"
    r"|/core/api/hassio/.*"
    r")$"
)

# Free to call or have own security concepts
NO_SECURITY_CHECK = re.compile(
    r"^(?:"
    r"|/homeassistant/api/.*"
    r"|/homeassistant/websocket"
    r"|/core/api/.*"
    r"|/core/websocket"
    r"|/supervisor/ping"
    r")$"
)

# Observer allow API calls
OBSERVER_CHECK = re.compile(
    r"^(?:"
    r"|/[^/]+/info"
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
        r"|/core/.+"
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
        r"|/addons(?:/[^/]+/(?!security).+|/reload)?"
        r"|/audio/.+"
        r"|/cli/.+"
        r"|/core/.+"
        r"|/dns/.+"
        r"|/docker/.+"
        r"|/hardware/.+"
        r"|/hassos/.+"
        r"|/homeassistant/.+"
        r"|/host/.+"
        r"|/multicast/.+"
        r"|/network/.+"
        r"|/observer/.+"
        r"|/os/.+"
        r"|/resolution/.+"
        r"|/snapshots.*"
        r"|/supervisor/.+"
        r")$"
    ),
    ROLE_ADMIN: re.compile(
        r".*"
    ),
}

# fmt: on


class SecurityMiddleware(CoreSysAttributes):
    """Security middleware functions."""

    def __init__(self, coresys: CoreSys):
        """Initialize security middleware."""
        self.coresys: CoreSys = coresys

    @middleware
    async def system_validation(
        self, request: Request, handler: RequestHandler
    ) -> Response:
        """Check if core is ready to response."""
        if self.sys_core.state not in (
            CoreState.STARTUP,
            CoreState.RUNNING,
            CoreState.FREEZE,
        ):
            return api_return_error(
                message=f"System is not ready with state: {self.sys_core.state.value}"
            )

        return await handler(request)

    @middleware
    async def token_validation(
        self, request: Request, handler: RequestHandler
    ) -> Response:
        """Check security access of this layer."""
        request_from = None
        supervisor_token = excract_supervisor_token(request)

        # Blacklist
        if BLACKLIST.match(request.path):
            _LOGGER.error("%s is blacklisted!", request.path)
            raise HTTPForbidden()

        # Ignore security check
        if NO_SECURITY_CHECK.match(request.path):
            _LOGGER.debug("Passthrough %s", request.path)
            return await handler(request)

        # Not token
        if not supervisor_token:
            _LOGGER.warning("No API token provided for %s", request.path)
            raise HTTPUnauthorized()

        # Home-Assistant
        if supervisor_token == self.sys_homeassistant.supervisor_token:
            _LOGGER.debug("%s access from Home Assistant", request.path)
            request_from = self.sys_homeassistant

        # Host
        if supervisor_token == self.sys_plugins.cli.supervisor_token:
            _LOGGER.debug("%s access from Host", request.path)
            request_from = self.sys_host

        # Observer
        if supervisor_token == self.sys_plugins.observer.supervisor_token:
            if not OBSERVER_CHECK.match(request.url):
                _LOGGER.warning("%s invalid Observer access", request.path)
                raise HTTPForbidden()
            _LOGGER.debug("%s access from Observer", request.path)
            request_from = self.sys_plugins.observer

        # Add-on
        addon = None
        if supervisor_token and not request_from:
            addon = self.sys_addons.from_token(supervisor_token)

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
