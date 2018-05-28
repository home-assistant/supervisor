"""Init file for HassIO rest api."""
import logging
from pathlib import Path

from aiohttp import web

from .addons import APIAddons
from .discovery import APIDiscovery
from .homeassistant import APIHomeAssistant
from .hardware import APIHardware
from .host import APIHost
from .proxy import APIProxy
from .supervisor import APISupervisor
from .snapshots import APISnapshots
from .services import APIServices
from .security import SecurityMiddleware
from ..coresys import CoreSysAttributes

_LOGGER = logging.getLogger(__name__)


class RestAPI(CoreSysAttributes):
    """Handle rest api for hassio."""

    def __init__(self, coresys):
        """Initialize docker base wrapper."""
        self.coresys = coresys
        self.security = SecurityMiddleware(coresys)
        self.webapp = web.Application(
            middlewares=[self.security.token_validation], loop=coresys.loop)

        # service stuff
        self._handler = None
        self.server = None

    async def load(self):
        """Register REST API Calls."""
        self._register_supervisor()
        self._register_host()
        self._register_hardware()
        self._register_homeassistant()
        self._register_proxy()
        self._register_panel()
        self._register_addons()
        self._register_snapshots()
        self._register_discovery()
        self._register_services()

    def _register_host(self):
        """Register hostcontrol function."""
        api_host = APIHost()
        api_host.coresys = self.coresys

        self.webapp.add_routes([
            web.get('/host/info', api_host.info),
            web.post('/host/reboot', api_host.reboot),
            web.post('/host/shutdown', api_host.shutdown),
            web.post('/host/update', api_host.update),
            web.post('/host/reload', api_host.reload),
        ])

    def _register_hardware(self):
        """Register hardware function."""
        api_hardware = APIHardware()
        api_hardware.coresys = self.coresys

        self.webapp.add_routes([
            web.get('/hardware/info', api_hardware.info),
            web.get('/hardware/audio', api_hardware.audio),
        ])

    def _register_supervisor(self):
        """Register supervisor function."""
        api_supervisor = APISupervisor()
        api_supervisor.coresys = self.coresys

        self.webapp.add_routes([
            web.get('/supervisor/ping', api_supervisor.ping),
            web.get('/supervisor/info', api_supervisor.info),
            web.get('/supervisor/stats', api_supervisor.stats),
            web.get('/supervisor/logs', api_supervisor.logs),
            web.post('/supervisor/update', api_supervisor.update),
            web.post('/supervisor/reload', api_supervisor.reload),
            web.post('/supervisor/options', api_supervisor.options),
        ])

    def _register_homeassistant(self):
        """Register homeassistant function."""
        api_hass = APIHomeAssistant()
        api_hass.coresys = self.coresys

        self.webapp.add_routes([
            web.get('/homeassistant/info', api_hass.info),
            web.get('/homeassistant/logs', api_hass.logs),
            web.get('/homeassistant/stats', api_hass.stats),
            web.post('/homeassistant/options', api_hass.options),
            web.post('/homeassistant/update', api_hass.update),
            web.post('/homeassistant/restart', api_hass.restart),
            web.post('/homeassistant/stop', api_hass.stop),
            web.post('/homeassistant/start', api_hass.start),
            web.post('/homeassistant/check', api_hass.check),
        ])

    def _register_proxy(self):
        """Register HomeAssistant API Proxy."""
        api_proxy = APIProxy()
        api_proxy.coresys = self.coresys

        self.webapp.add_routes([
            web.get('/homeassistant/api/websocket', api_proxy.websocket),
            web.get('/homeassistant/websocket', api_proxy.websocket),
            web.get('/homeassistant/api/stream', api_proxy.stream),
            web.post('/homeassistant/api/{path:.+}', api_proxy.api),
            web.get('/homeassistant/api/{path:.+}', api_proxy.api),
            web.get('/homeassistant/api/', api_proxy.api),
        ])

    def _register_addons(self):
        """Register homeassistant function."""
        api_addons = APIAddons()
        api_addons.coresys = self.coresys

        self.webapp.add_routes([
            web.get('/addons', api_addons.list),
            web.post('/addons/reload', api_addons.reload),
            web.get('/addons/{addon}/info', api_addons.info),
            web.post('/addons/{addon}/install', api_addons.install),
            web.post('/addons/{addon}/uninstall', api_addons.uninstall),
            web.post('/addons/{addon}/start', api_addons.start),
            web.post('/addons/{addon}/stop', api_addons.stop),
            web.post('/addons/{addon}/restart', api_addons.restart),
            web.post('/addons/{addon}/update', api_addons.update),
            web.post('/addons/{addon}/options', api_addons.options),
            web.post('/addons/{addon}/rebuild', api_addons.rebuild),
            web.get('/addons/{addon}/logs', api_addons.logs),
            web.get('/addons/{addon}/icon', api_addons.icon),
            web.get('/addons/{addon}/logo', api_addons.logo),
            web.get('/addons/{addon}/changelog', api_addons.changelog),
            web.post('/addons/{addon}/stdin', api_addons.stdin),
            web.get('/addons/{addon}/stats', api_addons.stats),
        ])

    def _register_snapshots(self):
        """Register snapshots function."""
        api_snapshots = APISnapshots()
        api_snapshots.coresys = self.coresys

        self.webapp.add_routes([
            web.get('/snapshots', api_snapshots.list),
            web.post('/snapshots/reload', api_snapshots.reload),
            web.post('/snapshots/new/full', api_snapshots.snapshot_full),
            web.post('/snapshots/new/partial', api_snapshots.snapshot_partial),
            web.post('/snapshots/new/upload', api_snapshots.upload),
            web.get('/snapshots/{snapshot}/info', api_snapshots.info),
            web.post('/snapshots/{snapshot}/remove', api_snapshots.remove),
            web.post('/snapshots/{snapshot}/restore/full',
                     api_snapshots.restore_full),
            web.post('/snapshots/{snapshot}/restore/partial',
                     api_snapshots.restore_partial),
            web.get('/snapshots/{snapshot}/download', api_snapshots.download),
        ])

    def _register_services(self):
        api_services = APIServices()
        api_services.coresys = self.coresys

        self.webapp.add_routes([
            web.get('/services', api_services.list),
            web.get('/services/{service}', api_services.get_service),
            web.post('/services/{service}', api_services.set_service),
            web.delete('/services/{service}', api_services.del_service),
        ])

    def _register_discovery(self):
        api_discovery = APIDiscovery()
        api_discovery.coresys = self.coresys

        self.webapp.add_routes([
            web.get('/services/discovery', api_discovery.list),
            web.get('/services/discovery/{uuid}', api_discovery.get_discovery),
            web.delete('/services/discovery/{uuid}',
                       api_discovery.del_discovery),
            web.post('/services/discovery', api_discovery.set_discovery),
        ])

    def _register_panel(self):
        """Register panel for homeassistant."""
        panel_dir = Path(__file__).parent.joinpath("panel")

        def create_response(panel_file):
            """Create a function to generate a response."""
            path = panel_dir.joinpath(f"{panel_file!s}.html")
            return lambda request: web.FileResponse(path)

        # This route is for backwards compatibility with HA < 0.58
        self.webapp.add_routes([
            web.get('/panel', create_response('hassio-main-es5'))])

        # This route is for backwards compatibility with HA 0.58 - 0.61
        self.webapp.add_routes([
            web.get('/panel_es5', create_response('hassio-main-es5')),
            web.get('/panel_latest', create_response('hassio-main-latest')),
        ])

        # This route is for HA > 0.61
        self.webapp.add_routes([web.static('/app-es5', panel_dir)])

    async def start(self):
        """Run rest api webserver."""
        self._handler = self.webapp.make_handler()

        try:
            self.server = await self.sys_loop.create_server(
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
