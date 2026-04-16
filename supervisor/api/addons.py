"""Init file for Supervisor Home Assistant RESTful API."""

import asyncio
from collections.abc import Awaitable
import logging
from typing import Any, TypedDict

from aiohttp import web
import voluptuous as vol
from voluptuous.humanize import humanize_error

from ..addons.addon import App
from ..addons.utils import rating_security
from ..const import (
    ATTR_ADDONS,
    ATTR_ADVANCED,
    ATTR_APPARMOR,
    ATTR_APPS,
    ATTR_ARCH,
    ATTR_AUDIO,
    ATTR_AUDIO_INPUT,
    ATTR_AUDIO_OUTPUT,
    ATTR_AUTH_API,
    ATTR_AUTO_UPDATE,
    ATTR_AVAILABLE,
    ATTR_BLK_READ,
    ATTR_BLK_WRITE,
    ATTR_BOOT,
    ATTR_BUILD,
    ATTR_CHANGELOG,
    ATTR_CPU_PERCENT,
    ATTR_DESCRIPTON,
    ATTR_DETACHED,
    ATTR_DEVICES,
    ATTR_DEVICETREE,
    ATTR_DISCOVERY,
    ATTR_DNS,
    ATTR_DOCKER_API,
    ATTR_DOCUMENTATION,
    ATTR_FORCE,
    ATTR_FULL_ACCESS,
    ATTR_GPIO,
    ATTR_HASSIO_API,
    ATTR_HASSIO_ROLE,
    ATTR_HOMEASSISTANT,
    ATTR_HOMEASSISTANT_API,
    ATTR_HOST_DBUS,
    ATTR_HOST_IPC,
    ATTR_HOST_NETWORK,
    ATTR_HOST_PID,
    ATTR_HOST_UTS,
    ATTR_HOSTNAME,
    ATTR_ICON,
    ATTR_INGRESS,
    ATTR_INGRESS_ENTRY,
    ATTR_INGRESS_PANEL,
    ATTR_INGRESS_PORT,
    ATTR_INGRESS_URL,
    ATTR_IP_ADDRESS,
    ATTR_KERNEL_MODULES,
    ATTR_LOGO,
    ATTR_LONG_DESCRIPTION,
    ATTR_MACHINE,
    ATTR_MEMORY_LIMIT,
    ATTR_MEMORY_PERCENT,
    ATTR_MEMORY_USAGE,
    ATTR_NAME,
    ATTR_NETWORK,
    ATTR_NETWORK_DESCRIPTION,
    ATTR_NETWORK_RX,
    ATTR_NETWORK_TX,
    ATTR_OPTIONS,
    ATTR_PRIVILEGED,
    ATTR_PROTECTED,
    ATTR_RATING,
    ATTR_REPOSITORY,
    ATTR_SCHEMA,
    ATTR_SERVICES,
    ATTR_SLUG,
    ATTR_STAGE,
    ATTR_STARTUP,
    ATTR_STATE,
    ATTR_STDIN,
    ATTR_SYSTEM_MANAGED,
    ATTR_SYSTEM_MANAGED_CONFIG_ENTRY,
    ATTR_TRANSLATIONS,
    ATTR_UART,
    ATTR_UDEV,
    ATTR_UPDATE_AVAILABLE,
    ATTR_URL,
    ATTR_USB,
    ATTR_VERSION,
    ATTR_VERSION_LATEST,
    ATTR_VIDEO,
    ATTR_WATCHDOG,
    ATTR_WEBUI,
    REQUEST_FROM,
    AppBoot,
    AppBootConfig,
)
from ..coresys import CoreSysAttributes
from ..docker.stats import DockerStats
from ..exceptions import (
    APIAppNotInstalled,
    APIError,
    APIForbidden,
    APINotFound,
    AppBootConfigCannotChangeError,
    AppConfigurationInvalidError,
    AppNotSupportedWriteStdinError,
    PwnedError,
    PwnedSecret,
)
from ..validate import docker_ports
from .const import ATTR_BOOT_CONFIG, ATTR_REMOVE_CONFIG, ATTR_SIGNED
from .utils import api_process, api_validate, json_loads

