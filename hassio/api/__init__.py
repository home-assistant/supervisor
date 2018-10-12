"""Init file for Hass.io RESTful API."""
import logging
from pathlib import Path

from aiohttp import web

from .addons import APIAddons
from .auth import APIAuth
from .discovery import APIDiscovery
from .homeassistant import APIHomeAssistant
from .hardware import APIHardware
from .host import APIHost
from .hassos import APIHassOS
from .info import APIInfo
from .proxy import APIProxy
from .supervisor import APISupervisor
from .snapshots import APISnapshots
from .services import APIServices
from .security import SecurityMiddleware
from ..coresys import CoreSysAttributes

_LOGGER = logging.getLogger(__name__)


class RestAPI(CoreSysAttributes):
    """Handle RESTful API for Hass.io."""

    def __init__(self, coresys):
        """Initialize Docker base wrapper."""
        self.coresys = coresys
        self.security = SecurityMiddleware(coresys)
        self.webapp = web.Application(
            middlewares=[self.security.token_validation], loop=coresys.loop)

        # service stuff
        self._runner = web.AppRunner(self.webapp)
        self._site = None

    async def load(self):
        """Register REST API Calls."""
        self._register_supervisor()
        self._register_host()
        self._register_hassos()
        self._register_hardware()
        self._register_homeassistant()
        self._register_proxy()
        self._register_panel()
        self._register_addons()
        self._register_snapshots()
        self._register_discovery()
        self._register_services()
        self._register_info()
        self._register_auth()

    def _register_host(self):
        """Register hostcontrol functions."""
        api_host = APIHost()
        api_host.coresys = self.coresys

        self.webapp.add_routes([
            web.get('/host/info', api_host.info),
            web.post('/host/reboot', api_host.reboot),
            web.post('/host/shutdown', api_host.shutdown),
            web.post('/host/reload', api_host.reload),
            web.post('/host/options', api_host.options),
            web.get('/host/services', api_host.services),
            web.post('/host/services/{service}/stop', api_host.service_stop),
            web.post('/host/services/{service}/start', api_host.service_start),
            web.post(
                '/host/services/{service}/restart', api_host.service_restart),
            web.post(
                '/host/services/{service}/reload', api_host.service_reload),
        ])

    def _register_hassos(self):
        """Register HassOS functions."""
        api_hassos = APIHassOS()
        api_hassos.coresys = self.coresys

        self.webapp.add_routes([
            web.get('/hassos/info', api_hassos.info),
            web.post('/hassos/update', api_hassos.update),
            web.post('/hassos/update/cli', api_hassos.update_cli),
            web.post('/hassos/config/sync', api_hassos.config_sync),
        ])

    def _register_hardware(self):
        """Register hardware functions."""
        api_hardware = APIHardware()
        api_hardware.coresys = self.coresys

        self.webapp.add_routes([
            web.get('/hardware/info', api_hardware.info),
            web.get('/hardware/audio', api_hardware.audio),
        ])

    def _register_info(self):
        """Register info functions."""
        api_info = APIInfo()
        api_info.coresys = self.coresys

        self.webapp.add_routes([
            web.get('/info', api_info.info),
        ])

    def _register_auth(self):
        """Register auth functions."""
        api_auth = APIAuth()
        api_auth.coresys = self.coresys

        self.webapp.add_routes([
            web.post('/auth', api_auth.auth),
        ])

    def _register_supervisor(self):
        """Register Supervisor functions."""
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
        """Register Home Assistant functions."""
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
        """Register Home Assistant API Proxy."""
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
        """Register Add-on functions."""
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
            web.post('/addons/{addon}/security', api_addons.security),
            web.get('/addons/{addon}/stats', api_addons.stats),
        ])

    def _register_snapshots(self):
        """Register snapshots functions."""
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
        """Register services functions."""
        api_services = APIServices()
        api_services.coresys = self.coresys

        self.webapp.add_routes([
            web.get('/services', api_services.list),
            web.get('/services/{service}', api_services.get_service),
            web.post('/services/{service}', api_services.set_service),
            web.delete('/services/{service}', api_services.del_service),
        ])

    def _register_discovery(self):
        """Register discovery functions."""
        api_discovery = APIDiscovery()
        api_discovery.coresys = self.coresys

        self.webapp.add_routes([
            web.get('/discovery', api_discovery.list),
            web.get('/discovery/{uuid}', api_discovery.get_discovery),
            web.delete('/discovery/{uuid}',
                       api_discovery.del_discovery),
            web.post('/discovery', api_discovery.set_discovery),
        ])

    def _register_panel(self):
        """Register panel for Home Assistant."""
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

        # This route is for backwards compatibility with HA 0.62 - 0.70
        self.webapp.add_routes([
            web.get('/app-es5/index.html', create_response('index')),
            web.get('/app-es5/hassio-app.html', create_response('hassio-app')),
        ])

        # This route is for HA > 0.70
        self.webapp.add_routes([web.static('/app', panel_dir)])

    async def start(self):
        """Run RESTful API webserver."""
        await self._runner.setup()
        self._site = web.TCPSite(
            self._runner, host="0.0.0.0", port=80, shutdown_timeout=5)

        try:
            await self._site.start()
        except OSError as err:
            _LOGGER.fatal(
                "Failed to create HTTP server at 0.0.0.0:80 -> %s", err)
        else:
            _LOGGER.info("Start API on %s", self.sys_docker.network.supervisor)

    async def stop(self):
        """Stop RESTful API webserver."""
        if not self._site:
            return

        # Shutdown running API
        await self._site.stop()
        await self._runner.cleanup()

        _LOGGER.info("Stop API on %s", self.sys_docker.network.supervisor)
