"""Init file for HassIO homeassistant rest api."""
import asyncio
import logging

import voluptuous as vol
from voluptuous.humanize import humanize_error

from .util import api_process, api_process_raw, api_validate
from ..const import (
    ATTR_VERSION, ATTR_LAST_VERSION, ATTR_STATE, ATTR_BOOT, ATTR_OPTIONS,
    ATTR_URL, ATTR_DESCRIPTON, ATTR_DETACHED, ATTR_NAME, ATTR_REPOSITORY,
    STATE_STOPPED, STATE_STARTED, BOOT_AUTO, BOOT_MANUAL)

_LOGGER = logging.getLogger(__name__)

SCHEMA_VERSION = vol.Schema({
    vol.Optional(ATTR_VERSION): vol.Coerce(str),
})

SCHEMA_OPTIONS = vol.Schema({
    vol.Optional(ATTR_BOOT): vol.In([BOOT_AUTO, BOOT_MANUAL])
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
        addon = request.match_info.get('addon')

        # check data
        if not self.addons.exists_addon(addon):
            raise RuntimeError("Addon not exists")
        if check_installed and not self.addons.is_installed(addon):
            raise RuntimeError("Addon is not installed")

        return addon

    @api_process
    async def info(self, request):
        """Return addon information."""
        addon = self._extract_addon(request)

        return {
            ATTR_NAME: self.addons.get_name(addon),
            ATTR_DESCRIPTON: self.addons.get_description(addon),
            ATTR_VERSION: self.addons.version_installed(addon),
            ATTR_REPOSITORY: self.addons.get_repository(addon),
            ATTR_LAST_VERSION: self.addons.get_last_version(addon),
            ATTR_STATE: await self.addons.state(addon),
            ATTR_BOOT: self.addons.get_boot(addon),
            ATTR_OPTIONS: self.addons.get_options(addon),
            ATTR_URL: self.addons.get_url(addon),
            ATTR_DETACHED: addon in self.addons.list_detached,
        }

    @api_process
    async def options(self, request):
        """Store user options for addon."""
        addon = self._extract_addon(request)
        options_schema = self.addons.get_schema(addon)

        addon_schema = SCHEMA_OPTIONS.extend({
            vol.Optional(ATTR_OPTIONS): options_schema,
        })

        body = await api_validate(addon_schema, request)

        if ATTR_OPTIONS in body:
            self.addons.set_options(addon, body[ATTR_OPTIONS])
        if ATTR_BOOT in body:
            self.addons.set_boot(addon, body[ATTR_BOOT])

        return True

    @api_process
    async def install(self, request):
        """Install addon."""
        body = await api_validate(SCHEMA_VERSION, request)
        addon = self._extract_addon(request, check_installed=False)
        version = body.get(
            ATTR_VERSION, self.addons.get_last_version(addon))

        # check if arch supported
        if self.addons.arch not in self.addons.get_arch(addon):
            raise RuntimeError(
                "Addon is not supported on {}".format(self.addons.arch))

        return await asyncio.shield(
            self.addons.install(addon, version), loop=self.loop)

    @api_process
    async def uninstall(self, request):
        """Uninstall addon."""
        addon = self._extract_addon(request)

        return await asyncio.shield(
            self.addons.uninstall(addon), loop=self.loop)

    @api_process
    async def start(self, request):
        """Start addon."""
        addon = self._extract_addon(request)

        if await self.addons.state(addon) == STATE_STARTED:
            raise RuntimeError("Addon is already running")

        # validate options
        try:
            schema = self.addons.get_schema(addon)
            options = self.addons.get_options(addon)
            schema(options)
        except vol.Invalid as ex:
            raise RuntimeError(humanize_error(options, ex)) from None

        return await asyncio.shield(
            self.addons.start(addon), loop=self.loop)

    @api_process
    async def stop(self, request):
        """Stop addon."""
        addon = self._extract_addon(request)

        if await self.addons.state(addon) == STATE_STOPPED:
            raise RuntimeError("Addon is already stoped")

        return await asyncio.shield(
            self.addons.stop(addon), loop=self.loop)

    @api_process
    async def update(self, request):
        """Update addon."""
        body = await api_validate(SCHEMA_VERSION, request)
        addon = self._extract_addon(request)
        version = body.get(
            ATTR_VERSION, self.addons.get_last_version(addon))

        if version == self.addons.version_installed(addon):
            raise RuntimeError("Version is already in use")

        return await asyncio.shield(
            self.addons.update(addon, version), loop=self.loop)

    @api_process
    async def restart(self, request):
        """Restart addon."""
        addon = self._extract_addon(request)
        return await asyncio.shield(self.addons.restart(addon), loop=self.loop)

    @api_process_raw
    def logs(self, request):
        """Return logs from addon."""
        addon = self._extract_addon(request)
        return self.addons.logs(addon)
