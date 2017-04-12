"""Init file for HassIO homeassistant rest api."""
import asyncio
import logging

import voluptuous as vol

from .util import api_process, api_validate
from ..const import (
    ATTR_VERSION, ATTR_CURRENT, ATTR_STATE, ATTR_BOOT, ATTR_OPTIONS,
    STATE_STOPPED, STATE_STARTED)

_LOGGER = logging.getLogger(__name__)

SCHEMA_VERSION = vol.Schema({
    vol.Optional(ATTR_VERSION): vol.Coerce(str),
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
            raise RuntimeError("Addon not exists.")
        if check_installed and not self.addons.is_installed(addon):
            raise RuntimeError("Addon is not installed.")

        return addon

    @api_process
    async def info(self, request):
        """Return addon information."""
        addon = self._extract_addon(request)

        info = {
            ATTR_VERSION: self.addons.version_installed(addon),
            ATTR_CURRENT: self.addons.get_version(addon),
            ATTR_STATE: await self.addons.state_addon(addon),
            ATTR_BOOT: self.addons.get_boot(addon),
            ATTR_OPTIONS: self.addons.get_options(addon),
        }
        return info

    @api_process
    async def options(self, request):
        """Store user options for addon."""
        addon = self._extract_addon(request)
        schema = self.addons.get_schema(addon)

        options = await api_validate(schema, request)
        self.addons.set_options(addon, options)
        return True

    @api_process
    async def install(self, request):
        """Install addon."""
        body = await api_validate(SCHEMA_VERSION, request)
        addon = self._extract_addon(request, check_installed=False)
        version = body.get(
            ATTR_VERSION, self.addons.get_version(addon))

        return await asyncio.shield(
            self.addons.addon_install(addon, version), loop=self.loop)

    @api_process
    async def uninstall(self, request):
        """Uninstall addon."""
        addon = self._extract_addon(request)

        return await asyncio.shield(
            self.addons.addon_uninstall(addon), loop=self.loop)

    @api_process
    async def start(self, request):
        """Start addon."""
        addon = self._extract_addon(request)

        if await self.addons.state_addon(addon) == STATE_STARTED:
            raise RuntimeError("Addon is already running.")

        return await asyncio.shield(
            self.addons.addon_start(addon), loop=self.loop)

    @api_process
    async def stop(self, request):
        """Stop addon."""
        addon = self._extract_addon(request)

        if await self.addons.state_addon(addon) == STATE_STOPPED:
            raise RuntimeError("Addon is already stoped.")

        return await asyncio.shield(
            self.addons.addon_stop(addon), loop=self.loop)

    @api_process
    async def update(self, request):
        """Update addon."""
        body = await api_validate(SCHEMA_VERSION, request)
        addon = self._extract_addon(request)
        version = body.get(
            ATTR_VERSION, self.addons.get_version(addon))

        if version == self.addons.version_installed(addon):
            raise RuntimeError("Version is already in use.")

        return await asyncio.shield(
            self.addons.addon_update(addon, version), loop=self.loop)
