"""Init file for HassIO homeassistant rest api."""
import asyncio
import logging

import voluptuous as vol
from voluptuous.humanize import humanize_error

from .util import api_process, api_process_raw, api_validate
from ..const import (
    ATTR_VERSION, ATTR_LAST_VERSION, ATTR_STATE, ATTR_BOOT, ATTR_OPTIONS,
    ATTR_URL, ATTR_DESCRIPTON, ATTR_DETACHED, ATTR_NAME, ATTR_REPOSITORY,
    ATTR_BUILD, ATTR_AUTO_UPDATE, ATTR_NETWORK, ATTR_HOST_NETWORK, ATTR_SLUG,
    ATTR_SOURCE, ATTR_REPOSITORIES, ATTR_ADDONS, ATTR_ARCH, ATTR_MAINTAINER,
    ATTR_INSTALLED, ATTR_LOGO, ATTR_WEBUI, BOOT_AUTO, BOOT_MANUAL,
    CONTENT_TYPE_PNG, CONTENT_TYPE_BINARY)
from ..validate import DOCKER_PORTS

_LOGGER = logging.getLogger(__name__)

SCHEMA_VERSION = vol.Schema({
    vol.Optional(ATTR_VERSION): vol.Coerce(str),
})

# pylint: disable=no-value-for-parameter
SCHEMA_OPTIONS = vol.Schema({
    vol.Optional(ATTR_BOOT): vol.In([BOOT_AUTO, BOOT_MANUAL]),
    vol.Optional(ATTR_NETWORK): vol.Any(None, DOCKER_PORTS),
    vol.Optional(ATTR_AUTO_UPDATE): vol.Boolean(),
})


class APIAddons(object):
    """Handle rest api for addons functions."""

    def __init__(self, config, loop, addons):
        """Initialize homeassistant rest api part."""
        self.config = config
        self.loop = loop
        self.addons = addons

    def _extract_addon(self, request, check_installed=True):
        """Return addon and if not exists trow a exception."""
        addon = self.addons.get(request.match_info.get('addon'))
        if not addon:
            raise RuntimeError("Addon not exists")

        if check_installed and not addon.is_installed:
            raise RuntimeError("Addon is not installed")

        return addon

    @api_process
    async def list(self, request):
        """Return all addons / repositories ."""
        data_addons = []
        for addon in self.addons.list_addons:
            data_addons.append({
                ATTR_NAME: addon.name,
                ATTR_SLUG: addon.slug,
                ATTR_DESCRIPTON: addon.description,
                ATTR_VERSION: addon.last_version,
                ATTR_INSTALLED: addon.version_installed,
                ATTR_ARCH: addon.supported_arch,
                ATTR_DETACHED: addon.is_detached,
                ATTR_REPOSITORY: addon.repository,
                ATTR_BUILD: addon.need_build,
                ATTR_URL: addon.url,
                ATTR_LOGO: addon.with_logo,
            })

        data_repositories = []
        for repository in self.addons.list_repositories:
            data_repositories.append({
                ATTR_SLUG: repository.slug,
                ATTR_NAME: repository.name,
                ATTR_SOURCE: repository.source,
                ATTR_URL: repository.url,
                ATTR_MAINTAINER: repository.maintainer,
            })

        return {
            ATTR_ADDONS: data_addons,
            ATTR_REPOSITORIES: data_repositories,
        }

    @api_process
    def reload(self, request):
        """Reload all addons data."""
        return self.addons.reload()

    @api_process
    async def info(self, request):
        """Return addon information."""
        addon = self._extract_addon(request, check_installed=False)

        return {
            ATTR_NAME: addon.name,
            ATTR_DESCRIPTON: addon.description,
            ATTR_VERSION: addon.version_installed,
            ATTR_AUTO_UPDATE: addon.auto_update,
            ATTR_REPOSITORY: addon.repository,
            ATTR_LAST_VERSION: addon.last_version,
            ATTR_STATE: await addon.state(),
            ATTR_BOOT: addon.boot,
            ATTR_OPTIONS: addon.options,
            ATTR_URL: addon.url,
            ATTR_DETACHED: addon.is_detached,
            ATTR_BUILD: addon.need_build,
            ATTR_NETWORK: addon.ports,
            ATTR_HOST_NETWORK: addon.network_mode == 'host',
            ATTR_LOGO: addon.with_logo,
            ATTR_WEBUI: addon.webui,
        }

    @api_process
    async def options(self, request):
        """Store user options for addon."""
        addon = self._extract_addon(request)

        addon_schema = SCHEMA_OPTIONS.extend({
            vol.Optional(ATTR_OPTIONS): addon.schema,
        })

        body = await api_validate(addon_schema, request)

        if ATTR_OPTIONS in body:
            addon.options = body[ATTR_OPTIONS]
        if ATTR_BOOT in body:
            addon.boot = body[ATTR_BOOT]
        if ATTR_AUTO_UPDATE in body:
            addon.auto_update = body[ATTR_AUTO_UPDATE]
        if ATTR_NETWORK in body:
            addon.ports = body[ATTR_NETWORK]

        return True

    @api_process
    async def install(self, request):
        """Install addon."""
        body = await api_validate(SCHEMA_VERSION, request)
        addon = self._extract_addon(request, check_installed=False)
        version = body.get(ATTR_VERSION)

        return await asyncio.shield(
            addon.install(version=version), loop=self.loop)

    @api_process
    async def uninstall(self, request):
        """Uninstall addon."""
        addon = self._extract_addon(request)
        return await asyncio.shield(addon.uninstall(), loop=self.loop)

    @api_process
    async def start(self, request):
        """Start addon."""
        addon = self._extract_addon(request)

        # check options
        options = addon.options
        try:
            addon.schema(options)
        except vol.Invalid as ex:
            raise RuntimeError(humanize_error(options, ex)) from None

        return await asyncio.shield(addon.start(), loop=self.loop)

    @api_process
    async def stop(self, request):
        """Stop addon."""
        addon = self._extract_addon(request)
        return await asyncio.shield(addon.stop(), loop=self.loop)

    @api_process
    async def update(self, request):
        """Update addon."""
        body = await api_validate(SCHEMA_VERSION, request)
        addon = self._extract_addon(request)
        version = body.get(ATTR_VERSION)

        return await asyncio.shield(
            addon.update(version=version), loop=self.loop)

    @api_process
    async def restart(self, request):
        """Restart addon."""
        addon = self._extract_addon(request)
        return await asyncio.shield(addon.restart(), loop=self.loop)

    @api_process_raw(CONTENT_TYPE_BINARY)
    def logs(self, request):
        """Return logs from addon."""
        addon = self._extract_addon(request)
        return addon.logs()

    @api_process_raw(CONTENT_TYPE_PNG)
    async def logo(self, request):
        """Return logo from addon."""
        addon = self._extract_addon(request, check_installed=False)
        if not addon.with_logo:
            raise RuntimeError("No image found!")

        with addon.path_logo.open('rb') as png:
            return png.read()
