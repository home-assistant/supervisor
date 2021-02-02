"""Handle deprecation of this API."""
import datetime
import logging

from aiohttp.web import Request, RequestHandler, Response, middleware

from ..coresys import CoreSys, CoreSysAttributes
from .utils import excract_supervisor_token

_LOGGER: logging.Logger = logging.getLogger(__name__)

DEFAULT_GRACE_PERIOD = datetime.timedelta(seconds=10)

DEPRECATED_PATHS = {
    "/hardware/trigger": {
        "message": "Ignoring DEPRECATED hardware trigger function call",
        "grace_period": datetime.timedelta(seconds=60),
    }
}


class DeprecationMiddleware(CoreSysAttributes):
    """Deprecation middleware functions."""

    def __init__(self, coresys: CoreSys):
        """Initialize security middleware."""
        self.coresys: CoreSys = coresys
        self._trottle = {}

    @middleware
    async def check_deprecation(
        self, request: Request, handler: RequestHandler
    ) -> Response:
        """Check if the requested path is deprecated."""
        if request.path in DEPRECATED_PATHS:
            now = datetime.datetime.now()
            if request.path not in self._trottle or (
                now - self._trottle[request.path]
            ) > DEPRECATED_PATHS[request.path].get(
                "grace_period", DEFAULT_GRACE_PERIOD
            ):
                self._trottle[request.path] = now
                self.write_log(request)

        return await handler(request)

    def write_log(self, request: Request):
        """Write the log entry."""
        request_from = "unknown"
        more_info = None
        supervisor_token = excract_supervisor_token(request)

        if supervisor_token == self.sys_homeassistant.supervisor_token:
            request_from = "Home Assistant"

        # Host
        elif supervisor_token == self.sys_plugins.cli.supervisor_token:
            request_from = "Host"

        # Observer
        elif supervisor_token == self.sys_plugins.observer.supervisor_token:
            request_from = "observer"

        # addon
        else:
            addon = self.sys_addons.from_token(supervisor_token)
            if addon:
                request_from = addon.name

        if DEPRECATED_PATHS[request.path].get("message"):
            more_info = DEPRECATED_PATHS[request.path]["message"]
        else:
            more_info = f"report this to the maintainer of {request_from}"

        _LOGGER.warning(
            "Access to deprecated API '%s' detected from %s - %s",
            request.path,
            request_from,
            more_info,
        )
