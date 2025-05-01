"""Handle security part of this API."""

from collections.abc import Callable
import logging
import re
from typing import Final
from urllib.parse import unquote

from aiohttp.web import Request, Response, middleware
from aiohttp.web_exceptions import HTTPBadRequest, HTTPForbidden, HTTPUnauthorized
from awesomeversion import AwesomeVersion

from supervisor.homeassistant.const import LANDINGPAGE

from ...addons.const import RE_SLUG
from ...const import (
    REQUEST_FROM,
    ROLE_ADMIN,
    ROLE_BACKUP,
    ROLE_DEFAULT,
    ROLE_HOMEASSISTANT,
    ROLE_MANAGER,
    VALID_API_STATES,
)
from ...coresys import CoreSys, CoreSysAttributes
from ...utils import version_is_new_enough
from ..utils import api_return_error, extract_supervisor_token

_LOGGER: logging.Logger = logging.getLogger(__name__)
_CORE_VERSION: Final = AwesomeVersion("2023.3.4")

# fmt: off

_CORE_FRONTEND_PATHS: Final = (
    r"|/app/.*\.(?:js|gz|json|map|woff2)"
    r"|/(store/)?addons/" + RE_SLUG + r"/(logo|icon)"
)

CORE_FRONTEND: Final = re.compile(
    r"^(?:" + _CORE_FRONTEND_PATHS + r")$"
)


# Block Anytime
BLACKLIST: Final = re.compile(
    r"^(?:"
    r"|/homeassistant/api/hassio/.*"
    r"|/core/api/hassio/.*"
    r")$"
)

# Free to call or have own security concepts
NO_SECURITY_CHECK: Final = re.compile(
    r"^(?:"
    r"|/homeassistant/api/.*"
    r"|/homeassistant/websocket"
    r"|/core/api/.*"
    r"|/core/websocket"
    r"|/supervisor/ping"
    r"|/ingress/[-_A-Za-z0-9]+/.*"
    + _CORE_FRONTEND_PATHS
    + r")$"
)

# Observer allow API calls
OBSERVER_CHECK: Final = re.compile(
    r"^(?:"
    r"|/.+/info"
    r")$"
)

# Can called by every add-on
ADDONS_API_BYPASS: Final = re.compile(
    r"^(?:"
    r"|/addons/self/(?!security|update)[^/]+"
    r"|/addons/self/options/config"
    r"|/info"
    r"|/services.*"
    r"|/discovery.*"
    r"|/auth"
    r")$"
)

# Home Assistant only
CORE_ONLY_PATHS: Final = re.compile(
    r"^(?:"
    r"/addons/" + RE_SLUG + "/sys_options"
    r")$"
)

# Policy role add-on API access
ADDONS_ROLE_ACCESS: dict[str, re.Pattern] = {
    ROLE_DEFAULT: re.compile(
        r"^(?:"
        r"|/.+/info"
        r")$"
    ),
    ROLE_HOMEASSISTANT: re.compile(
        r"^(?:"
        r"|/.+/info"
        r"|/core/.+"
        r"|/homeassistant/.+"
        r")$"
    ),
    ROLE_BACKUP: re.compile(
        r"^(?:"
        r"|/.+/info"
        r"|/backups.*"
        r")$"
    ),
    ROLE_MANAGER: re.compile(
        r"^(?:"
        r"|/.+/info"
        r"|/addons(?:/" + RE_SLUG + r"/(?!security).+|/reload)?"
        r"|/audio/.+"
        r"|/auth/cache"
        r"|/available_updates"
        r"|/backups.*"
        r"|/cli/.+"
        r"|/core/.+"
        r"|/dns/.+"
        r"|/docker/.+"
        r"|/jobs/.+"
        r"|/hardware/.+"
        r"|/hassos/.+"
        r"|/homeassistant/.+"
        r"|/host/.+"
        r"|/mounts.*"
        r"|/multicast/.+"
        r"|/network/.+"
        r"|/observer/.+"
        r"|/os/(?!datadisk/wipe).+"
        r"|/refresh_updates"
        r"|/resolution/.+"
        r"|/security/.+"
        r"|/snapshots.*"
        r"|/store.*"
        r"|/supervisor/.+"
        r")$"
    ),
    ROLE_ADMIN: re.compile(
        r".*"
    ),
}

FILTERS: Final = re.compile(
    r"(?:"

    # Common exploits
    r"proc/self/environ"
    r"|(<|%3C).*script.*(>|%3E)"

    # File Injections
    r"|(\.\.//?)+"  # ../../anywhere
    r"|[a-zA-Z0-9_]=/([a-z0-9_.]//?)+"  # .html?v=/.//test

    # SQL Injections
    r"|union.*select.*\("
    r"|union.*all.*select.*"
    r"|concat.*\("

    r")",
    flags=re.IGNORECASE,
)

