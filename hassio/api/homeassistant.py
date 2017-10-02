"""Init file for HassIO homeassistant rest api."""
import asyncio
import logging

import aiohttp
from aiohttp import web
from aiohttp.web_exceptions import HTTPBadGateway
from aiohttp.hdrs import CONTENT_TYPE
import async_timeout
import voluptuous as vol

from .util import api_process, api_process_raw, api_validate
from ..const import (
    ATTR_VERSION, ATTR_LAST_VERSION, ATTR_DEVICES, ATTR_IMAGE, ATTR_CUSTOM,
    ATTR_BOOT, ATTR_PORT, ATTR_PASSWORD, ATTR_SSL, CONTENT_TYPE_BINARY,
    HEADER_HA_ACCESS)
from ..validate import HASS_DEVICES, NETWORK_PORT

_LOGGER = logging.getLogger(__name__)


# pylint: disable=no-value-for-parameter
SCHEMA_OPTIONS = vol.Schema({
    vol.Optional(ATTR_DEVICES): HASS_DEVICES,
    vol.Optional(ATTR_BOOT): vol.Boolean(),
    vol.Inclusive(ATTR_IMAGE, 'custom_hass'): vol.Any(None, vol.Coerce(str)),
    vol.Inclusive(ATTR_LAST_VERSION, 'custom_hass'):
        vol.Any(None, vol.Coerce(str)),
    vol.Optional(ATTR_PORT): NETWORK_PORT,
    vol.Optional(ATTR_PASSWORD): vol.Any(None, vol.Coerce(str)),
    vol.Optional(ATTR_SSL): vol.Boolean(),
})

SCHEMA_VERSION = vol.Schema({
    vol.Optional(ATTR_VERSION): vol.Coerce(str),
})


class APIHomeAssistant(object):
    """Handle rest api for homeassistant functions."""

    def __init__(self, config, loop, homeassistant):
        """Initialize homeassistant rest api part."""
        self.config = config
        self.loop = loop
        self.homeassistant = homeassistant

    async def homeassistant_proxy(self, path, request):
        """Return a client request with proxy origin for Home-Assistant."""
        url = "{}/api/{}".format(self.homeassistant.api_url, path)

        try:
            data = None
            headers = {}
            method = getattr(
                self.homeassistant.websession, request.method.lower())

            # read data
            with async_timeout.timeout(10, loop=self.loop):
                data = await request.read()

            if data:
                headers.update({CONTENT_TYPE: request.content_type})

            # need api password?
            if self.homeassistant.api_password:
                headers = {HEADER_HA_ACCESS: self.homeassistant.api_password}

            # reset headers
            if not headers:
                headers = None

            client = await method(
                url, data=data, headers=headers, timeout=300
            )

            return client

        except aiohttp.ClientError as err:
            _LOGGER.error("Client error on api %s request %s.", path, err)

        except asyncio.TimeoutError:
            _LOGGER.error("Client timeout error on api request %s.", path)

        raise HTTPBadGateway()

    @api_process
    async def info(self, request):
        """Return host information."""
        return {
            ATTR_VERSION: self.homeassistant.version,
            ATTR_LAST_VERSION: self.homeassistant.last_version,
            ATTR_IMAGE: self.homeassistant.image,
            ATTR_DEVICES: self.homeassistant.devices,
            ATTR_CUSTOM: self.homeassistant.is_custom_image,
            ATTR_BOOT: self.homeassistant.boot,
            ATTR_PORT: self.homeassistant.api_port,
            ATTR_SSL: self.homeassistant.api_ssl,
        }

    @api_process
    async def options(self, request):
        """Set homeassistant options."""
        body = await api_validate(SCHEMA_OPTIONS, request)

        if ATTR_DEVICES in body:
            self.homeassistant.devices = body[ATTR_DEVICES]

        if ATTR_IMAGE in body:
            self.homeassistant.set_custom(
                body[ATTR_IMAGE], body[ATTR_LAST_VERSION])

        if ATTR_BOOT in body:
            self.homeassistant.boot = body[ATTR_BOOT]

        if ATTR_PORT in body:
            self.homeassistant.api_port = body[ATTR_PORT]

        if ATTR_PASSWORD in body:
            self.homeassistant.api_password = body[ATTR_PASSWORD]

        if ATTR_SSL in body:
            self.homeassistant.api_ssl = body[ATTR_SSL]

        return True

    @api_process
    async def update(self, request):
        """Update homeassistant."""
        body = await api_validate(SCHEMA_VERSION, request)
        version = body.get(ATTR_VERSION, self.homeassistant.last_version)

        if version == self.homeassistant.version:
            raise RuntimeError("Version {} is already in use".format(version))

        return await asyncio.shield(
            self.homeassistant.update(version), loop=self.loop)

    @api_process
    def stop(self, request):
        """Stop homeassistant."""
        return asyncio.shield(self.homeassistant.stop(), loop=self.loop)

    @api_process
    def start(self, request):
        """Start homeassistant."""
        return asyncio.shield(self.homeassistant.run(), loop=self.loop)

    @api_process
    def restart(self, request):
        """Restart homeassistant."""
        return asyncio.shield(self.homeassistant.restart(), loop=self.loop)

    @api_process_raw(CONTENT_TYPE_BINARY)
    def logs(self, request):
        """Return homeassistant docker logs."""
        return self.homeassistant.logs()

    @api_process
    async def check(self, request):
        """Check config of homeassistant."""
        code, message = await self.homeassistant.check_config()
        if not code:
            raise RuntimeError(message)

        return True

    async def api(self, request):
        """Proxy API request to Home-Assistant."""
        path = request.match_info.get('path')

        client = await self.homeassistant_proxy(path, request)
        return web.Response(
            body=await client.read(),
            status=client.status,
            content_type=client.content_type
        )
