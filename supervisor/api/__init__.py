"""Init file for Supervisor RESTful API."""

from dataclasses import dataclass
from functools import partial
import logging
from pathlib import Path
from typing import Any

from aiohttp import hdrs, web

from ..addons.addon import App
from ..const import SUPERVISOR_DOCKER_NAME, AppState, FeatureFlag
from ..coresys import CoreSys, CoreSysAttributes
from ..exceptions import APIAppNotInstalled, HostNotSupportedError
from ..utils.sentry import async_capture_exception
from .addons import APIApps
from .audio import APIAudio
from .auth import APIAuth
from .backups import APIBackups
from .cli import APICli
from .const import CONTENT_TYPE_TEXT
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
from .utils import api_process, api_process_raw

_LOGGER: logging.Logger = logging.getLogger(__name__)


MAX_CLIENT_SIZE: int = 1024**2 * 16
MAX_LINE_SIZE: int = 24570


@dataclass(slots=True, frozen=True)
class StaticResourceConfig:
    """Configuration for a static resource."""

    prefix: str
    path: Path


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
        # v2 sub-app: no middleware of its own — parent webapp's middleware
        # stack runs first for all requests including sub-app routes.
        self.v2_app: web.Application = web.Application()

        # service stuff
        self._runner: web.AppRunner = web.AppRunner(self.webapp, shutdown_timeout=5)
        self._site: web.TCPSite | None = None

        # share single host API handler for reuse in logging endpoints
        self._api_host: APIHost = APIHost()
        self._api_host.coresys = coresys

        # handler instances shared between v1 and v2 registrations
        self._api_apps: APIApps | None = None
        self._api_backups: APIBackups | None = None
        self._api_store: APIStore | None = None

    async def load(self) -> None:
        """Register REST API Calls."""
        static_resource_configs: list[StaticResourceConfig] = []

        self._register_apps()
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
        static_resource_configs.extend(self._register_panel())
        self._register_proxy()
        self._register_resolution()
        self._register_root()
        self._register_security()
        self._register_services()
        self._register_store()
        self._register_supervisor()

        # Register v2 routes before mounting the sub-app
        # (add_subapp freezes the sub-app's router)
        if self.sys_config.feature_flags.get(FeatureFlag.SUPERVISOR_V2_API, False):
            self._register_v2_apps()
            self._register_v2_backups()
            self._register_v2_store()
            self.webapp.add_subapp("/v2", self.v2_app)

        if static_resource_configs:

            def process_configs() -> list[web.StaticResource]:
                return [
                    web.StaticResource(config.prefix, config.path)
                    for config in static_resource_configs
                ]

            for resource in await self.sys_run_in_executor(process_configs):
                self.webapp.router.register_resource(resource)

        await self.start()

    def _register_advanced_logs(
        self,
        path: str,
        syslog_identifier: str,
        default_verbose: bool = False,
    ):
        """Register logs endpoint for a given path, returning logs for single syslog identifier."""

        self.webapp.add_routes(
            [
                web.get(
                    f"{path}/logs",
                    partial(
                        self._api_host.advanced_logs,
                        identifier=syslog_identifier,
                        default_verbose=default_verbose,
                    ),
                ),
                web.get(
                    f"{path}/logs/follow",
                    partial(
                        self._api_host.advanced_logs,
                        identifier=syslog_identifier,
                        follow=True,
                        default_verbose=default_verbose,
                    ),
                ),
                web.get(
                    f"{path}/logs/latest",
                    partial(
                        self._api_host.advanced_logs,
                        identifier=syslog_identifier,
                        latest=True,
                        no_colors=True,
                        default_verbose=default_verbose,
                    ),
                ),
                web.get(
                    f"{path}/logs/boots/{{bootid}}",
                    partial(
                        self._api_host.advanced_logs,
                        identifier=syslog_identifier,
                        default_verbose=default_verbose,
                    ),
                ),
                web.get(
                    f"{path}/logs/boots/{{bootid}}/follow",
                    partial(
                        self._api_host.advanced_logs,
                        identifier=syslog_identifier,
                        follow=True,
                        default_verbose=default_verbose,
                    ),
                ),
            ]
        )

    def _register_host(self) -> None:
        """Register hostcontrol functions."""
        api_host = self._api_host

        self.webapp.add_routes(
            [
                web.get("/host/info", api_host.info),
                web.get(
                    "/host/logs",
                    partial(api_host.advanced_logs, default_verbose=True),
                ),
                web.get(
                    "/host/logs/follow",
                    partial(api_host.advanced_logs, follow=True, default_verbose=True),
                ),
                web.get("/host/logs/identifiers", api_host.list_identifiers),
                web.get("/host/logs/identifiers/{identifier}", api_host.advanced_logs),
                web.get(
                    "/host/logs/identifiers/{identifier}/follow",
                    partial(api_host.advanced_logs, follow=True),
                ),
                web.get("/host/logs/boots", api_host.list_boots),
                web.get(
                    "/host/logs/boots/{bootid}",
                    partial(api_host.advanced_logs, default_verbose=True),
                ),
                web.get(
                    "/host/logs/boots/{bootid}/follow",
                    partial(api_host.advanced_logs, follow=True, default_verbose=True),
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
                web.get("/host/disks/default/usage", api_host.disk_usage),
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
                web.get("/os/config/swap", api_os.config_swap_info),
                web.post("/os/config/swap", api_os.config_swap_options),
                web.post("/os/config/sync", api_os.config_sync),
                web.post("/os/datadisk/move", api_os.migrate_data),
                web.get("/os/datadisk/list", api_os.list_data),
                web.post("/os/datadisk/wipe", api_os.wipe_data),
                web.post("/os/boot-slot", api_os.set_boot_slot),
            ]
        )

        # Boards endpoints
        self.webapp.add_routes(
            [
                web.get("/os/boards/green", api_os.boards_green_info),
                web.post("/os/boards/green", api_os.boards_green_options),
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
                web.get("/jobs/{uuid}", api_jobs.job_info),
                web.delete("/jobs/{uuid}", api_jobs.remove_job),
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
                web.post("/multicast/update", api_multicast.update),
                web.post("/multicast/restart", api_multicast.restart),
            ]
        )
        self._register_advanced_logs(
            "/multicast", "hassio_multicast", default_verbose=True
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
        self.webapp.add_routes([web.post("/reload_updates", api_root.reload_updates)])

        # Discouraged
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
                web.get("/auth/list", api_auth.list_users),
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
                web.post("/supervisor/update", api_supervisor.update),
                web.post("/supervisor/reload", api_supervisor.reload),
                web.post("/supervisor/restart", api_supervisor.restart),
                web.post("/supervisor/options", api_supervisor.options),
                web.post("/supervisor/repair", api_supervisor.repair),
            ]
        )

        async def get_supervisor_logs(*args, **kwargs):
            try:
                return await self._api_host.advanced_logs_handler(
                    *args, identifier=SUPERVISOR_DOCKER_NAME, **kwargs
                )
            except Exception as err:  # pylint: disable=broad-exception-caught
                # Supervisor logs are critical, so catch everything, log the exception
                # and try to return Docker container logs as the fallback
                _LOGGER.exception(
                    "Failed to get supervisor logs using advanced_logs API"
                )
                if not isinstance(err, HostNotSupportedError):
                    # No need to capture HostNotSupportedError to Sentry, the cause
                    # is known and reported to the user using the resolution center.
                    await async_capture_exception(err)
                kwargs.pop("follow", None)  # Follow is not supported for Docker logs
                kwargs.pop("latest", None)  # Latest is not supported for Docker logs
                kwargs.pop("no_colors", None)  # no_colors not supported for Docker logs
                return await api_supervisor.logs(*args, **kwargs)

        self.webapp.add_routes(
            [
                web.get("/supervisor/logs", get_supervisor_logs),
                web.get(
                    "/supervisor/logs/follow",
                    partial(get_supervisor_logs, follow=True),
                ),
                web.get(
                    "/supervisor/logs/latest",
                    partial(get_supervisor_logs, latest=True, no_colors=True),
                ),
                web.get("/supervisor/logs/boots/{bootid}", get_supervisor_logs),
                web.get(
                    "/supervisor/logs/boots/{bootid}/follow",
                    partial(get_supervisor_logs, follow=True),
                ),
            ]
        )

    def _register_homeassistant(self) -> None:
        """Register Home Assistant functions."""
        api_hass = APIHomeAssistant()
        api_hass.coresys = self.coresys

        self.webapp.add_routes(
            [
                web.get("/core/info", api_hass.info),
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

        self._register_advanced_logs("/core", "homeassistant")

        # Reroute from legacy
        self.webapp.add_routes(
            [
                web.get("/homeassistant/info", api_hass.info),
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

        self._register_advanced_logs("/homeassistant", "homeassistant")

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
                web.delete("/core/api/{path:.+}", api_proxy.api),
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

    def _register_apps(self) -> None:
        """Register App functions."""
        api_apps = APIApps()
        api_apps.coresys = self.coresys
        self._api_apps = api_apps

        self.webapp.add_routes(
            [
                web.get("/addons", api_apps.list_apps_v1),
                web.post("/addons/{app}/uninstall", api_apps.uninstall),
                web.post("/addons/{app}/start", api_apps.start),
                web.post("/addons/{app}/stop", api_apps.stop),
                web.post("/addons/{app}/restart", api_apps.restart),
                web.post("/addons/{app}/options", api_apps.options),
                web.post("/addons/{app}/sys_options", api_apps.sys_options),
                web.post("/addons/{app}/options/validate", api_apps.options_validate),
                web.get("/addons/{app}/options/config", api_apps.options_config),
                web.post("/addons/{app}/rebuild", api_apps.rebuild),
                web.post("/addons/{app}/stdin", api_apps.stdin),
                web.post("/addons/{app}/security", api_apps.security),
                web.get("/addons/{app}/stats", api_apps.stats),
            ]
        )

        @api_process_raw(CONTENT_TYPE_TEXT, error_type=CONTENT_TYPE_TEXT)
        async def get_app_logs(request, *args, **kwargs):
            app = api_apps.get_app_for_request(request)
            kwargs["identifier"] = f"addon_{app.slug}"
            return await self._api_host.advanced_logs(request, *args, **kwargs)

        self.webapp.add_routes(
            [
                web.get("/addons/{app}/logs", get_app_logs),
                web.get(
                    "/addons/{app}/logs/follow",
                    partial(get_app_logs, follow=True),
                ),
                web.get(
                    "/addons/{app}/logs/latest",
                    partial(get_app_logs, latest=True, no_colors=True),
                ),
                web.get("/addons/{app}/logs/boots/{bootid}", get_app_logs),
                web.get(
                    "/addons/{app}/logs/boots/{bootid}/follow",
                    partial(get_app_logs, follow=True),
                ),
            ]
        )

        # Legacy routing to support requests for not installed apps
        api_store = APIStore()
        api_store.coresys = self.coresys

        @api_process
        async def apps_app_info(request: web.Request) -> dict[str, Any]:
            """Route to store if info requested for not installed app."""
            try:
                app: App = api_apps.get_app_for_request(request)
                return await api_apps.info_data(app)
            except APIAppNotInstalled:
                # Route to store/{app}/info but add missing fields
                return dict(
                    await api_store.apps_app_info_wrapped(request),
                    state=AppState.UNKNOWN,
                    options=self.sys_apps.store[request.match_info["app"]].options,
                )

        self.webapp.add_routes([web.get("/addons/{app}/info", apps_app_info)])

    def _register_v2_apps(self) -> None:
        """Register v2 app routes on the v2 sub-app (accessible as /v2/apps/...)."""
        assert self._api_apps is not None
        api_apps = self._api_apps

        @api_process_raw(CONTENT_TYPE_TEXT, error_type=CONTENT_TYPE_TEXT)
        async def get_app_logs_v2(request, *args, **kwargs):
            app = api_apps.get_app_for_request(request)
            kwargs["identifier"] = f"addon_{app.slug}"
            return await self._api_host.advanced_logs(request, *args, **kwargs)

        self.v2_app.add_routes(
            [
                web.get("/apps", api_apps.list_apps),
                web.post("/apps/{app}/uninstall", api_apps.uninstall),
                web.post("/apps/{app}/start", api_apps.start),
                web.post("/apps/{app}/stop", api_apps.stop),
                web.post("/apps/{app}/restart", api_apps.restart),
                web.post("/apps/{app}/options", api_apps.options),
                web.post("/apps/{app}/sys_options", api_apps.sys_options),
                web.post("/apps/{app}/options/validate", api_apps.options_validate),
                web.get("/apps/{app}/options/config", api_apps.options_config),
                web.post("/apps/{app}/rebuild", api_apps.rebuild),
                web.post("/apps/{app}/stdin", api_apps.stdin),
                web.post("/apps/{app}/security", api_apps.security),
                web.get("/apps/{app}/stats", api_apps.stats),
                web.get("/apps/{app}/info", api_apps.info),
                web.get("/apps/{app}/logs", get_app_logs_v2),
                web.get(
                    "/apps/{app}/logs/follow",
                    partial(get_app_logs_v2, follow=True),
                ),
                web.get(
                    "/apps/{app}/logs/latest",
                    partial(get_app_logs_v2, latest=True, no_colors=True),
                ),
                web.get("/apps/{app}/logs/boots/{bootid}", get_app_logs_v2),
                web.get(
                    "/apps/{app}/logs/boots/{bootid}/follow",
                    partial(get_app_logs_v2, follow=True),
                ),
            ]
        )

    def _register_ingress(self) -> None:
        """Register Ingress functions."""
        api_ingress = APIIngress()
        api_ingress.coresys = self.coresys

        self.webapp.add_routes(
            [
                web.post("/ingress/session", api_ingress.create_session),
                web.post("/ingress/validate_session", api_ingress.validate_session),
                web.get("/ingress/panels", api_ingress.panels),
                web.route(
                    hdrs.METH_ANY, "/ingress/{token}/{path:.*}", api_ingress.handler
                ),
            ]
        )

    def _register_backups(self) -> None:
        """Register backups functions."""
        api_backups = APIBackups()
        api_backups.coresys = self.coresys
        self._api_backups = api_backups

        self.webapp.add_routes(
            [
                web.get("/backups", api_backups.list_backups_v1),
                web.get("/backups/info", api_backups.info_v1),
                web.post("/backups/options", api_backups.options),
                web.post("/backups/reload", api_backups.reload),
                web.post("/backups/freeze", api_backups.freeze),
                web.post("/backups/thaw", api_backups.thaw),
                web.post("/backups/new/full", api_backups.backup_full),
                web.post("/backups/new/partial", api_backups.backup_partial_v1),
                web.post("/backups/new/upload", api_backups.upload),
                web.get("/backups/{slug}/info", api_backups.backup_info_v1),
                web.delete("/backups/{slug}", api_backups.remove),
                web.post("/backups/{slug}/restore/full", api_backups.restore_full),
                web.post(
                    "/backups/{slug}/restore/partial",
                    api_backups.restore_partial_v1,
                ),
                web.get("/backups/{slug}/download", api_backups.download),
            ]
        )

    def _register_v2_backups(self) -> None:
        """Register v2 backup routes on the v2 sub-app (accessible as /v2/backups/...)."""
        assert self._api_backups is not None
        api_backups = self._api_backups

        self.v2_app.add_routes(
            [
                web.get("/backups", api_backups.list_backups),
                web.get("/backups/info", api_backups.info),
                web.post("/backups/options", api_backups.options),
                web.post("/backups/reload", api_backups.reload),
                web.post("/backups/freeze", api_backups.freeze),
                web.post("/backups/thaw", api_backups.thaw),
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
                web.get("/services", api_services.list_services),
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
                web.get("/discovery", api_discovery.list_discovery),
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
                web.post("/dns/update", api_dns.update),
                web.post("/dns/options", api_dns.options),
                web.post("/dns/restart", api_dns.restart),
                web.post("/dns/reset", api_dns.reset),
            ]
        )

        self._register_advanced_logs("/dns", "hassio_dns", default_verbose=True)

    def _register_audio(self) -> None:
        """Register Audio functions."""
        api_audio = APIAudio()
        api_audio.coresys = self.coresys

        self.webapp.add_routes(
            [
                web.get("/audio/info", api_audio.info),
                web.get("/audio/stats", api_audio.stats),
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

        self._register_advanced_logs("/audio", "hassio_audio", default_verbose=True)

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
        self._api_store = api_store

        self.webapp.add_routes(
            [
                web.get("/store", api_store.store_info_v1),
                web.get("/store/addons", api_store.apps_list_v1),
                web.get("/store/addons/{app}", api_store.apps_app_info),
                web.get("/store/addons/{app}/icon", api_store.apps_app_icon),
                web.get("/store/addons/{app}/logo", api_store.apps_app_logo),
                web.get("/store/addons/{app}/changelog", api_store.apps_app_changelog),
                web.get(
                    "/store/addons/{app}/documentation",
                    api_store.apps_app_documentation,
                ),
                web.get(
                    "/store/addons/{app}/availability",
                    api_store.apps_app_availability,
                ),
                web.post("/store/addons/{app}/install", api_store.apps_app_install),
                web.post(
                    "/store/addons/{app}/install/{version}",
                    api_store.apps_app_install,
                ),
                web.post("/store/addons/{app}/update", api_store.apps_app_update),
                web.post(
                    "/store/addons/{app}/update/{version}",
                    api_store.apps_app_update,
                ),
                # Must be below others since it has a wildcard in resource path
                web.get("/store/addons/{app}/{version}", api_store.apps_app_info),
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
                web.post(
                    "/store/repositories/{repository}/repair",
                    api_store.repositories_repository_repair,
                ),
            ]
        )

        # Reroute from legacy
        self.webapp.add_routes(
            [
                web.post("/addons/reload", api_store.reload),
                web.post("/addons/{app}/install", api_store.apps_app_install),
                web.post("/addons/{app}/update", api_store.apps_app_update),
                web.get("/addons/{app}/icon", api_store.apps_app_icon),
                web.get("/addons/{app}/logo", api_store.apps_app_logo),
                web.get("/addons/{app}/changelog", api_store.apps_app_changelog),
                web.get(
                    "/addons/{app}/documentation",
                    api_store.apps_app_documentation,
                ),
            ]
        )

    def _register_v2_store(self) -> None:
        """Register v2 store routes on the v2 sub-app (accessible as /v2/store/...)."""
        assert self._api_store is not None
        api_store = self._api_store

        self.v2_app.add_routes(
            [
                web.get("/store", api_store.store_info),
                web.get("/store/apps", api_store.apps_list),
                web.get("/store/apps/{app}", api_store.apps_app_info),
                web.get("/store/apps/{app}/icon", api_store.apps_app_icon),
                web.get("/store/apps/{app}/logo", api_store.apps_app_logo),
                web.get("/store/apps/{app}/changelog", api_store.apps_app_changelog),
                web.get(
                    "/store/apps/{app}/documentation",
                    api_store.apps_app_documentation,
                ),
                web.get(
                    "/store/apps/{app}/availability",
                    api_store.apps_app_availability,
                ),
                web.post("/store/apps/{app}/install", api_store.apps_app_install),
                web.post(
                    "/store/apps/{app}/install/{version}",
                    api_store.apps_app_install,
                ),
                web.post("/store/apps/{app}/update", api_store.apps_app_update),
                web.post(
                    "/store/apps/{app}/update/{version}",
                    api_store.apps_app_update,
                ),
                # Must be below others since it has a wildcard in resource path
                web.get("/store/apps/{app}/{version}", api_store.apps_app_info),
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
                web.post(
                    "/store/repositories/{repository}/repair",
                    api_store.repositories_repository_repair,
                ),
            ]
        )

    def _register_panel(self) -> list[StaticResourceConfig]:
        """Register panel for Home Assistant."""
        return [StaticResourceConfig("/app", Path(__file__).parent.joinpath("panel"))]

    def _register_docker(self) -> None:
        """Register docker configuration functions."""
        api_docker = APIDocker()
        api_docker.coresys = self.coresys

        self.webapp.add_routes(
            [
                web.get("/docker/info", api_docker.info),
                web.post(
                    "/docker/migrate-storage-driver",
                    api_docker.migrate_docker_storage_driver,
                ),
                web.post("/docker/options", api_docker.options),
                web.get("/docker/registries", api_docker.registries),
                web.post("/docker/registries", api_docker.create_registry),
                web.delete("/docker/registries/{hostname}", api_docker.remove_registry),
            ]
        )

    async def start(self) -> None:
        """Run RESTful API webserver."""
        await self._runner.setup()
        self._site = web.TCPSite(self._runner, host="0.0.0.0", port=80)

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
