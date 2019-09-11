"""Init file for Hass.io Home Assistant RESTful API."""
import asyncio
import logging
from typing import Any, Awaitable, Dict, List

from aiohttp import web
import voluptuous as vol
from voluptuous.humanize import humanize_error

from ..addons import AnyAddon
from ..docker.stats import DockerStats
from ..addons.utils import rating_security
from ..const import (
    ATTR_ADDONS,
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
    ATTR_HOSTNAME,
    ATTR_ICON,
    ATTR_INGRESS,
    ATTR_INGRESS_ENTRY,
    ATTR_INGRESS_PANEL,
    ATTR_INGRESS_PORT,
    ATTR_INGRESS_URL,
    ATTR_INSTALLED,
    ATTR_IP_ADDRESS,
    ATTR_KERNEL_MODULES,
    ATTR_LAST_VERSION,
    ATTR_LOGO,
    ATTR_LONG_DESCRIPTION,
    ATTR_MACHINE,
    ATTR_MAINTAINER,
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
    ATTR_REPOSITORIES,
    ATTR_REPOSITORY,
    ATTR_SERVICES,
    ATTR_SLUG,
    ATTR_SOURCE,
    ATTR_STATE,
    ATTR_STDIN,
    ATTR_UDEV,
    ATTR_URL,
    ATTR_VERSION,
    ATTR_WEBUI,
    BOOT_AUTO,
    BOOT_MANUAL,
    CONTENT_TYPE_BINARY,
    CONTENT_TYPE_PNG,
    CONTENT_TYPE_TEXT,
    REQUEST_FROM,
    STATE_NONE,
)
from ..coresys import CoreSysAttributes
from ..exceptions import APIError
from ..validate import ALSA_DEVICE, DOCKER_PORTS
from .utils import api_process, api_process_raw, api_validate

_LOGGER: logging.Logger = logging.getLogger(__name__)

SCHEMA_VERSION = vol.Schema({vol.Optional(ATTR_VERSION): vol.Coerce(str)})

# pylint: disable=no-value-for-parameter
SCHEMA_OPTIONS = vol.Schema(
    {
        vol.Optional(ATTR_BOOT): vol.In([BOOT_AUTO, BOOT_MANUAL]),
        vol.Optional(ATTR_NETWORK): vol.Any(None, DOCKER_PORTS),
        vol.Optional(ATTR_AUTO_UPDATE): vol.Boolean(),
        vol.Optional(ATTR_AUDIO_OUTPUT): ALSA_DEVICE,
        vol.Optional(ATTR_AUDIO_INPUT): ALSA_DEVICE,
        vol.Optional(ATTR_INGRESS_PANEL): vol.Boolean(),
    }
)

# pylint: disable=no-value-for-parameter
SCHEMA_SECURITY = vol.Schema({vol.Optional(ATTR_PROTECTED): vol.Boolean()})