_LOGGER: logging.Logger = logging.getLogger(__name__)

SCHEMA_VERSION = vol.Schema({vol.Optional(ATTR_VERSION): str})

# pylint: disable=no-value-for-parameter
SCHEMA_OPTIONS = vol.Schema(
    {
        vol.Optional(ATTR_BOOT): vol.Coerce(AppBoot),
        vol.Optional(ATTR_NETWORK): vol.Maybe(docker_ports),
        vol.Optional(ATTR_AUTO_UPDATE): vol.Boolean(),
        vol.Optional(ATTR_AUDIO_OUTPUT): vol.Maybe(str),
        vol.Optional(ATTR_AUDIO_INPUT): vol.Maybe(str),
        vol.Optional(ATTR_INGRESS_PANEL): vol.Boolean(),
        vol.Optional(ATTR_WATCHDOG): vol.Boolean(),
        vol.Optional(ATTR_OPTIONS): vol.Maybe(dict),
    }
)

SCHEMA_SYS_OPTIONS = vol.Schema(
    {
        vol.Optional(ATTR_SYSTEM_MANAGED): vol.Boolean(),
        vol.Optional(ATTR_SYSTEM_MANAGED_CONFIG_ENTRY): vol.Maybe(str),
    }
)

SCHEMA_SECURITY = vol.Schema({vol.Optional(ATTR_PROTECTED): vol.Boolean()})

SCHEMA_UNINSTALL = vol.Schema(
    {vol.Optional(ATTR_REMOVE_CONFIG, default=False): vol.Boolean()}
)

SCHEMA_REBUILD = vol.Schema({vol.Optional(ATTR_FORCE, default=False): vol.Boolean()})
# pylint: enable=no-value-for-parameter


class OptionsValidateResponse(TypedDict):
    """Response object for options validate."""

    message: str
    valid: bool
    pwned: bool | None


