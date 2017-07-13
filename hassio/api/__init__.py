"""Init file for HassIO rest api."""
import logging
from pathlib import Path

from aiohttp import web

from .cluster import APICluster
from .cluster_management import APIClusterManagement
from .cluster_addons import APIClusterAddons
from .addons import APIAddons
from .homeassistant import APIHomeAssistant
from .host import APIHost
from .network import APINetwork
from .security import APISecurity
from .snapshots import APISnapshots
from .supervisor import APISupervisor

_LOGGER = logging.getLogger(__name__)


class RestAPIBase(object):
    """Base REST API server."""

    def __init__(self, config, loop):
        """Initialize docker base wrapper."""
        self.config = config
        self.loop = loop
        self.webapp = web.Application(loop=self.loop)

        # service stuff
        self._handler = None
        self.server = None

    async def start(self, port):
        """Run rest api webserver."""
        self._handler = self.webapp.make_handler(loop=self.loop)

        try:
            self.server = await self.loop.create_server(
                self._handler, "0.0.0.0", port)
        except OSError as err:
            _LOGGER.fatal(
                "Failed to create HTTP server at 0.0.0.0:%d -> %s", port, err)

    async def stop(self):
        """Stop rest api webserver."""
        if self.server:
            self.server.close()
            await self.server.wait_closed()
        await self.webapp.shutdown()

        if self._handler:
            await self._handler.finish_connections(60)
        await self.webapp.cleanup()


class RestAPI(RestAPIBase):
    """Handle rest api for hassio."""

    def __init__(self, config, loop):
        super().__init__(config, loop)
        # shared api
        self.api_addons = None

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

    def register_supervisor(self, supervisor, snapshots, addons, host_control,
                            websession, cluster):
        """Register supervisor function."""
        api_supervisor = APISupervisor(
            self.config, self.loop, supervisor, snapshots, addons,
            host_control, websession, cluster)

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
        self.webapp.router.add_post('/homeassistant/options', api_hass.options)
        self.webapp.router.add_post('/homeassistant/update', api_hass.update)
        self.webapp.router.add_post('/homeassistant/restart', api_hass.restart)
        self.webapp.router.add_get('/homeassistant/logs', api_hass.logs)

    def register_addons(self, addons, cluster):
        """Register homeassistant function."""
        self.api_addons = APIAddons(self.config, self.loop, addons, cluster)

        self.webapp.router.add_get('/addons', self.api_addons.list)
        self.webapp.router.add_post('/addons/reload', self.api_addons.reload)

        self.webapp.router.add_get('/addons/{addon}/info',
                                   self.api_addons.info)
        self.webapp.router.add_get('/addons/{addon}/{node}/info',
                                   self.api_addons.info)

        self.webapp.router.add_post('/addons/{addon}/install',
                                    self.api_addons.install)
        self.webapp.router.add_post('/addons/{addon}/{node}/install',
                                    self.api_addons.install)

        self.webapp.router.add_post('/addons/{addon}/uninstall',
                                    self.api_addons.uninstall)
        self.webapp.router.add_post('/addons/{addon}/{node}/uninstall',
                                    self.api_addons.uninstall)

        self.webapp.router.add_post('/addons/{addon}/start',
                                    self.api_addons.start)
        self.webapp.router.add_post('/addons/{addon}/{node}/start',
                                    self.api_addons.start)

        self.webapp.router.add_post('/addons/{addon}/stop',
                                    self.api_addons.stop)
        self.webapp.router.add_post('/addons/{addon}/{node}/stop',
                                    self.api_addons.stop)

        self.webapp.router.add_post('/addons/{addon}/restart',
                                    self.api_addons.restart)
        self.webapp.router.add_post('/addons/{addon}/{node}/restart',
                                    self.api_addons.restart)

        self.webapp.router.add_post('/addons/{addon}/update',
                                    self.api_addons.update)
        self.webapp.router.add_post('/addons/{addon}/{node}/update',
                                    self.api_addons.update)

        self.webapp.router.add_post('/addons/{addon}/options',
                                    self.api_addons.options)
        self.webapp.router.add_post('/addons/{addon}/{node}/options',
                                    self.api_addons.options)

        self.webapp.router.add_get('/addons/{addon}/logs',
                                   self.api_addons.logs)
        self.webapp.router.add_get('/addons/{addon}/{node}/logs',
                                   self.api_addons.logs)

    def register_security(self):
        """Register security function."""
        api_security = APISecurity(self.config, self.loop)

        self.webapp.router.add_get('/security/info', api_security.info)
        self.webapp.router.add_post('/security/options', api_security.options)
        self.webapp.router.add_post('/security/totp', api_security.totp)
        self.webapp.router.add_post('/security/session', api_security.session)

    def register_snapshots(self, snapshots):
        """Register snapshots function."""
        api_snapshots = APISnapshots(self.config, self.loop, snapshots)

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

    def register_cluster(self, cluster):
        """Register cluster function."""
        api_cluster = APICluster(cluster, self.config, self.loop)

        self.webapp.router.add_get('/cluster/info', api_cluster.info)
        self.webapp.router.add_post('/cluster/leave',
                                    api_cluster.switch_to_master)
        self.webapp.router.add_post('/cluster/register',
                                    api_cluster.switch_to_slave)
        self.webapp.router.add_post('/cluster/{node}/leave',
                                    api_cluster.remove_node)

    def register_panel(self):
        """Register panel for homeassistant."""
        panel = Path(__file__).parents[1].joinpath('panel/hassio-main.html')

        def get_panel(request):
            """Return file response with panel."""
            return web.FileResponse(panel)

        self.webapp.router.add_get('/panel', get_panel)


class ClusterAPI(RestAPIBase):
    """Cluster management REST API."""

    def register_cluster_management(self, cluster):
        """Registering cluster management functions."""
        api_cluster = APIClusterManagement(cluster, self.config, self.loop)

        self.webapp.router.add_post('/cluster/register', api_cluster.register)
        self.webapp.router.add_post('/cluster/leave', api_cluster.leave)
        self.webapp.router.add_post('/cluster/ping', api_cluster.ping)
        self.webapp.router.add_post('/cluster/kick', api_cluster.kick)

    def register_cluster_addons(self, cluster, addons, api_addons):
        """Registering cluster addons functions."""
        api_cluster_addons = APIClusterAddons(cluster, self.config,
                                              addons, api_addons, self.loop)

        self.webapp.router.add_post('/cluster/addons/{addon}/install',
                                    api_cluster_addons.install)
        self.webapp.router.add_post('/cluster/addons/{addon}/uninstall',
                                    api_cluster_addons.uninstall)
        self.webapp.router.add_post('/cluster/addons/{addon}/info',
                                    api_cluster_addons.info)
        self.webapp.router.add_post('/cluster/addons/{addon}/start',
                                    api_cluster_addons.start)
        self.webapp.router.add_post('/cluster/addons/{addon}/stop',
                                    api_cluster_addons.stop)
        self.webapp.router.add_post('/cluster/addons/{addon}/restart',
                                    api_cluster_addons.restart)
        self.webapp.router.add_post('/cluster/addons/{addon}/update',
                                    api_cluster_addons.update)
        self.webapp.router.add_post('/cluster/addons/{addon}/options',
                                    api_cluster_addons.options)
        self.webapp.router.add_post('/cluster/addons/{addon}/logs',
                                    api_cluster_addons.logs)
