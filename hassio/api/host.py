"""Init file for HassIO host rest api."""
import asyncio
import logging

import voluptuous as vol

from .util import api_process_hostcontrol, api_process, api_validate, \
    cluster_api_process
from ..const import (
    ATTR_VERSION, ATTR_LAST_VERSION, ATTR_TYPE, ATTR_HOSTNAME, ATTR_FEATURES,
    ATTR_OS, ATTR_NODE)

_LOGGER = logging.getLogger(__name__)

SCHEMA_VERSION = vol.Schema({
    vol.Optional(ATTR_VERSION): vol.Coerce(str),
})


class APIHost(object):
    """Handle rest api for host functions."""

    def __init__(self, config, loop, host_control, cluster):
        """Initialize host rest api part."""
        self.config = config
        self.loop = loop
        self.host_control = host_control
        self.cluster = cluster

    @api_process
    async def info(self, request):
        """Return host information."""
        node = self.cluster.get_cluster_node(request)
        if node:
            return await node.host_info()

        return {
            ATTR_NODE: self.cluster.get_node_name(),
            ATTR_TYPE: self.host_control.type,
            ATTR_VERSION: self.host_control.version,
            ATTR_LAST_VERSION: self.host_control.last_version,
            ATTR_FEATURES: self.host_control.features,
            ATTR_HOSTNAME: self.host_control.hostname,
            ATTR_OS: self.host_control.os_info,
        }

    @api_process_hostcontrol
    async def reboot(self, request):
        """Reboot host."""
        node = self.cluster.get_cluster_node(request)
        if node:
            return await node.host_reboot()
        return self.host_control.reboot()

    @api_process_hostcontrol
    async def shutdown(self, request):
        """Poweroff host."""
        node = self.cluster.get_cluster_node(request)
        if node:
            return await node.host_shutdown()
        return self.host_control.shutdown()

    @cluster_api_process
    @api_process_hostcontrol
    async def update(self, request, cluster_body=None):
        """Update host OS."""
        body = await api_validate(SCHEMA_VERSION, request) \
            if cluster_body is None else SCHEMA_VERSION(cluster_body)
        node = self.cluster.get_cluster_node(request)
        if node:
            return await node.host_update(body)

        version = body.get(ATTR_VERSION, self.host_control.last_version)

        if version == self.host_control.version:
            raise RuntimeError("Version is already in use")

        return await asyncio.shield(
            self.host_control.update(version=version), loop=self.loop)
