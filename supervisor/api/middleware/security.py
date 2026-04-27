"""Handle security part of this API."""

from collections.abc import Awaitable, Callable
from dataclasses import dataclass
import logging
import re
from typing import Final
from urllib.parse import unquote

from aiohttp.web import Request, StreamResponse, middleware
from aiohttp.web_exceptions import HTTPBadRequest, HTTPForbidden, HTTPUnauthorized

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
from ..utils import api_return_error, extract_supervisor_token

_LOGGER: logging.Logger = logging.getLogger(__name__)

# fmt: off

_V1_FRONTEND_PATHS: Final = (
    r"|/app/.*\.(?:js|gz|json|map|woff2)"
    r"|/(store/)?addons/" + RE_SLUG + r"/(logo|icon)"
)

_V2_FRONTEND_PATHS: Final = (
    r"|/store/apps/" + RE_SLUG + r"/(logo|icon)"
)


# Block Anytime
BLACKLIST: Final = re.compile(
    r"^(?:"
    r"|/homeassistant/api/hassio/.*"
    r"|/core/api/hassio/.*"
    r")$"
)

# Observer allow API calls
OBSERVER_CHECK: Final = re.compile(
    r"^(?:"
    r"|/.+/info"
    r")$"
)

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

@dataclass(slots=True, frozen=True)
class _AppSecurityPatterns:
    """All compiled regex patterns for app API access control, per API version."""

    # Paths where an installed app's token bypasses normal role checks
    api_bypass: re.Pattern[str]

    # Paths that only Home Assistant Core may call
    core_only: re.Pattern[str]

    # Per-role allowed path patterns for installed apps
    role_access: dict[str, re.Pattern[str]]

    # Paths that skip token validation entirely
    no_security_check: re.Pattern[str]


# fmt: off

_V1_PATTERNS: Final = _AppSecurityPatterns(
    api_bypass=re.compile(
        r"^(?:"
        r"|/addons/self/(?!security|update)[^/]+"
        r"|/addons/self/options/config"
        r"|/info"
        r"|/services.*"
        r"|/discovery.*"
        r"|/auth"
        r")$"
    ),
    core_only=re.compile(
        r"^(?:"
        r"/addons/" + RE_SLUG + r"/sys_options"
        r")$"
    ),
    role_access={
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
        ROLE_ADMIN: re.compile(r".*"),
    },
    no_security_check=re.compile(
        r"^(?:"
        r"|/homeassistant/api/.*"
        r"|/homeassistant/websocket"
        r"|/core/api/.*"
        r"|/core/websocket"
        r"|/supervisor/ping"
        r"|/ingress/[-_A-Za-z0-9]+/.*"
        + _V1_FRONTEND_PATHS
        + r")$"
    ),
)

_V2_PATTERNS: Final = _AppSecurityPatterns(
    # /v2 is factored out as a literal prefix — alternatives only list the
    # path suffix, making v1 ↔ v2 pattern diffs easy to read.
    api_bypass=re.compile(
        r"^/v2(?:"
        r"|/apps/self/(?!security|update)[^/]+"
        r"|/apps/self/options/config"
        r"|/info"
        r"|/services.*"
        r"|/discovery.*"
        r"|/auth"
        r")$"
    ),
    core_only=re.compile(
        r"^/v2(?:"
        r"/apps/" + RE_SLUG + r"/sys_options"
        r")$"
    ),
    role_access={
        ROLE_DEFAULT: re.compile(
            r"^/v2(?:"
            r"|/.+/info"
            r")$"
        ),
        ROLE_HOMEASSISTANT: re.compile(
            r"^/v2(?:"
            r"|/.+/info"
            r"|/core/.+"
            r"|/homeassistant/.+"
            r")$"
        ),
        ROLE_BACKUP: re.compile(
            r"^/v2(?:"
            r"|/.+/info"
            r"|/backups.*"
            r")$"
        ),
        ROLE_MANAGER: re.compile(
            r"^/v2(?:"
            r"|/.+/info"
            r"|/apps(?:/" + RE_SLUG + r"/(?!security).+)?"
            r"|/audio/.+"
            r"|/auth/cache"
            r"|/backups.*"
            r"|/cli/.+"
            r"|/core/.+"
            r"|/dns/.+"
            r"|/docker/.+"
            r"|/jobs/.+"
            r"|/hardware/.+"
            r"|/homeassistant/.+"
            r"|/host/.+"
            r"|/mounts.*"
            r"|/multicast/.+"
            r"|/network/.+"
            r"|/observer/.+"
            r"|/os/(?!datadisk/wipe).+"
            r"|/reload_updates"
            r"|/resolution/.+"
            r"|/security/.+"
            r"|/store.*"
            r"|/supervisor/.+"
            r")$"
        ),
        ROLE_ADMIN: re.compile(r".*"),
    },
    no_security_check=re.compile(
        r"^/v2(?:"
        r"|/ingress/[-_A-Za-z0-9]+/.*"
        + _V2_FRONTEND_PATHS
        + r")$"
    ),
)

# fmt: on


def _get_app_security_patterns(request: Request) -> _AppSecurityPatterns:
    """Return the correct pattern set based on the request's API version."""
    if request.path.startswith("/v2/"):
        return _V2_PATTERNS
    return _V1_PATTERNS


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
    async def block_bad_requests(
        self, request: Request, handler: Callable[[Request], Awaitable[StreamResponse]]
    ) -> StreamResponse:
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
    async def system_validation(
        self, request: Request, handler: Callable[[Request], Awaitable[StreamResponse]]
    ) -> StreamResponse:
        """Check if core is ready to response."""
        if self.sys_core.state not in VALID_API_STATES:
            return api_return_error(
                message=f"System is not ready with state: {self.sys_core.state}"
            )

        return await handler(request)

    @middleware
    async def token_validation(
        self, request: Request, handler: Callable[[Request], Awaitable[StreamResponse]]
    ) -> StreamResponse:
        """Check security access of this layer."""
        request_from: CoreSysAttributes | None = None
        supervisor_token = extract_supervisor_token(request)
        patterns = _get_app_security_patterns(request)

        # Blacklist
        if BLACKLIST.match(request.path):
            _LOGGER.error("%s is blacklisted!", request.path)
            raise HTTPForbidden()

        # Ignore security check
        if patterns.no_security_check.match(request.path):
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
        elif patterns.core_only.match(request.path):
            _LOGGER.warning(
                "Attempted access to %s from client besides Home Assistant",
                request.path,
            )
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

        # App
        app = None
        if supervisor_token and not request_from:
            app = self.sys_apps.from_token(supervisor_token)

        # Check App API access
        if app and patterns.api_bypass.match(request.path):
            _LOGGER.debug("Passthrough %s from %s", request.path, app.slug)
            request_from = app
        elif app and app.access_hassio_api:
            # Check Role
            if patterns.role_access[app.hassio_role].match(request.path):
                _LOGGER.info("%s access from %s", request.path, app.slug)
                request_from = app
            else:
                _LOGGER.warning("%s no role for %s", request.path, app.slug)
        elif app:
            _LOGGER.warning("%s missing API permission for %s", app.slug, request.path)

        if request_from:
            request[REQUEST_FROM] = request_from
            return await handler(request)

        _LOGGER.error("Invalid token for access %s", request.path)
        raise HTTPForbidden()
