"""Init file for HassIO rest api."""
import logging

from aiohttp import web

from .host import APIHost
from .supervisor import APISupervisor
from .homeassistant import APIHomeAssistant

_LOGGER = logging.getLogger(__name__)


class RestAPI(object):
    """Handle rest api for hassio."""

    def __init__(self, config, loop):
        """Initialize docker base wrapper."""
        self.config = config
        self.loop = loop
        self.webapp = web.Application(loop=self.loop)

        self._handler = None
        self.server = None

    def register_host(self, host_controll):
        """Register hostcontroll function."""
        api_host = APIHost(self.config, self.loop, host_controll)

        self.webapp.router.add_get('/host/info', api_host.info)
        self.webapp.router.add_get('/host/reboot', api_host.reboot)
        self.webapp.router.add_get('/host/shutdown', api_host.shutdown)
        self.webapp.router.add_get('/host/update', api_host.update)
        self.webapp.router.add_get(
            '/host/network/info', api_host.network_info)
        self.webapp.router.add_get(
            '/host/network/update', api_host.network_update)

    def register_supervisor(self, host_controll):
        """Register supervisor function."""
        api_supervisor = APISupervisor(self.config, self.loop, host_controll)

        self.webapp.router.add_get('/supervisor/info', api_supervisor.info)
        self.webapp.router.add_get('/supervisor/update', api_supervisor.update)

    def register_homeassistant(self, dock_homeassistant):
        """Register homeassistant function."""
        api_hass = APIHomeAssistant(self.config, self.loop, dock_homeassistant)

        self.webapp.router.add_get('/homeassistant/info', api_hass.info)
        self.webapp.router.add_get('/homeassistant/update', api_hass.update)

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
