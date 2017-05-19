"""Init file for HassIO rest api."""
import logging
from pathlib import Path

from aiohttp import web

from .addons import APIAddons
from .homeassistant import APIHomeAssistant
from .host import APIHost
from .network import APINetwork
from .supervisor import APISupervisor
from .security import APISecurity

_LOGGER = logging.getLogger(__name__)


class RestAPI(object):
    """Handle rest api for hassio."""

    def __init__(self, config, loop):
        """Initialize docker base wrapper."""
        self.config = config
        self.loop = loop
        self.webapp = web.Application(loop=self.loop)

        # service stuff
        self._handler = None
        self.server = None

    def register_host(self, host_control):
        """Register hostcontrol function."""
        api_host = APIHost(self.config, self.loop, host_control)

        self.webapp.router.add_get('/host/info', api_host.info)
        self.webapp.router.add_post('/host/reboot', api_host.reboot)
        self.webapp.router.add_post('/host/shutdown', api_host.shutdown)
        self.webapp.router.add_post('/host/update', api_host.update)

    def register_network(self, host_control):
        """Register network function."""
        api_net = APINetwork(self.config, self.loop, host_control)

        self.webapp.router.add_get('/network/info', api_net.info)
        self.webapp.router.add_post('/network/options', api_net.options)

    def register_supervisor(self, supervisor, addons, host_control):
        """Register supervisor function."""
        api_supervisor = APISupervisor(
            self.config, self.loop, supervisor, addons, host_control)

        self.webapp.router.add_get('/supervisor/ping', api_supervisor.ping)
        self.webapp.router.add_get('/supervisor/info', api_supervisor.info)
        self.webapp.router.add_get(
            '/supervisor/addons', api_supervisor.available_addons)
        self.webapp.router.add_post(
            '/supervisor/update', api_supervisor.update)
        self.webapp.router.add_post(
            '/supervisor/reload', api_supervisor.reload)
        self.webapp.router.add_post(
            '/supervisor/options', api_supervisor.options)
        self.webapp.router.add_get('/supervisor/logs', api_supervisor.logs)

    def register_homeassistant(self, dock_homeassistant):
        """Register homeassistant function."""
        api_hass = APIHomeAssistant(self.config, self.loop, dock_homeassistant)

        self.webapp.router.add_get('/homeassistant/info', api_hass.info)
        self.webapp.router.add_post('/homeassistant/update', api_hass.update)
        self.webapp.router.add_post('/homeassistant/restart', api_hass.restart)
        self.webapp.router.add_get('/homeassistant/logs', api_hass.logs)

    def register_addons(self, addons):
        """Register homeassistant function."""
        api_addons = APIAddons(self.config, self.loop, addons)

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
        self.webapp.router.add_get('/addons/{addon}/logs', api_addons.logs)

    def register_security(self):
        """Register security function."""
        api_security = APISecurity(self.config, self.loop)

        self.webapp.router.add_get('/security/info', api_security.info)
        self.webapp.router.add_post('/security/options', api_security.options)
        self.webapp.router.add_post('/security/totp', api_security.totp)
        self.webapp.router.add_post('/security/session', api_security.session)

    def register_panel(self):
        """Register panel for homeassistant."""
        panel = Path(__file__).parents[1].joinpath('panel/hassio-main.html')

        self.webapp.router.register_resource(
            web.StaticResource('/panel', str(panel)))

    async def start(self):
        """Run rest api webserver."""
        self._handler = self.webapp.make_handler(loop=self.loop)

        try:
            self.server = await self.loop.create_server(
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
            await self._handler.finish_connections(60)
        await self.webapp.cleanup()