# fmt: on


class SecurityMiddleware(CoreSysAttributes):
    """Security middleware functions."""

    def __init__(self, coresys: CoreSys):
        """Initialize security middleware."""
        self.coresys: CoreSys = coresys

    def _recursive_unquote(self, value: str) -> str:
        """Handle values that are encoded multiple times."""
        if (unquoted := unquote(value)) != value:
            unquoted = self._recursive_unquote(unquoted)
        return unquoted

    @middleware
    async def block_bad_requests(self, request: Request, handler: Callable) -> Response:
        """Process request and tblock commonly known exploit attempts."""
        if FILTERS.search(self._recursive_unquote(request.path)):
            _LOGGER.warning(
                "Filtered a potential harmful request to: %s", request.raw_path
            )
            raise HTTPBadRequest

        if FILTERS.search(self._recursive_unquote(request.query_string)):
            _LOGGER.warning(
                "Filtered a request with a potential harmful query string: %s",
                request.raw_path,
            )
            raise HTTPBadRequest

        return await handler(request)

    @middleware
    async def system_validation(self, request: Request, handler: Callable) -> Response:
        """Check if core is ready to response."""
        if self.sys_core.state not in VALID_API_STATES:
            return api_return_error(
                message=f"System is not ready with state: {self.sys_core.state}"
            )

        return await handler(request)

    @middleware
    async def token_validation(self, request: Request, handler: Callable) -> Response:
        """Check security access of this layer."""
        request_from: CoreSysAttributes | None = None
        supervisor_token = extract_supervisor_token(request)

        # Blacklist
        if BLACKLIST.match(request.path):
            _LOGGER.error("%s is blacklisted!", request.path)
            raise HTTPForbidden()

        # Ignore security check
        if NO_SECURITY_CHECK.match(request.path):
            _LOGGER.debug("Passthrough %s", request.path)
            request[REQUEST_FROM] = None
            return await handler(request)

        # Not token
        if not supervisor_token:
            _LOGGER.warning("No API token provided for %s", request.path)
            raise HTTPUnauthorized()

        # Home-Assistant
        if supervisor_token == self.sys_homeassistant.supervisor_token:
            _LOGGER.debug("%s access from Home Assistant", request.path)
            request_from = self.sys_homeassistant
        elif CORE_ONLY_PATHS.match(request.path):
            _LOGGER.warning("Attempted access to %s from client besides Home Assistant")
            raise HTTPForbidden()

        # Host
        if supervisor_token == self.sys_plugins.cli.supervisor_token:
            _LOGGER.debug("%s access from Host", request.path)
            request_from = self.sys_host

        # Observer
        if supervisor_token == self.sys_plugins.observer.supervisor_token:
            if not OBSERVER_CHECK.match(request.path):
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
        elif addon:
            _LOGGER.warning(
                "%s missing API permission for %s", addon.slug, request.path
            )

        if request_from:
            request[REQUEST_FROM] = request_from
            return await handler(request)

        _LOGGER.error("Invalid token for access %s", request.path)
        raise HTTPForbidden()

    @middleware
    async def core_proxy(self, request: Request, handler: Callable) -> Response:
        """Validate user from Core API proxy."""
        if (
            request[REQUEST_FROM] != self.sys_homeassistant
            or self.sys_homeassistant.version == LANDINGPAGE
            or version_is_new_enough(self.sys_homeassistant.version, _CORE_VERSION)
        ):
            return await handler(request)

        authorization_index: int | None = None
        content_type_index: int | None = None
        user_request: bool = False
        admin_request: bool = False
        ingress_request: bool = False

        for idx, (key, value) in enumerate(request.raw_headers):
            if key in (b"Authorization", b"X-Hassio-Key"):
                authorization_index = idx
            elif key == b"Content-Type":
                content_type_index = idx
            elif key == b"X-Hass-User-ID":
                user_request = True
            elif key == b"X-Hass-Is-Admin":
                admin_request = value == b"1"
            elif key == b"X-Ingress-Path":
                ingress_request = True

        if (user_request or admin_request) and not ingress_request:
            return await handler(request)

        is_proxy_request = (
            authorization_index is not None
            and content_type_index is not None
            and content_type_index - authorization_index == 1
        )

        if (
            not CORE_FRONTEND.match(request.path) and is_proxy_request
        ) or ingress_request:
            raise HTTPBadRequest()
        return await handler(request)
