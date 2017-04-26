"""Init file for HassIO supervisor rest api."""
import asyncio
import logging

import voluptuous as vol

from .util import api_process, api_process_raw, api_validate
from ..const import (
    ATTR_ADDONS, ATTR_VERSION, ATTR_LAST_VERSION, ATTR_BETA_CHANNEL,
    HASSIO_VERSION)

_LOGGER = logging.getLogger(__name__)

SCHEMA_OPTIONS = vol.Schema({
    # pylint: disable=no-value-for-parameter
    vol.Optional(ATTR_BETA_CHANNEL): vol.Boolean(),
})

SCHEMA_VERSION = vol.Schema({
    vol.Optional(ATTR_VERSION): vol.Coerce(str),
})


class APISupervisor(object):
    """Handle rest api for supervisor functions."""

    def __init__(self, config, loop, supervisor, addons):
        """Initialize supervisor rest api part."""
        self.config = config
        self.loop = loop
        self.supervisor = supervisor
        self.addons = addons

    @api_process
    async def ping(self, request):
        """Return ok for signal that the api is ready."""
        return True

    @api_process
    async def info(self, request):
        """Return host information."""
        info = {
            ATTR_VERSION: HASSIO_VERSION,
            ATTR_LAST_VERSION: self.config.last_hassio,
            ATTR_BETA_CHANNEL: self.config.upstream_beta,
            ATTR_ADDONS: self.addons.list,
        }
        return info

    @api_process
    async def options(self, request):
        """Set supervisor options."""
        body = await api_validate(SCHEMA_OPTIONS, request)

        if ATTR_BETA_CHANNEL in body:
            self.config.upstream_beta = body[ATTR_BETA_CHANNEL]

        return self.config.save()

    @api_process
    async def update(self, request):
        """Update supervisor OS."""
        body = await api_validate(SCHEMA_VERSION, request)
        version = body.get(ATTR_VERSION, self.config.last_hassio)

        if version == self.supervisor.version:
            raise RuntimeError("Version is already in use")

        return await asyncio.shield(
            self.supervisor.update(version), loop=self.loop)

    @api_process
    async def reload(self, request):
        """Reload addons, config ect."""
        tasks = [self.addons.reload(), self.config.fetch_update_infos()]
        results, _ = await asyncio.shield(
            asyncio.wait(tasks, loop=self.loop), loop=self.loop)

        for result in results:
            if result.exception() is not None:
                raise RuntimeError("Some reload task fails!")

        return True

    @api_process_raw
    def logs(self, request):
        """Return supervisor docker logs.

        Return a coroutine.
        """
        return self.supervisor.logs()