class APIAddons(CoreSysAttributes):
    """Handle RESTful API for add-on functions."""

    def _extract_addon(
        self, request: web.Request, check_installed: bool = True
    ) -> AnyAddon:
        """Return addon, throw an exception it it doesn't exist."""
        addon_slug: str = request.match_info.get("addon")

        # Lookup itself
        if addon_slug == "self":
            return request.get(REQUEST_FROM)

        addon = self.sys_addons.get(addon_slug)
        if not addon:
            raise APIError("Addon does not exist")

        if check_installed and not addon.is_installed:
            raise APIError("Addon is not installed")

        return addon

    @api_process
    async def list(self, request: web.Request) -> Dict[str, Any]:
        """Return all add-ons or repositories."""
        data_addons = []
        for addon in self.sys_addons.all:
            data_addons.append(
                {
                    ATTR_NAME: addon.name,
                    ATTR_SLUG: addon.slug,
                    ATTR_DESCRIPTON: addon.description,
                    ATTR_VERSION: addon.latest_version,
                    ATTR_INSTALLED: addon.version if addon.is_installed else None,
                    ATTR_AVAILABLE: addon.available,
                    ATTR_DETACHED: addon.is_detached,
                    ATTR_REPOSITORY: addon.repository,
                    ATTR_BUILD: addon.need_build,
                    ATTR_URL: addon.url,
                    ATTR_ICON: addon.with_icon,
                    ATTR_LOGO: addon.with_logo,
                }
            )

        data_repositories = []
        for repository in self.sys_store.all:
            data_repositories.append(
                {
                    ATTR_SLUG: repository.slug,
                    ATTR_NAME: repository.name,
                    ATTR_SOURCE: repository.source,
                    ATTR_URL: repository.url,
                    ATTR_MAINTAINER: repository.maintainer,
                }
            )

        return {ATTR_ADDONS: data_addons, ATTR_REPOSITORIES: data_repositories}

    @api_process
    async def reload(self, request: web.Request) -> None:
        """Reload all add-on data from store."""
        await asyncio.shield(self.sys_store.reload())

    @api_process
    async def info(self, request: web.Request) -> Dict[str, Any]:
        """Return add-on information."""
        addon: AnyAddon = self._extract_addon(request, check_installed=False)

        data = {
            ATTR_NAME: addon.name,
            ATTR_SLUG: addon.slug,
            ATTR_HOSTNAME: addon.hostname,
            ATTR_DNS: addon.dns,
            ATTR_DESCRIPTON: addon.description,
            ATTR_LONG_DESCRIPTION: addon.long_description,
            ATTR_AUTO_UPDATE: None,
            ATTR_REPOSITORY: addon.repository,
            ATTR_VERSION: None,
            ATTR_LAST_VERSION: addon.latest_version,
            ATTR_PROTECTED: addon.protected,
            ATTR_RATING: rating_security(addon),
            ATTR_BOOT: addon.boot,
            ATTR_OPTIONS: addon.options,
            ATTR_ARCH: addon.supported_arch,
            ATTR_MACHINE: addon.supported_machine,
            ATTR_HOMEASSISTANT: addon.homeassistant_version,
            ATTR_URL: addon.url,
            ATTR_STATE: STATE_NONE,
            ATTR_DETACHED: addon.is_detached,
            ATTR_AVAILABLE: addon.available,
            ATTR_BUILD: addon.need_build,
            ATTR_NETWORK: addon.ports,
            ATTR_NETWORK_DESCRIPTION: addon.ports_description,
            ATTR_HOST_NETWORK: addon.host_network,
            ATTR_HOST_PID: addon.host_pid,
            ATTR_HOST_IPC: addon.host_ipc,
            ATTR_HOST_DBUS: addon.host_dbus,
            ATTR_PRIVILEGED: addon.privileged,
            ATTR_FULL_ACCESS: addon.with_full_access,
            ATTR_APPARMOR: addon.apparmor,
            ATTR_DEVICES: _pretty_devices(addon),
            ATTR_ICON: addon.with_icon,
            ATTR_LOGO: addon.with_logo,
            ATTR_CHANGELOG: addon.with_changelog,
            ATTR_STDIN: addon.with_stdin,
            ATTR_WEBUI: None,
            ATTR_HASSIO_API: addon.access_hassio_api,
            ATTR_HASSIO_ROLE: addon.hassio_role,
            ATTR_AUTH_API: addon.access_auth_api,
            ATTR_HOMEASSISTANT_API: addon.access_homeassistant_api,
            ATTR_GPIO: addon.with_gpio,
            ATTR_KERNEL_MODULES: addon.with_kernel_modules,
            ATTR_DEVICETREE: addon.with_devicetree,
            ATTR_UDEV: addon.with_udev,
            ATTR_DOCKER_API: addon.access_docker_api,
            ATTR_AUDIO: addon.with_audio,
            ATTR_AUDIO_INPUT: None,
            ATTR_AUDIO_OUTPUT: None,
            ATTR_SERVICES: _pretty_services(addon),
            ATTR_DISCOVERY: addon.discovery,
            ATTR_IP_ADDRESS: None,
            ATTR_INGRESS: addon.with_ingress,
            ATTR_INGRESS_ENTRY: None,
            ATTR_INGRESS_URL: None,
            ATTR_INGRESS_PORT: None,
            ATTR_INGRESS_PANEL: None,
        }

        if addon.is_installed:
            data.update(
                {
                    ATTR_STATE: await addon.state(),
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
                }
            )

        return data

    @api_process
    async def options(self, request: web.Request) -> None:
        """Store user options for add-on."""
        addon: AnyAddon = self._extract_addon(request)

        addon_schema = SCHEMA_OPTIONS.extend(
            {vol.Optional(ATTR_OPTIONS): vol.Any(None, addon.schema)}
        )
        body: Dict[str, Any] = await api_validate(
            addon_schema, request, origin=[ATTR_OPTIONS]
        )

        if ATTR_OPTIONS in body:
            addon.options = body[ATTR_OPTIONS]
        if ATTR_BOOT in body:
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

        addon.save_persist()

    @api_process
    async def security(self, request: web.Request) -> None:
        """Store security options for add-on."""
        addon: AnyAddon = self._extract_addon(request)
        body: Dict[str, Any] = await api_validate(SCHEMA_SECURITY, request)

        if ATTR_PROTECTED in body:
            _LOGGER.warning("Protected flag changing for %s!", addon.slug)
            addon.protected = body[ATTR_PROTECTED]

        addon.save_persist()

    @api_process
    async def stats(self, request: web.Request) -> Dict[str, Any]:
        """Return resource information."""
        addon: AnyAddon = self._extract_addon(request)
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
    def install(self, request: web.Request) -> Awaitable[None]:
        """Install add-on."""
        addon: AnyAddon = self._extract_addon(request, check_installed=False)
        return asyncio.shield(addon.install())

    @api_process
    def uninstall(self, request: web.Request) -> Awaitable[None]:
        """Uninstall add-on."""
        addon: AnyAddon = self._extract_addon(request)
        return asyncio.shield(addon.uninstall())

    @api_process
    def start(self, request: web.Request) -> Awaitable[None]:
        """Start add-on."""
        addon: AnyAddon = self._extract_addon(request)

        # check options
        options = addon.options
        try:
            addon.schema(options)
        except vol.Invalid as ex:
            raise APIError(humanize_error(options, ex)) from None

        return asyncio.shield(addon.start())

    @api_process
    def stop(self, request: web.Request) -> Awaitable[None]:
        """Stop add-on."""
        addon: AnyAddon = self._extract_addon(request)
        return asyncio.shield(addon.stop())

    @api_process
    def update(self, request: web.Request) -> Awaitable[None]:
        """Update add-on."""
        addon: AnyAddon = self._extract_addon(request)

        if addon.latest_version == addon.version:
            raise APIError("No update available!")

        return asyncio.shield(addon.update())

    @api_process
    def restart(self, request: web.Request) -> Awaitable[None]:
        """Restart add-on."""
        addon: AnyAddon = self._extract_addon(request)
        return asyncio.shield(addon.restart())

    @api_process
    def rebuild(self, request: web.Request) -> Awaitable[None]:
        """Rebuild local build add-on."""
        addon: AnyAddon = self._extract_addon(request)
        if not addon.need_build:
            raise APIError("Only local build addons are supported")

        return asyncio.shield(addon.rebuild())

    @api_process_raw(CONTENT_TYPE_BINARY)
    def logs(self, request: web.Request) -> Awaitable[bytes]:
        """Return logs from add-on."""
        addon: AnyAddon = self._extract_addon(request)
        return addon.logs()

    @api_process_raw(CONTENT_TYPE_PNG)
    async def icon(self, request: web.Request) -> bytes:
        """Return icon from add-on."""
        addon: AnyAddon = self._extract_addon(request, check_installed=False)
        if not addon.with_icon:
            raise APIError("No icon found!")

        with addon.path_icon.open("rb") as png:
            return png.read()

    @api_process_raw(CONTENT_TYPE_PNG)
    async def logo(self, request: web.Request) -> bytes:
        """Return logo from add-on."""
        addon: AnyAddon = self._extract_addon(request, check_installed=False)
        if not addon.with_logo:
            raise APIError("No logo found!")

        with addon.path_logo.open("rb") as png:
            return png.read()

    @api_process_raw(CONTENT_TYPE_TEXT)
    async def changelog(self, request: web.Request) -> str:
        """Return changelog from add-on."""
        addon: AnyAddon = self._extract_addon(request, check_installed=False)
        if not addon.with_changelog:
            raise APIError("No changelog found!")

        with addon.path_changelog.open("r") as changelog:
            return changelog.read()

    @api_process
    async def stdin(self, request: web.Request) -> None:
        """Write to stdin of add-on."""
        addon: AnyAddon = self._extract_addon(request)
        if not addon.with_stdin:
            raise APIError("STDIN not supported by add-on")

        data = await request.read()
        await asyncio.shield(addon.write_stdin(data))


def _pretty_devices(addon: AnyAddon) -> List[str]:
    """Return a simplified device list."""
    dev_list = addon.devices
    if not dev_list:
        return None
    return [row.split(":")[0] for row in dev_list]


def _pretty_services(addon: AnyAddon) -> List[str]:
    """Return a simplified services role list."""
    services = []
    for name, access in addon.services_role.items():
        services.append(f"{name}:{access}")
    return services
