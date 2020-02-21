"""Init file for Supervisor RESTful API."""
import logging
from pathlib import Path
from typing import Optional

from aiohttp import web

from ..coresys import CoreSys, CoreSysAttributes
from .addons import APIAddons
from .auth import APIAuth
from .discovery import APIDiscovery
from .dns import APICoreDNS
from .hardware import APIHardware
from .hassos import APIHassOS
from .homeassistant import APIHomeAssistant
from .host import APIHost
from .info import APIInfo
from .ingress import APIIngress
from .proxy import APIProxy
from .security import SecurityMiddleware
from .services import APIServices
from .snapshots import APISnapshots
from .supervisor import APISupervisor

_LOGGER: logging.Logger = logging.getLogger(__name__)


MAX_CLIENT_SIZE: int = 1024 ** 2 * 16


class RestAPI(CoreSysAttributes):
    """Handle RESTful API for Supervisor."""

    def __init__(self, coresys: CoreSys):
        """Initialize Docker base wrapper."""
        self.coresys: CoreSys = coresys
        self.security: SecurityMiddleware = SecurityMiddleware(coresys)
        self.webapp: web.Application = web.Application(
            client_max_size=MAX_CLIENT_SIZE,
            middlewares=[self.security.token_validation],
        )

        # service stuff
        self._runner: web.AppRunner = web.AppRunner(self.webapp)
        self._site: Optional[web.TCPSite] = None

    async def load(self) -> None:
        """Register REST API Calls."""
        self._register_supervisor()
        self._register_host()
        self._register_hassos()
        self._register_hardware()
        self._register_homeassistant()
        self._register_proxy()
        self._register_panel()
        self._register_addons()
        self._register_ingress()
        self._register_snapshots()
        self._register_discovery()
        self._register_services()
        self._register_info()
        self._register_auth()
        self._register_dns()

    def _register_host(self) -> None:
        """Register hostcontrol functions."""
        api_host = APIHost()
        api_host.coresys = self.coresys

        self.webapp.add_routes(
            [
                web.get("/host/info", api_host.info),
                web.post("/host/reboot", api_host.reboot),
                web.post("/host/shutdown", api_host.shutdown),
                web.post("/host/reload", api_host.reload),
                web.post("/host/options", api_host.options),
                web.get("/host/services", api_host.services),
                web.post("/host/services/{service}/stop", api_host.service_stop),
                web.post("/host/services/{service}/start", api_host.service_start),
                web.post("/host/services/{service}/restart", api_host.service_restart),
                web.post("/host/services/{service}/reload", api_host.service_reload),
            ]
        )

    def _register_hassos(self) -> None:
        """Register HassOS functions."""
        api_hassos = APIHassOS()
        api_hassos.coresys = self.coresys

        self.webapp.add_routes(
            [
                web.get("/os/info", api_hassos.info),
                web.post("/os/update", api_hassos.update),
                web.post("/os/update/cli", api_hassos.update_cli),
                web.post("/os/config/sync", api_hassos.config_sync),
                # Remove with old Supervisor fallback
                web.get("/hassos/info", api_hassos.info),
                web.post("/hassos/update", api_hassos.update),
                web.post("/hassos/update/cli", api_hassos.update_cli),
                web.post("/hassos/config/sync", api_hassos.config_sync),
            ]
        )

    def _register_hardware(self) -> None:
        """Register hardware functions."""
        api_hardware = APIHardware()
        api_hardware.coresys = self.coresys

        self.webapp.add_routes(
            [
                web.get("/hardware/info", api_hardware.info),
                web.get("/hardware/audio", api_hardware.audio),
                web.post("/hardware/trigger", api_hardware.trigger),
            ]
        )

    def _register_info(self) -> None:
        """Register info functions."""
        api_info = APIInfo()
        api_info.coresys = self.coresys

        self.webapp.add_routes([web.get("/info", api_info.info)])

    def _register_auth(self) -> None:
        """Register auth functions."""
        api_auth = APIAuth()
        api_auth.coresys = self.coresys

        self.webapp.add_routes(
            [web.post("/auth", api_auth.auth), web.post("/auth/reset", api_auth.reset)]
        )

    def _register_supervisor(self) -> None:
        """Register Supervisor functions."""
        api_supervisor = APISupervisor()
        api_supervisor.coresys = self.coresys

        self.webapp.add_routes(
            [
                web.get("/supervisor/ping", api_supervisor.ping),
                web.get("/supervisor/info", api_supervisor.info),
                web.get("/supervisor/stats", api_supervisor.stats),
                web.get("/supervisor/logs", api_supervisor.logs),
                web.post("/supervisor/update", api_supervisor.update),
                web.post("/supervisor/reload", api_supervisor.reload),
                web.post("/supervisor/options", api_supervisor.options),
                web.post("/supervisor/repair", api_supervisor.repair),
            ]
        )

    def _register_homeassistant(self) -> None:
        """Register Home Assistant functions."""
        api_hass = APIHomeAssistant()
        api_hass.coresys = self.coresys

        self.webapp.add_routes(
            [
                web.get("/core/info", api_hass.info),
                web.get("/core/logs", api_hass.logs),
                web.get("/core/stats", api_hass.stats),
                web.post("/core/options", api_hass.options),
                web.post("/core/update", api_hass.update),
                web.post("/core/restart", api_hass.restart),
                web.post("/core/stop", api_hass.stop),
                web.post("/core/start", api_hass.start),
                web.post("/core/check", api_hass.check),
                web.post("/core/rebuild", api_hass.rebuild),
                # Remove with old Supervisor fallback
                web.get("/homeassistant/info", api_hass.info),
                web.get("/homeassistant/logs", api_hass.logs),
                web.get("/homeassistant/stats", api_hass.stats),
                web.post("/homeassistant/options", api_hass.options),
                web.post("/homeassistant/update", api_hass.update),
                web.post("/homeassistant/restart", api_hass.restart),
                web.post("/homeassistant/stop", api_hass.stop),
                web.post("/homeassistant/start", api_hass.start),
                web.post("/homeassistant/check", api_hass.check),
                web.post("/homeassistant/rebuild", api_hass.rebuild),
            ]
        )

    def _register_proxy(self) -> None:
        """Register Home Assistant API Proxy."""
        api_proxy = APIProxy()
        api_proxy.coresys = self.coresys

        self.webapp.add_routes(
            [
                web.get("/core/api/websocket", api_proxy.websocket),
                web.get("/core/websocket", api_proxy.websocket),
                web.get("/core/api/stream", api_proxy.stream),
                web.post("/core/api/{path:.+}", api_proxy.api),
                web.get("/core/api/{path:.+}", api_proxy.api),
                web.get("/core/api/", api_proxy.api),
                # Remove with old Supervisor fallback
                web.get("/homeassistant/api/websocket", api_proxy.websocket),
                web.get("/homeassistant/websocket", api_proxy.websocket),
                web.get("/homeassistant/api/stream", api_proxy.stream),
                web.post("/homeassistant/api/{path:.+}", api_proxy.api),
                web.get("/homeassistant/api/{path:.+}", api_proxy.api),
                web.get("/homeassistant/api/", api_proxy.api),
            ]
        )

    def _register_addons(self) -> None:
        """Register Add-on functions."""
        api_addons = APIAddons()
        api_addons.coresys = self.coresys

        self.webapp.add_routes(
            [
                web.get("/addons", api_addons.list),
                web.post("/addons/reload", api_addons.reload),
                web.get("/addons/{addon}/info", api_addons.info),
                web.post("/addons/{addon}/install", api_addons.install),
                web.post("/addons/{addon}/uninstall", api_addons.uninstall),
                web.post("/addons/{addon}/start", api_addons.start),
                web.post("/addons/{addon}/stop", api_addons.stop),
                web.post("/addons/{addon}/restart", api_addons.restart),
                web.post("/addons/{addon}/update", api_addons.update),
                web.post("/addons/{addon}/options", api_addons.options),
                web.post("/addons/{addon}/rebuild", api_addons.rebuild),
                web.get("/addons/{addon}/logs", api_addons.logs),
                web.get("/addons/{addon}/icon", api_addons.icon),
                web.get("/addons/{addon}/logo", api_addons.logo),
                web.get("/addons/{addon}/changelog", api_addons.changelog),
                web.get("/addons/{addon}/documentation", api_addons.documentation),
                web.post("/addons/{addon}/stdin", api_addons.stdin),
                web.post("/addons/{addon}/security", api_addons.security),
                web.get("/addons/{addon}/stats", api_addons.stats),
            ]
        )

    def _register_ingress(self) -> None:
        """Register Ingress functions."""
        api_ingress = APIIngress()
        api_ingress.coresys = self.coresys

        self.webapp.add_routes(
            [
                web.post("/ingress/session", api_ingress.create_session),
                web.get("/ingress/panels", api_ingress.panels),
                web.view("/ingress/{token}/{path:.*}", api_ingress.handler),
            ]
        )

    def _register_snapshots(self) -> None:
        """Register snapshots functions."""
        api_snapshots = APISnapshots()
        api_snapshots.coresys = self.coresys

        self.webapp.add_routes(
            [
                web.get("/snapshots", api_snapshots.list),
                web.post("/snapshots/reload", api_snapshots.reload),
                web.post("/snapshots/new/full", api_snapshots.snapshot_full),
                web.post("/snapshots/new/partial", api_snapshots.snapshot_partial),
                web.post("/snapshots/new/upload", api_snapshots.upload),
                web.get("/snapshots/{snapshot}/info", api_snapshots.info),
                web.post("/snapshots/{snapshot}/remove", api_snapshots.remove),
                web.post(
                    "/snapshots/{snapshot}/restore/full", api_snapshots.restore_full
                ),
                web.post(
                    "/snapshots/{snapshot}/restore/partial",
                    api_snapshots.restore_partial,
                ),
                web.get("/snapshots/{snapshot}/download", api_snapshots.download),
            ]
        )

    def _register_services(self) -> None:
        """Register services functions."""
        api_services = APIServices()
        api_services.coresys = self.coresys

        self.webapp.add_routes(
            [
                web.get("/services", api_services.list),
                web.get("/services/{service}", api_services.get_service),
                web.post("/services/{service}", api_services.set_service),
                web.delete("/services/{service}", api_services.del_service),
            ]
        )

    def _register_discovery(self) -> None:
        """Register discovery functions."""
        api_discovery = APIDiscovery()
        api_discovery.coresys = self.coresys

        self.webapp.add_routes(
            [
                web.get("/discovery", api_discovery.list),
                web.get("/discovery/{uuid}", api_discovery.get_discovery),
                web.delete("/discovery/{uuid}", api_discovery.del_discovery),
                web.post("/discovery", api_discovery.set_discovery),
            ]
        )

    def _register_dns(self) -> None:
        """Register DNS functions."""
        api_dns = APICoreDNS()
        api_dns.coresys = self.coresys

        self.webapp.add_routes(
            [
                web.get("/dns/info", api_dns.info),
                web.get("/dns/stats", api_dns.stats),
                web.get("/dns/logs", api_dns.logs),
                web.post("/dns/update", api_dns.update),
                web.post("/dns/options", api_dns.options),
                web.post("/dns/restart", api_dns.restart),
                web.post("/dns/reset", api_dns.reset),
            ]
        )

    def _register_panel(self) -> None:
        """Register panel for Home Assistant."""
        panel_dir = Path(__file__).parent.joinpath("panel")
        self.webapp.add_routes([web.static("/app", panel_dir)])

    async def start(self) -> None:
        """Run RESTful API webserver."""
        await self._runner.setup()
        self._site = web.TCPSite(
            self._runner, host="0.0.0.0", port=80, shutdown_timeout=5
        )

        try:
            await self._site.start()
        except OSError as err:
            _LOGGER.fatal("Failed to create HTTP server at 0.0.0.0:80 -> %s", err)
        else:
            _LOGGER.info("Start API on %s", self.sys_docker.network.supervisor)

    async def stop(self) -> None:
        """Stop RESTful API webserver."""
        if not self._site:
            return

        # Shutdown running API
        await self._site.stop()
        await self._runner.cleanup()

        _LOGGER.info("Stop API on %s", self.sys_docker.network.supervisor)
