"""Init file for Supervisor RESTful API."""
from functools import partial
import logging
from pathlib import Path
from typing import Any

from aiohttp import web

from ..const import AddonState
from ..coresys import CoreSys, CoreSysAttributes
from ..exceptions import APIAddonNotInstalled
from .addons import APIAddons
from .audio import APIAudio
from .auth import APIAuth
from .backups import APIBackups
from .cli import APICli
from .discovery import APIDiscovery
from .dns import APICoreDNS
from .docker import APIDocker
from .hardware import APIHardware
from .homeassistant import APIHomeAssistant
from .host import APIHost
from .ingress import APIIngress
from .jobs import APIJobs
from .middleware.security import SecurityMiddleware
from .mounts import APIMounts
from .multicast import APIMulticast
from .network import APINetwork
from .observer import APIObserver
from .os import APIOS
from .proxy import APIProxy
from .resolution import APIResoulution
from .root import APIRoot
from .security import APISecurity
from .services import APIServices
from .store import APIStore
from .supervisor import APISupervisor
from .utils import api_process

_LOGGER: logging.Logger = logging.getLogger(__name__)


MAX_CLIENT_SIZE: int = 1024**2 * 16
MAX_LINE_SIZE: int = 24570


class RestAPI(CoreSysAttributes):
    """Handle RESTful API for Supervisor."""

    def __init__(self, coresys: CoreSys):
        """Initialize Docker base wrapper."""
        self.coresys: CoreSys = coresys
        self.security: SecurityMiddleware = SecurityMiddleware(coresys)
        self.webapp: web.Application = web.Application(
            client_max_size=MAX_CLIENT_SIZE,
            middlewares=[
                self.security.block_bad_requests,
                self.security.system_validation,
                self.security.token_validation,
                self.security.core_proxy,
            ],
            handler_args={
                "max_line_size": MAX_LINE_SIZE,
                "max_field_size": MAX_LINE_SIZE,
            },
        )

        # service stuff
        self._runner: web.AppRunner = web.AppRunner(self.webapp)
        self._site: web.TCPSite | None = None

    async def load(self) -> None:
        """Register REST API Calls."""
        self._register_addons()
        self._register_audio()
        self._register_auth()
        self._register_backups()
        self._register_cli()
        self._register_discovery()
        self._register_dns()
        self._register_docker()
        self._register_hardware()
        self._register_homeassistant()
        self._register_host()
        self._register_jobs()
        self._register_ingress()
        self._register_mounts()
        self._register_multicast()
        self._register_network()
        self._register_observer()
        self._register_os()
        self._register_panel()
        self._register_proxy()
        self._register_resolution()
        self._register_root()
        self._register_security()
        self._register_services()
        self._register_store()
        self._register_supervisor()

        await self.start()

    def _register_host(self) -> None:
        """Register hostcontrol functions."""
        api_host = APIHost()
        api_host.coresys = self.coresys

        self.webapp.add_routes(
            [
                web.get("/host/info", api_host.info),
                web.get("/host/logs", api_host.advanced_logs),
                web.get(
                    "/host/logs/follow",
                    partial(api_host.advanced_logs, follow=True),
                ),
                web.get("/host/logs/identifiers", api_host.list_identifiers),
                web.get("/host/logs/identifiers/{identifier}", api_host.advanced_logs),
                web.get(
                    "/host/logs/identifiers/{identifier}/follow",
                    partial(api_host.advanced_logs, follow=True),
                ),
                web.get("/host/logs/boots", api_host.list_boots),
                web.get("/host/logs/boots/{bootid}", api_host.advanced_logs),
                web.get(
                    "/host/logs/boots/{bootid}/follow",
                    partial(api_host.advanced_logs, follow=True),
                ),
                web.get(
                    "/host/logs/boots/{bootid}/identifiers/{identifier}",
                    api_host.advanced_logs,
                ),
                web.get(
                    "/host/logs/boots/{bootid}/identifiers/{identifier}/follow",
                    partial(api_host.advanced_logs, follow=True),
                ),
                web.post("/host/reboot", api_host.reboot),
                web.post("/host/shutdown", api_host.shutdown),
                web.post("/host/reload", api_host.reload),
                web.post("/host/options", api_host.options),
                web.get("/host/services", api_host.services),
            ]
        )

    def _register_network(self) -> None:
        """Register network functions."""
        api_network = APINetwork()
        api_network.coresys = self.coresys

        self.webapp.add_routes(
            [
                web.get("/network/info", api_network.info),
                web.post("/network/reload", api_network.reload),
                web.get(
                    "/network/interface/{interface}/info", api_network.interface_info
                ),
                web.post(
                    "/network/interface/{interface}/update",
                    api_network.interface_update,
                ),
                web.get(
                    "/network/interface/{interface}/accesspoints",
                    api_network.scan_accesspoints,
                ),
                web.post(
                    "/network/interface/{interface}/vlan/{vlan}",
                    api_network.create_vlan,
                ),
            ]
        )

    def _register_os(self) -> None:
        """Register OS functions."""
        api_os = APIOS()
        api_os.coresys = self.coresys

        self.webapp.add_routes(
            [
                web.get("/os/info", api_os.info),
                web.post("/os/update", api_os.update),
                web.post("/os/config/sync", api_os.config_sync),
                web.post("/os/datadisk/move", api_os.migrate_data),
                web.get("/os/datadisk/list", api_os.list_data),
            ]
        )

        # Boards endpoints
        self.webapp.add_routes(
            [
                web.get("/os/boards/yellow", api_os.boards_yellow_info),
                web.post("/os/boards/yellow", api_os.boards_yellow_options),
                web.get("/os/boards/{board}", api_os.boards_other_info),
            ]
        )

    def _register_security(self) -> None:
        """Register Security functions."""
        api_security = APISecurity()
        api_security.coresys = self.coresys

        self.webapp.add_routes(
            [
                web.get("/security/info", api_security.info),
                web.post("/security/options", api_security.options),
                web.post("/security/integrity", api_security.integrity_check),
            ]
        )

    def _register_jobs(self) -> None:
        """Register Jobs functions."""
        api_jobs = APIJobs()
        api_jobs.coresys = self.coresys

        self.webapp.add_routes(
            [
                web.get("/jobs/info", api_jobs.info),
                web.post("/jobs/options", api_jobs.options),
                web.post("/jobs/reset", api_jobs.reset),
            ]
        )

    def _register_cli(self) -> None:
        """Register HA cli functions."""
        api_cli = APICli()
        api_cli.coresys = self.coresys

        self.webapp.add_routes(
            [
                web.get("/cli/info", api_cli.info),
                web.get("/cli/stats", api_cli.stats),
                web.post("/cli/update", api_cli.update),
            ]
        )

    def _register_observer(self) -> None:
        """Register Observer functions."""
        api_observer = APIObserver()
        api_observer.coresys = self.coresys

        self.webapp.add_routes(
            [
                web.get("/observer/info", api_observer.info),
                web.get("/observer/stats", api_observer.stats),
                web.post("/observer/update", api_observer.update),
            ]
        )

    def _register_multicast(self) -> None:
        """Register Multicast functions."""
        api_multicast = APIMulticast()
        api_multicast.coresys = self.coresys

        self.webapp.add_routes(
            [
                web.get("/multicast/info", api_multicast.info),
                web.get("/multicast/stats", api_multicast.stats),
                web.get("/multicast/logs", api_multicast.logs),
                web.post("/multicast/update", api_multicast.update),
                web.post("/multicast/restart", api_multicast.restart),
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
            ]
        )

    def _register_root(self) -> None:
        """Register root functions."""
        api_root = APIRoot()
        api_root.coresys = self.coresys

        self.webapp.add_routes([web.get("/info", api_root.info)])
        self.webapp.add_routes([web.post("/refresh_updates", api_root.refresh_updates)])
        self.webapp.add_routes(
            [web.get("/available_updates", api_root.available_updates)]
        )

        # Remove: 2023
        self.webapp.add_routes(
            [web.get("/supervisor/available_updates", api_root.available_updates)]
        )

    def _register_resolution(self) -> None:
        """Register info functions."""
        api_resolution = APIResoulution()
        api_resolution.coresys = self.coresys

        self.webapp.add_routes(
            [
                web.get("/resolution/info", api_resolution.info),
                web.post(
                    "/resolution/check/{check}/options", api_resolution.options_check
                ),
                web.post("/resolution/check/{check}/run", api_resolution.run_check),
                web.post(
                    "/resolution/suggestion/{suggestion}",
                    api_resolution.apply_suggestion,
                ),
                web.delete(
                    "/resolution/suggestion/{suggestion}",
                    api_resolution.dismiss_suggestion,
                ),
                web.delete(
                    "/resolution/issue/{issue}",
                    api_resolution.dismiss_issue,
                ),
                web.get(
                    "/resolution/issue/{issue}/suggestions",
                    api_resolution.suggestions_for_issue,
                ),
                web.post("/resolution/healthcheck", api_resolution.healthcheck),
            ]
        )

    def _register_auth(self) -> None:
        """Register auth functions."""
        api_auth = APIAuth()
        api_auth.coresys = self.coresys

        self.webapp.add_routes(
            [
                web.get("/auth", api_auth.auth),
                web.post("/auth", api_auth.auth),
                web.post("/auth/reset", api_auth.reset),
                web.delete("/auth/cache", api_auth.cache),
            ]
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
                web.post("/supervisor/restart", api_supervisor.restart),
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
            ]
        )

        # Reroute from legacy
        self.webapp.add_routes(
            [
                web.get("/homeassistant/info", api_hass.info),
                web.get("/homeassistant/logs", api_hass.logs),
                web.get("/homeassistant/stats", api_hass.stats),
                web.post("/homeassistant/options", api_hass.options),
                web.post("/homeassistant/restart", api_hass.restart),
                web.post("/homeassistant/stop", api_hass.stop),
                web.post("/homeassistant/start", api_hass.start),
                web.post("/homeassistant/update", api_hass.update),
                web.post("/homeassistant/rebuild", api_hass.rebuild),
                web.post("/homeassistant/check", api_hass.check),
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
            ]
        )

        # Reroute from legacy
        self.webapp.add_routes(
            [
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
                web.post("/addons/{addon}/uninstall", api_addons.uninstall),
                web.post("/addons/{addon}/start", api_addons.start),
                web.post("/addons/{addon}/stop", api_addons.stop),
                web.post("/addons/{addon}/restart", api_addons.restart),
                web.post("/addons/{addon}/options", api_addons.options),
                web.post(
                    "/addons/{addon}/options/validate", api_addons.options_validate
                ),
                web.get("/addons/{addon}/options/config", api_addons.options_config),
                web.post("/addons/{addon}/rebuild", api_addons.rebuild),
                web.get("/addons/{addon}/logs", api_addons.logs),
                web.post("/addons/{addon}/stdin", api_addons.stdin),
                web.post("/addons/{addon}/security", api_addons.security),
                web.get("/addons/{addon}/stats", api_addons.stats),
            ]
        )

        # Legacy routing to support requests for not installed addons
        api_store = APIStore()
        api_store.coresys = self.coresys

        @api_process
        async def addons_addon_info(request: web.Request) -> dict[str, Any]:
            """Route to store if info requested for not installed addon."""
            try:
                return await api_addons.info(request)
            except APIAddonNotInstalled:
                # Route to store/{addon}/info but add missing fields
                return dict(
                    await api_store.addons_addon_info_wrapped(request),
                    state=AddonState.UNKNOWN,
                    options=self.sys_addons.store[request.match_info["addon"]].options,
                )

        self.webapp.add_routes([web.get("/addons/{addon}/info", addons_addon_info)])

    def _register_ingress(self) -> None:
        """Register Ingress functions."""
        api_ingress = APIIngress()
        api_ingress.coresys = self.coresys

        self.webapp.add_routes(
            [
                web.post("/ingress/session", api_ingress.create_session),
                web.post("/ingress/validate_session", api_ingress.validate_session),
                web.get("/ingress/panels", api_ingress.panels),
                web.view("/ingress/{token}/{path:.*}", api_ingress.handler),
            ]
        )

    def _register_backups(self) -> None:
        """Register backups functions."""
        api_backups = APIBackups()
        api_backups.coresys = self.coresys

        self.webapp.add_routes(
            [
                web.get("/backups", api_backups.list),
                web.get("/backups/info", api_backups.info),
                web.post("/backups/options", api_backups.options),
                web.post("/backups/reload", api_backups.reload),
                web.post("/backups/new/full", api_backups.backup_full),
                web.post("/backups/new/partial", api_backups.backup_partial),
                web.post("/backups/new/upload", api_backups.upload),
                web.get("/backups/{slug}/info", api_backups.backup_info),
                web.delete("/backups/{slug}", api_backups.remove),
                web.post("/backups/{slug}/restore/full", api_backups.restore_full),
                web.post(
                    "/backups/{slug}/restore/partial",
                    api_backups.restore_partial,
                ),
                web.get("/backups/{slug}/download", api_backups.download),
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

    def _register_audio(self) -> None:
        """Register Audio functions."""
        api_audio = APIAudio()
        api_audio.coresys = self.coresys
        api_host = APIHost()
        api_host.coresys = self.coresys

        self.webapp.add_routes(
            [
                web.get("/audio/info", api_audio.info),
                web.get("/audio/stats", api_audio.stats),
                web.get("/audio/logs", api_audio.logs),
                web.post("/audio/update", api_audio.update),
                web.post("/audio/restart", api_audio.restart),
                web.post("/audio/reload", api_audio.reload),
                web.post("/audio/profile", api_audio.set_profile),
                web.post("/audio/volume/{source}/application", api_audio.set_volume),
                web.post("/audio/volume/{source}", api_audio.set_volume),
                web.post("/audio/mute/{source}/application", api_audio.set_mute),
                web.post("/audio/mute/{source}", api_audio.set_mute),
                web.post("/audio/default/{source}", api_audio.set_default),
            ]
        )

    def _register_mounts(self) -> None:
        """Register mounts endpoints."""
        api_mounts = APIMounts()
        api_mounts.coresys = self.coresys

        self.webapp.add_routes(
            [
                web.get("/mounts", api_mounts.info),
                web.post("/mounts/options", api_mounts.options),
                web.post("/mounts", api_mounts.create_mount),
                web.put("/mounts/{mount}", api_mounts.update_mount),
                web.delete("/mounts/{mount}", api_mounts.delete_mount),
                web.post("/mounts/{mount}/reload", api_mounts.reload_mount),
            ]
        )

    def _register_store(self) -> None:
        """Register store endpoints."""
        api_store = APIStore()
        api_store.coresys = self.coresys

        self.webapp.add_routes(
            [
                web.get("/store", api_store.store_info),
                web.get("/store/addons", api_store.addons_list),
                web.get("/store/addons/{addon}", api_store.addons_addon_info),
                web.get("/store/addons/{addon}/{version}", api_store.addons_addon_info),
                web.get("/store/addons/{addon}/icon", api_store.addons_addon_icon),
                web.get("/store/addons/{addon}/logo", api_store.addons_addon_logo),
                web.get(
                    "/store/addons/{addon}/changelog", api_store.addons_addon_changelog
                ),
                web.get(
                    "/store/addons/{addon}/documentation",
                    api_store.addons_addon_documentation,
                ),
                web.post(
                    "/store/addons/{addon}/install", api_store.addons_addon_install
                ),
                web.post(
                    "/store/addons/{addon}/install/{version}",
                    api_store.addons_addon_install,
                ),
                web.post("/store/addons/{addon}/update", api_store.addons_addon_update),
                web.post(
                    "/store/addons/{addon}/update/{version}",
                    api_store.addons_addon_update,
                ),
                web.post("/store/reload", api_store.reload),
                web.get("/store/repositories", api_store.repositories_list),
                web.get(
                    "/store/repositories/{repository}",
                    api_store.repositories_repository_info,
                ),
                web.post("/store/repositories", api_store.add_repository),
                web.delete(
                    "/store/repositories/{repository}", api_store.remove_repository
                ),
            ]
        )

        # Reroute from legacy
        self.webapp.add_routes(
            [
                web.post("/addons/reload", api_store.reload),
                web.post("/addons/{addon}/install", api_store.addons_addon_install),
                web.post("/addons/{addon}/update", api_store.addons_addon_update),
                web.get("/addons/{addon}/icon", api_store.addons_addon_icon),
                web.get("/addons/{addon}/logo", api_store.addons_addon_logo),
                web.get("/addons/{addon}/changelog", api_store.addons_addon_changelog),
                web.get(
                    "/addons/{addon}/documentation",
                    api_store.addons_addon_documentation,
                ),
            ]
        )

    def _register_panel(self) -> None:
        """Register panel for Home Assistant."""
        panel_dir = Path(__file__).parent.joinpath("panel")
        self.webapp.add_routes([web.static("/app", panel_dir)])

    def _register_docker(self) -> None:
        """Register docker configuration functions."""
        api_docker = APIDocker()
        api_docker.coresys = self.coresys

        self.webapp.add_routes(
            [
                web.get("/docker/info", api_docker.info),
                web.get("/docker/registries", api_docker.registries),
                web.post("/docker/registries", api_docker.create_registry),
                web.delete("/docker/registries/{hostname}", api_docker.remove_registry),
            ]
        )

    async def start(self) -> None:
        """Run RESTful API webserver."""
        await self._runner.setup()
        self._site = web.TCPSite(
            self._runner, host="0.0.0.0", port=80, shutdown_timeout=5
        )

        try:
            await self._site.start()
        except OSError as err:
            _LOGGER.critical("Failed to create HTTP server at 0.0.0.0:80 -> %s", err)
        else:
            _LOGGER.info("Starting API on %s", self.sys_docker.network.supervisor)

    async def stop(self) -> None:
        """Stop RESTful API webserver."""
        if not self._site:
            return

        # Shutdown running API
        await self._site.stop()
        await self._runner.cleanup()

        _LOGGER.info("Stopping API on %s", self.sys_docker.network.supervisor)
