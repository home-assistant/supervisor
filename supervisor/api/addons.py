"""Init file for Supervisor Home Assistant RESTful API."""

import asyncio
from collections.abc import Awaitable
import logging
from typing import Any, TypedDict

from aiohttp import web
import voluptuous as vol
from voluptuous.humanize import humanize_error

from ..addons.addon import Addon
from ..addons.utils import rating_security
from ..const import (
    ATTR_ADDONS,
    ATTR_ADVANCED,
    ATTR_APPARMOR,
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
    AddonBoot,
    AddonBootConfig,
)
from ..coresys import CoreSysAttributes
from ..docker.stats import DockerStats
from ..exceptions import (
    APIAddonNotInstalled,
    APIError,
    APIForbidden,
    APINotFound,
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
        vol.Optional(ATTR_BOOT): vol.Coerce(AddonBoot),
        vol.Optional(ATTR_NETWORK): vol.Maybe(docker_ports),
        vol.Optional(ATTR_AUTO_UPDATE): vol.Boolean(),
        vol.Optional(ATTR_AUDIO_OUTPUT): vol.Maybe(str),
        vol.Optional(ATTR_AUDIO_INPUT): vol.Maybe(str),
        vol.Optional(ATTR_INGRESS_PANEL): vol.Boolean(),
        vol.Optional(ATTR_WATCHDOG): vol.Boolean(),
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
# pylint: enable=no-value-for-parameter


class OptionsValidateResponse(TypedDict):
    """Response object for options validate."""

    message: str
    valid: bool
    pwned: bool | None


class APIAddons(CoreSysAttributes):
    """Handle RESTful API for add-on functions."""

    def get_addon_for_request(self, request: web.Request) -> Addon:
        """Return addon, throw an exception if it doesn't exist."""
        addon_slug: str = request.match_info["addon"]

        # Lookup itself
        if addon_slug == "self":
            addon = request.get(REQUEST_FROM)
            if not isinstance(addon, Addon):
                raise APIError("Self is not an Addon")
            return addon

        addon = self.sys_addons.get(addon_slug)
        if not addon:
            raise APINotFound(f"Addon {addon_slug} does not exist")
        if not isinstance(addon, Addon) or not addon.is_installed:
            raise APIAddonNotInstalled("Addon is not installed")

        return addon

    @api_process
    async def list_addons(self, request: web.Request) -> dict[str, Any]:
        """Return all add-ons or repositories."""
        data_addons = [
            {
                ATTR_NAME: addon.name,
                ATTR_SLUG: addon.slug,
                ATTR_DESCRIPTON: addon.description,
                ATTR_ADVANCED: addon.advanced,
                ATTR_STAGE: addon.stage,
                ATTR_VERSION: addon.version,
                ATTR_VERSION_LATEST: addon.latest_version,
                ATTR_UPDATE_AVAILABLE: addon.need_update,
                ATTR_AVAILABLE: addon.available,
                ATTR_DETACHED: addon.is_detached,
                ATTR_HOMEASSISTANT: addon.homeassistant_version,
                ATTR_STATE: addon.state,
                ATTR_REPOSITORY: addon.repository,
                ATTR_BUILD: addon.need_build,
                ATTR_URL: addon.url,
                ATTR_ICON: addon.with_icon,
                ATTR_LOGO: addon.with_logo,
                ATTR_SYSTEM_MANAGED: addon.system_managed,
            }
            for addon in self.sys_addons.installed
        ]

        return {ATTR_ADDONS: data_addons}

    @api_process
    async def reload(self, request: web.Request) -> None:
        """Reload all add-on data from store."""
        await asyncio.shield(self.sys_store.reload())

    async def info(self, request: web.Request) -> dict[str, Any]:
        """Return add-on information."""
        addon: Addon = self.get_addon_for_request(request)

        data = {
            ATTR_NAME: addon.name,
            ATTR_SLUG: addon.slug,
            ATTR_HOSTNAME: addon.hostname,
            ATTR_DNS: addon.dns,
            ATTR_DESCRIPTON: addon.description,
            ATTR_LONG_DESCRIPTION: await addon.long_description(),
            ATTR_ADVANCED: addon.advanced,
            ATTR_STAGE: addon.stage,
            ATTR_REPOSITORY: addon.repository,
            ATTR_VERSION_LATEST: addon.latest_version,
            ATTR_PROTECTED: addon.protected,
            ATTR_RATING: rating_security(addon),
            ATTR_BOOT_CONFIG: addon.boot_config,
            ATTR_BOOT: addon.boot,
            ATTR_OPTIONS: addon.options,
            ATTR_SCHEMA: addon.schema_ui,
            ATTR_ARCH: addon.supported_arch,
            ATTR_MACHINE: addon.supported_machine,
            ATTR_HOMEASSISTANT: addon.homeassistant_version,
            ATTR_URL: addon.url,
            ATTR_DETACHED: addon.is_detached,
            ATTR_AVAILABLE: addon.available,
            ATTR_BUILD: addon.need_build,
            ATTR_NETWORK: addon.ports,
            ATTR_NETWORK_DESCRIPTION: addon.ports_description,
            ATTR_HOST_NETWORK: addon.host_network,
            ATTR_HOST_PID: addon.host_pid,
            ATTR_HOST_IPC: addon.host_ipc,
            ATTR_HOST_UTS: addon.host_uts,
            ATTR_HOST_DBUS: addon.host_dbus,
            ATTR_PRIVILEGED: addon.privileged,
            ATTR_FULL_ACCESS: addon.with_full_access,
            ATTR_APPARMOR: addon.apparmor,
            ATTR_ICON: addon.with_icon,
            ATTR_LOGO: addon.with_logo,
            ATTR_CHANGELOG: addon.with_changelog,
            ATTR_DOCUMENTATION: addon.with_documentation,
            ATTR_STDIN: addon.with_stdin,
            ATTR_HASSIO_API: addon.access_hassio_api,
            ATTR_HASSIO_ROLE: addon.hassio_role,
            ATTR_AUTH_API: addon.access_auth_api,
            ATTR_HOMEASSISTANT_API: addon.access_homeassistant_api,
            ATTR_GPIO: addon.with_gpio,
            ATTR_USB: addon.with_usb,
            ATTR_UART: addon.with_uart,
            ATTR_KERNEL_MODULES: addon.with_kernel_modules,
            ATTR_DEVICETREE: addon.with_devicetree,
            ATTR_UDEV: addon.with_udev,
            ATTR_DOCKER_API: addon.access_docker_api,
            ATTR_VIDEO: addon.with_video,
            ATTR_AUDIO: addon.with_audio,
            ATTR_STARTUP: addon.startup,
            ATTR_SERVICES: _pretty_services(addon),
            ATTR_DISCOVERY: addon.discovery,
            ATTR_TRANSLATIONS: addon.translations,
            ATTR_INGRESS: addon.with_ingress,
            ATTR_SIGNED: addon.signed,
            ATTR_STATE: addon.state,
            ATTR_WEBUI: addon.webui,
            ATTR_INGRESS_ENTRY: addon.ingress_entry,
            ATTR_INGRESS_URL: addon.ingress_url,
            ATTR_INGRESS_PORT: addon.ingress_port,
            ATTR_INGRESS_PANEL: addon.ingress_panel,
            ATTR_AUDIO_INPUT: addon.audio_input,
            ATTR_AUDIO_OUTPUT: addon.audio_output,
            ATTR_AUTO_UPDATE: addon.auto_update,
            ATTR_IP_ADDRESS: str(addon.ip_address),
            ATTR_VERSION: addon.version,
            ATTR_UPDATE_AVAILABLE: addon.need_update,
            ATTR_WATCHDOG: addon.watchdog,
            ATTR_DEVICES: addon.static_devices
            + [device.path for device in addon.devices],
            ATTR_SYSTEM_MANAGED: addon.system_managed,
            ATTR_SYSTEM_MANAGED_CONFIG_ENTRY: addon.system_managed_config_entry,
        }

        return data

    @api_process
    async def options(self, request: web.Request) -> None:
        """Store user options for add-on."""
        addon = self.get_addon_for_request(request)

        # Update secrets for validation
        await self.sys_homeassistant.secrets.reload()

        # Extend schema with add-on specific validation
        addon_schema = SCHEMA_OPTIONS.extend(
            {vol.Optional(ATTR_OPTIONS): vol.Maybe(addon.schema)}
        )

        # Validate/Process Body
        body = await api_validate(addon_schema, request, origin=[ATTR_OPTIONS])
        if ATTR_OPTIONS in body:
            addon.options = body[ATTR_OPTIONS]
        if ATTR_BOOT in body:
            if addon.boot_config == AddonBootConfig.MANUAL_ONLY:
                raise APIError(
                    f"Addon {addon.slug} boot option is set to {addon.boot_config} so it cannot be changed"
                )
            addon.boot = body[ATTR_BOOT]
        if ATTR_AUTO_UPDATE in body:
            addon.auto_update = body[ATTR_AUTO_UPDATE]
        if ATTR_NETWORK in body:
            addon.ports = body[ATTR_NETWORK]
        if ATTR_AUDIO_INPUT in body:
            addon.audio_input = body[ATTR_AUDIO_INPUT]
        if ATTR_AUDIO_OUTPUT in body:
            addon.audio_output = body[ATTR_AUDIO_OUTPUT]
        if ATTR_INGRESS_PANEL in body:
            addon.ingress_panel = body[ATTR_INGRESS_PANEL]
            await self.sys_ingress.update_hass_panel(addon)
        if ATTR_WATCHDOG in body:
            addon.watchdog = body[ATTR_WATCHDOG]

        await addon.save_persist()

    @api_process
    async def sys_options(self, request: web.Request) -> None:
        """Store system options for an add-on."""
        addon = self.get_addon_for_request(request)

        # Validate/Process Body
        body = await api_validate(SCHEMA_SYS_OPTIONS, request)
        if ATTR_SYSTEM_MANAGED in body:
            addon.system_managed = body[ATTR_SYSTEM_MANAGED]
        if ATTR_SYSTEM_MANAGED_CONFIG_ENTRY in body:
            addon.system_managed_config_entry = body[ATTR_SYSTEM_MANAGED_CONFIG_ENTRY]

        await addon.save_persist()

    @api_process
    async def options_validate(self, request: web.Request) -> OptionsValidateResponse:
        """Validate user options for add-on."""
        addon = self.get_addon_for_request(request)
        data = OptionsValidateResponse(message="", valid=True, pwned=False)

        options = await request.json(loads=json_loads) or addon.options

        # Validate config
        options_schema = addon.schema
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
                data["message"] = "Add-on uses pwned secrets!"

        return data

    @api_process
    async def options_config(self, request: web.Request) -> None:
        """Validate user options for add-on."""
        slug: str = request.match_info["addon"]
        if slug != "self":
            raise APIForbidden("This can be only read by the Add-on itself!")
        addon = self.get_addon_for_request(request)

        # Lookup/reload secrets
        await self.sys_homeassistant.secrets.reload()
        try:
            return addon.schema.validate(addon.options)
        except vol.Invalid:
            raise APIError("Invalid configuration data for the add-on") from None

    @api_process
    async def security(self, request: web.Request) -> None:
        """Store security options for add-on."""
        addon = self.get_addon_for_request(request)
        body: dict[str, Any] = await api_validate(SCHEMA_SECURITY, request)

        if ATTR_PROTECTED in body:
            _LOGGER.warning("Changing protected flag for %s!", addon.slug)
            addon.protected = body[ATTR_PROTECTED]

        await addon.save_persist()

    @api_process
    async def stats(self, request: web.Request) -> dict[str, Any]:
        """Return resource information."""
        addon = self.get_addon_for_request(request)

        stats: DockerStats = await addon.stats()

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
    async def uninstall(self, request: web.Request) -> Awaitable[None]:
        """Uninstall add-on."""
        addon = self.get_addon_for_request(request)
        body: dict[str, Any] = await api_validate(SCHEMA_UNINSTALL, request)
        return await asyncio.shield(
            self.sys_addons.uninstall(
                addon.slug, remove_config=body[ATTR_REMOVE_CONFIG]
            )
        )

    @api_process
    async def start(self, request: web.Request) -> None:
        """Start add-on."""
        addon = self.get_addon_for_request(request)
        if start_task := await asyncio.shield(addon.start()):
            await start_task

    @api_process
    def stop(self, request: web.Request) -> Awaitable[None]:
        """Stop add-on."""
        addon = self.get_addon_for_request(request)
        return asyncio.shield(addon.stop())

    @api_process
    async def restart(self, request: web.Request) -> None:
        """Restart add-on."""
        addon: Addon = self.get_addon_for_request(request)
        if start_task := await asyncio.shield(addon.restart()):
            await start_task

    @api_process
    async def rebuild(self, request: web.Request) -> None:
        """Rebuild local build add-on."""
        addon = self.get_addon_for_request(request)
        if start_task := await asyncio.shield(self.sys_addons.rebuild(addon.slug)):
            await start_task

    @api_process
    async def stdin(self, request: web.Request) -> None:
        """Write to stdin of add-on."""
        addon = self.get_addon_for_request(request)
        if not addon.with_stdin:
            raise APIError(f"STDIN not supported the {addon.slug} add-on")

        data = await request.read()
        await asyncio.shield(addon.write_stdin(data))


def _pretty_services(addon: Addon) -> list[str]:
    """Return a simplified services role list."""
    return [f"{name}:{access}" for name, access in addon.services_role.items()]