class APIApps(CoreSysAttributes):
    """Handle RESTful API for app functions."""

    def get_app_for_request(self, request: web.Request) -> App:
        """Return app, throw an exception if it doesn't exist."""
        app_slug: str = request.match_info["app"]

        # Lookup itself
        if app_slug == "self":
            app = request.get(REQUEST_FROM)
            if not isinstance(app, App):
                raise APIError("Self is not an App")
            return app

        app = self.sys_apps.get(app_slug)
        if not app:
            raise APINotFound(f"App {app_slug} does not exist")
        if not isinstance(app, App) or not app.is_installed:
            raise APIAppNotInstalled("App is not installed")

        return app

    def _list_apps_data(self) -> list[dict[str, Any]]:
        """Build the list of installed app data dicts."""
        return [
            {
                ATTR_NAME: app.name,
                ATTR_SLUG: app.slug,
                ATTR_DESCRIPTON: app.description,
                ATTR_ADVANCED: app.advanced,  # Deprecated 2026.03
                ATTR_STAGE: app.stage,
                ATTR_VERSION: app.version,
                ATTR_VERSION_LATEST: app.latest_version,
                ATTR_UPDATE_AVAILABLE: app.need_update,
                ATTR_AVAILABLE: app.available,
                ATTR_DETACHED: app.is_detached,
                ATTR_HOMEASSISTANT: app.homeassistant_version,
                ATTR_STATE: app.state,
                ATTR_REPOSITORY: app.repository,
                ATTR_BUILD: app.need_build,
                ATTR_URL: app.url,
                ATTR_ICON: app.with_icon,
                ATTR_LOGO: app.with_logo,
                ATTR_SYSTEM_MANAGED: app.system_managed,
            }
            for app in self.sys_apps.installed
        ]

    @api_process
    async def list_apps(self, request: web.Request) -> dict[str, Any]:
        """Return all installed apps (v2: uses "apps" key)."""
        return {ATTR_APPS: self._list_apps_data()}

    @api_process
    async def list_apps_v1(self, request: web.Request) -> dict[str, Any]:
        """Return all installed apps (v1: uses "addons" key)."""
        return {ATTR_ADDONS: self._list_apps_data()}

    @api_process
    async def reload(self, request: web.Request) -> None:
        """Reload all app data from store."""
        await asyncio.shield(self.sys_store.reload())

    async def info_data(self, app: App) -> dict[str, Any]:
        """Build and return app information dict (raises on invalid state)."""
        return {
            ATTR_NAME: app.name,
            ATTR_SLUG: app.slug,
            ATTR_HOSTNAME: app.hostname,
            ATTR_DNS: app.dns,
            ATTR_DESCRIPTON: app.description,
            ATTR_LONG_DESCRIPTION: await app.long_description(),
            ATTR_ADVANCED: app.advanced,  # Deprecated 2026.03
            ATTR_STAGE: app.stage,
            ATTR_REPOSITORY: app.repository,
            ATTR_VERSION_LATEST: app.latest_version,
            ATTR_PROTECTED: app.protected,
            ATTR_RATING: rating_security(app),
            ATTR_BOOT_CONFIG: app.boot_config,
            ATTR_BOOT: app.boot,
            ATTR_OPTIONS: app.options,
            ATTR_SCHEMA: app.schema_ui,
            ATTR_ARCH: app.supported_arch,
            ATTR_MACHINE: app.supported_machine,
            ATTR_HOMEASSISTANT: app.homeassistant_version,
            ATTR_URL: app.url,
            ATTR_DETACHED: app.is_detached,
            ATTR_AVAILABLE: app.available,
            ATTR_BUILD: app.need_build,
            ATTR_NETWORK: app.ports,
            ATTR_NETWORK_DESCRIPTION: app.ports_description,
            ATTR_HOST_NETWORK: app.host_network,
            ATTR_HOST_PID: app.host_pid,
            ATTR_HOST_IPC: app.host_ipc,
            ATTR_HOST_UTS: app.host_uts,
            ATTR_HOST_DBUS: app.host_dbus,
            ATTR_PRIVILEGED: app.privileged,
            ATTR_FULL_ACCESS: app.with_full_access,
            ATTR_APPARMOR: app.apparmor,
            ATTR_ICON: app.with_icon,
            ATTR_LOGO: app.with_logo,
            ATTR_CHANGELOG: app.with_changelog,
            ATTR_DOCUMENTATION: app.with_documentation,
            ATTR_STDIN: app.with_stdin,
            ATTR_HASSIO_API: app.access_hassio_api,
            ATTR_HASSIO_ROLE: app.hassio_role,
            ATTR_AUTH_API: app.access_auth_api,
            ATTR_HOMEASSISTANT_API: app.access_homeassistant_api,
            ATTR_GPIO: app.with_gpio,
            ATTR_USB: app.with_usb,
            ATTR_UART: app.with_uart,
            ATTR_KERNEL_MODULES: app.with_kernel_modules,
            ATTR_DEVICETREE: app.with_devicetree,
            ATTR_UDEV: app.with_udev,
            ATTR_DOCKER_API: app.access_docker_api,
            ATTR_VIDEO: app.with_video,
            ATTR_AUDIO: app.with_audio,
            ATTR_STARTUP: app.startup,
            ATTR_SERVICES: _pretty_services(app),
            ATTR_DISCOVERY: app.discovery,
            ATTR_TRANSLATIONS: app.translations,
            ATTR_INGRESS: app.with_ingress,
            ATTR_SIGNED: app.signed,
            ATTR_STATE: app.state,
            ATTR_WEBUI: app.webui,
            ATTR_INGRESS_ENTRY: app.ingress_entry,
            ATTR_INGRESS_URL: app.ingress_url,
            ATTR_INGRESS_PORT: app.ingress_port,
            ATTR_INGRESS_PANEL: app.ingress_panel,
            ATTR_AUDIO_INPUT: app.audio_input,
            ATTR_AUDIO_OUTPUT: app.audio_output,
            ATTR_AUTO_UPDATE: app.auto_update,
            ATTR_IP_ADDRESS: str(app.ip_address),
            ATTR_VERSION: app.version,
            ATTR_UPDATE_AVAILABLE: app.need_update,
            ATTR_WATCHDOG: app.watchdog,
            ATTR_DEVICES: app.static_devices + [device.path for device in app.devices],
            ATTR_SYSTEM_MANAGED: app.system_managed,
            ATTR_SYSTEM_MANAGED_CONFIG_ENTRY: app.system_managed_config_entry,
        }

    @api_process
    async def info(self, request: web.Request) -> dict[str, Any]:
        """Return app information."""
        app: App = self.get_app_for_request(request)
        return await self.info_data(app)

    @api_process
    async def options(self, request: web.Request) -> None:
        """Store user options for app."""
        app = self.get_app_for_request(request)

        # Update secrets for validation
        await self.sys_homeassistant.secrets.reload()

        # Validate/Process Body
        body = await api_validate(SCHEMA_OPTIONS, request)
        if ATTR_OPTIONS in body:
            # None resets options to defaults, otherwise validate the options
            if body[ATTR_OPTIONS] is None:
                app.options = None
            else:
                try:
                    app.options = app.schema(body[ATTR_OPTIONS])
                except vol.Invalid as ex:
                    raise AppConfigurationInvalidError(
                        app=app.slug,
                        validation_error=humanize_error(body[ATTR_OPTIONS], ex),
                    ) from None
        if ATTR_BOOT in body:
            if app.boot_config == AppBootConfig.MANUAL_ONLY:
                raise AppBootConfigCannotChangeError(
                    app=app.slug, boot_config=app.boot_config.value
                )
            app.boot = body[ATTR_BOOT]
        if ATTR_AUTO_UPDATE in body:
            app.auto_update = body[ATTR_AUTO_UPDATE]
        if ATTR_NETWORK in body:
            app.ports = body[ATTR_NETWORK]
        if ATTR_AUDIO_INPUT in body:
            app.audio_input = body[ATTR_AUDIO_INPUT]
        if ATTR_AUDIO_OUTPUT in body:
            app.audio_output = body[ATTR_AUDIO_OUTPUT]
        if ATTR_INGRESS_PANEL in body:
            app.ingress_panel = body[ATTR_INGRESS_PANEL]
            await self.sys_ingress.update_hass_panel(app)
        if ATTR_WATCHDOG in body:
            app.watchdog = body[ATTR_WATCHDOG]

        await app.save_persist()

    @api_process
    async def sys_options(self, request: web.Request) -> None:
        """Store system options for an app."""
        app = self.get_app_for_request(request)

        # Validate/Process Body
        body = await api_validate(SCHEMA_SYS_OPTIONS, request)
        if ATTR_SYSTEM_MANAGED in body:
            app.system_managed = body[ATTR_SYSTEM_MANAGED]
        if ATTR_SYSTEM_MANAGED_CONFIG_ENTRY in body:
            app.system_managed_config_entry = body[ATTR_SYSTEM_MANAGED_CONFIG_ENTRY]

        await app.save_persist()

    @api_process
    async def options_validate(self, request: web.Request) -> OptionsValidateResponse:
        """Validate user options for app."""
        app = self.get_app_for_request(request)
        data = OptionsValidateResponse(message="", valid=True, pwned=False)

        options = await request.json(loads=json_loads) or app.options

        # Validate config
        options_schema = app.schema
        try:
            options_schema.validate(options)
        except vol.Invalid as ex:
            data["message"] = humanize_error(options, ex)
            data["valid"] = False

        if not self.sys_security.pwned:
            return data

        # Pwned check
        for secret in options_schema.pwned:
            try:
                await self.sys_security.verify_secret(secret)
                continue
            except PwnedSecret:
                data["pwned"] = True
            except PwnedError:
                data["pwned"] = None
            break

        if self.sys_security.force and data["pwned"] in (None, True):
            data["valid"] = False
            if data["pwned"] is None:
                data["message"] = "Error happening on pwned secrets check!"
            else:
                data["message"] = "App uses pwned secrets!"

        return data

    @api_process
    async def options_config(self, request: web.Request) -> dict[str, Any]:
        """Validate user options for app."""
        slug: str = request.match_info["app"]
        if slug != "self":
            raise APIForbidden("This can be only read by the app itself!")
        app = self.get_app_for_request(request)

        # Lookup/reload secrets
        await self.sys_homeassistant.secrets.reload()
        try:
            return app.schema.validate(app.options)
        except vol.Invalid:
            raise APIError("Invalid configuration data for the app") from None

    @api_process
    async def security(self, request: web.Request) -> None:
        """Store security options for app."""
        app = self.get_app_for_request(request)
        body: dict[str, Any] = await api_validate(SCHEMA_SECURITY, request)

        if ATTR_PROTECTED in body:
            _LOGGER.warning("Changing protected flag for %s!", app.slug)
            app.protected = body[ATTR_PROTECTED]

        await app.save_persist()

    @api_process
    async def stats(self, request: web.Request) -> dict[str, Any]:
        """Return resource information."""
        app = self.get_app_for_request(request)

        stats: DockerStats = await app.stats()

        return {
            ATTR_CPU_PERCENT: stats.cpu_percent,
            ATTR_MEMORY_USAGE: stats.memory_usage,
            ATTR_MEMORY_LIMIT: stats.memory_limit,
            ATTR_MEMORY_PERCENT: stats.memory_percent,
            ATTR_NETWORK_RX: stats.network_rx,
            ATTR_NETWORK_TX: stats.network_tx,
            ATTR_BLK_READ: stats.blk_read,
            ATTR_BLK_WRITE: stats.blk_write,
        }

    @api_process
    async def uninstall(self, request: web.Request) -> None:
        """Uninstall app."""
        app = self.get_app_for_request(request)
        body: dict[str, Any] = await api_validate(SCHEMA_UNINSTALL, request)
        await asyncio.shield(
            self.sys_apps.uninstall(app.slug, remove_config=body[ATTR_REMOVE_CONFIG])
        )

    @api_process
    async def start(self, request: web.Request) -> None:
        """Start app."""
        app = self.get_app_for_request(request)
        if start_task := await asyncio.shield(app.start()):
            await start_task

    @api_process
    def stop(self, request: web.Request) -> Awaitable[None]:
        """Stop app."""
        app = self.get_app_for_request(request)
        return asyncio.shield(app.stop())

    @api_process
    async def restart(self, request: web.Request) -> None:
        """Restart app."""
        app: App = self.get_app_for_request(request)
        if start_task := await asyncio.shield(app.restart()):
            await start_task

    @api_process
    async def rebuild(self, request: web.Request) -> None:
        """Rebuild local build app."""
        app = self.get_app_for_request(request)
        body: dict[str, Any] = await api_validate(SCHEMA_REBUILD, request)

        if start_task := await asyncio.shield(
            self.sys_apps.rebuild(app.slug, force=body[ATTR_FORCE])
        ):
            await start_task

    @api_process
    async def stdin(self, request: web.Request) -> None:
        """Write to stdin of app."""
        app = self.get_app_for_request(request)
        if not app.with_stdin:
            raise AppNotSupportedWriteStdinError(_LOGGER.error, app=app.slug)

        data = await request.read()
        await asyncio.shield(app.write_stdin(data))


def _pretty_services(app: App) -> list[str]:
    """Return a simplified services role list."""
    return [f"{name}:{access}" for name, access in app.services_role.items()]
