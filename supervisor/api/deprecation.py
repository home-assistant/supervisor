"""Handle deprecation of this API."""
import datetime
import logging

from aiohttp.web import Request, RequestHandler, Response, middleware

from ..addons import Addon
from ..const import REQUEST_FROM
from ..coresys import CoreSys, CoreSysAttributes
from ..homeassistant import HomeAssistant
from ..host import HostManager
from ..plugins import PluginObserver

_LOGGER: logging.Logger = logging.getLogger(__name__)

DEFAULT_GRACE_PERIOD = datetime.timedelta(seconds=10)

DEPRECATED_PATHS = {
    "/hardware/trigger": {
        "grace_period": datetime.timedelta(hours=1),
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
            origin = self.get_origin(request)
            grace = DEPRECATED_PATHS[request.path].get(
                "grace_period", DEFAULT_GRACE_PERIOD
            )
            if (
                origin not in self._trottle.get(request.path, {})
                or (now - self._trottle[request.path][origin]) > grace
            ):
                self._trottle[request.path] = {origin: now}
                self.write_log(request)

        return await handler(request)

    def write_log(self, request: Request):
        """Write the log entry."""
        request_from = request[REQUEST_FROM]
        origin = self.get_origin(request)
        more_info = ""

        if isinstance(request_from, Addon):
            addon = request_from
            if addon:
                more_info = (
                    f"please report this to the maintainer of the {addon.name} add-on"
                )
                request_from = addon.name
                if addon.need_update:
                    more_info = f"you are currently running version {addon.version}, there is an update pending for {addon.latest_version}. If that does not help {more_info}"

        if more_info == "" and DEPRECATED_PATHS[request.path].get("message"):
            more_info = DEPRECATED_PATHS[request.path]["message"]

        _LOGGER.warning(
            "Access to deprecated API '%s' detected from %s - %s",
            request.path,
            origin,
            more_info,
        )

    def get_origin(self, request: Request):
        """Determine where the request was sendt from."""
        origin = request[REQUEST_FROM]

        # Home Assistant
        if isinstance(origin, HomeAssistant):
            origin = "Home Assistant"

        # Host
        elif isinstance(origin, HostManager):
            origin = "Host"

        # Observer
        elif isinstance(origin, PluginObserver):
            origin = "observer"

        # addon
        elif isinstance(origin, Addon):
            origin = origin.name

        return origin
