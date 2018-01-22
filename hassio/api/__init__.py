"""Init file for HassIO rest api."""
import logging
from pathlib import Path

from aiohttp import web

from .addons import APIAddons
from .homeassistant import APIHomeAssistant
from .host import APIHost
from .network import APINetwork
from .proxy import APIProxy
from .supervisor import APISupervisor
from .snapshots import APISnapshots
from ..coresys import CoreSysAttributes

_LOGGER = logging.getLogger(__name__)


class RestAPI(CoreSysAttributes):
    """Handle rest api for hassio."""

    def __init__(self, coresys):
        """Initialize docker base wrapper."""
        self.coresys = coresys
        self.webapp = web.Application(loop=self._loop)

        # service stuff
        self._handler = None
        self.server = None

    async def load(self):
        """Register REST API Calls."""
        self._register_supervisor()
        self._register_host()
        self._register_homeassistant()
        self._register_proxy()
        self._register_panel()
        self._register_addons()
        self._register_snapshots()
        self._register_network()

    def _register_host(self):
        """Register hostcontrol function."""
        api_host = APIHost()
        api_host.coresys = self.coresys

        self.webapp.router.add_get('/host/info', api_host.info)
        self.webapp.router.add_get('/host/hardware', api_host.hardware)
        self.webapp.router.add_post('/host/reboot', api_host.reboot)
        self.webapp.router.add_post('/host/shutdown', api_host.shutdown)
        self.webapp.router.add_post('/host/update', api_host.update)
        self.webapp.router.add_post('/host/options', api_host.options)
        self.webapp.router.add_post('/host/reload', api_host.reload)

    def _register_network(self):
        """Register network function."""
        api_net = APINetwork()
        api_net.coresys = self.coresys

        self.webapp.router.add_get('/network/info', api_net.info)
        self.webapp.router.add_post('/network/options', api_net.options)

    def _register_supervisor(self):
        """Register supervisor function."""
        api_supervisor = APISupervisor()
        api_supervisor.coresys = self.coresys

        self.webapp.router.add_get('/supervisor/ping', api_supervisor.ping)
        self.webapp.router.add_get('/supervisor/info', api_supervisor.info)
        self.webapp.router.add_get('/supervisor/stats', api_supervisor.stats)
        self.webapp.router.add_post(
            '/supervisor/update', api_supervisor.update)
        self.webapp.router.add_post(
            '/supervisor/reload', api_supervisor.reload)
        self.webapp.router.add_post(
            '/supervisor/options', api_supervisor.options)
        self.webapp.router.add_get('/supervisor/logs', api_supervisor.logs)

    def _register_homeassistant(self):
        """Register homeassistant function."""
        api_hass = APIHomeAssistant()
        api_hass.coresys = self.coresys

        self.webapp.router.add_get('/homeassistant/info', api_hass.info)
        self.webapp.router.add_get('/homeassistant/logs', api_hass.logs)
        self.webapp.router.add_get('/homeassistant/stats', api_hass.stats)
        self.webapp.router.add_post('/homeassistant/options', api_hass.options)
        self.webapp.router.add_post('/homeassistant/update', api_hass.update)
        self.webapp.router.add_post('/homeassistant/restart', api_hass.restart)
        self.webapp.router.add_post('/homeassistant/stop', api_hass.stop)
        self.webapp.router.add_post('/homeassistant/start', api_hass.start)
        self.webapp.router.add_post('/homeassistant/check', api_hass.check)

    def _register_proxy(self):
        """Register HomeAssistant API Proxy."""
        api_proxy = APIProxy()
        api_proxy.coresys = self.coresys

        self.webapp.router.add_get(
            '/homeassistant/api/websocket', api_proxy.websocket)
        self.webapp.router.add_get(
            '/homeassistant/websocket', api_proxy.websocket)
        self.webapp.router.add_get(
            '/homeassistant/api/stream', api_proxy.stream)
        self.webapp.router.add_post(
            '/homeassistant/api/{path:.+}', api_proxy.api)
        self.webapp.router.add_get(
            '/homeassistant/api/{path:.+}', api_proxy.api)
        self.webapp.router.add_get(
            '/homeassistant/api/', api_proxy.api)

    def _register_addons(self):
        """Register homeassistant function."""
        api_addons = APIAddons()
        api_addons.coresys = self.coresys

        self.webapp.router.add_get('/addons', api_addons.list)
        self.webapp.router.add_post('/addons/reload', api_addons.reload)
        self.webapp.router.add_get('/addons/{addon}/info', api_addons.info)
        self.webapp.router.add_post(
            '/addons/{addon}/install', api_addons.install)
        self.webapp.router.add_post(
            '/addons/{addon}/uninstall', api_addons.uninstall)
        self.webapp.router.add_post('/addons/{addon}/start', api_addons.start)
        self.webapp.router.add_post('/addons/{addon}/stop', api_addons.stop)
        self.webapp.router.add_post(
            '/addons/{addon}/restart', api_addons.restart)
        self.webapp.router.add_post(
            '/addons/{addon}/update', api_addons.update)
        self.webapp.router.add_post(
            '/addons/{addon}/options', api_addons.options)
        self.webapp.router.add_post(
            '/addons/{addon}/rebuild', api_addons.rebuild)
        self.webapp.router.add_get('/addons/{addon}/logs', api_addons.logs)
        self.webapp.router.add_get('/addons/{addon}/logo', api_addons.logo)
        self.webapp.router.add_get(
            '/addons/{addon}/changelog', api_addons.changelog)
        self.webapp.router.add_post('/addons/{addon}/stdin', api_addons.stdin)
        self.webapp.router.add_get('/addons/{addon}/stats', api_addons.stats)

    def _register_snapshots(self):
        """Register snapshots function."""
        api_snapshots = APISnapshots()
        api_snapshots.coresys = self.coresys

        self.webapp.router.add_get('/snapshots', api_snapshots.list)
        self.webapp.router.add_post('/snapshots/reload', api_snapshots.reload)

        self.webapp.router.add_post(
            '/snapshots/new/full', api_snapshots.snapshot_full)
        self.webapp.router.add_post(
            '/snapshots/new/partial', api_snapshots.snapshot_partial)

        self.webapp.router.add_get(
            '/snapshots/{snapshot}/info', api_snapshots.info)
        self.webapp.router.add_post(
            '/snapshots/{snapshot}/remove', api_snapshots.remove)
        self.webapp.router.add_post(
            '/snapshots/{snapshot}/restore/full', api_snapshots.restore_full)
        self.webapp.router.add_post(
            '/snapshots/{snapshot}/restore/partial',
            api_snapshots.restore_partial)

    def _register_panel(self):
        """Register panel for homeassistant."""
        def create_panel_response(build_type):
            """Create a function to generate a response."""
            path = Path(__file__).parent.joinpath(
                f"panel/{build_type}.html")
            return lambda request: web.FileResponse(path)

        # This route is for backwards compatibility with HA < 0.58
        self.webapp.router.add_get(
            '/panel', create_panel_response('hassio-main-es5'))
        self.webapp.router.add_get(
            '/panel_es5', create_panel_response('hassio-main-es5'))
        self.webapp.router.add_get(
            '/panel_latest', create_panel_response('hassio-main-latest'))
        
        # This route is for HA > 0.61
        self.webapp.router.add_get(
            '/app-es5', create_panel_response('index'))
        self.webapp.router.add_get(
            '/app-es5', create_panel_response('hassio-app'))

    async def start(self):
        """Run rest api webserver."""
        self._handler = self.webapp.make_handler(loop=self._loop)

        try:
            self.server = await self._loop.create_server(
                self._handler, "0.0.0.0", "80")
        except OSError as err:
            _LOGGER.fatal(
                "Failed to create HTTP server at 0.0.0.0:80 -> %s", err)

    async def stop(self):
        """Stop rest api webserver."""
        if self.server:
            self.server.close()
            await self.server.wait_closed()
        await self.webapp.shutdown()

        if self._handler:
            await self._handler.shutdown(60)
        await self.webapp.cleanup()
