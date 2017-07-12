"""Init file for HassIO homeassistant rest api."""
import asyncio
import logging

import voluptuous as vol
from voluptuous.humanize import humanize_error

from .util import api_process, api_process_raw, api_validate
from ..const import (
    ATTR_VERSION, ATTR_LAST_VERSION, ATTR_STATE, ATTR_BOOT, ATTR_OPTIONS,
    ATTR_URL, ATTR_DESCRIPTON, ATTR_DETACHED, ATTR_NAME, ATTR_REPOSITORY,
    ATTR_SLUG,
    ATTR_SOURCE, ATTR_REPOSITORIES, ATTR_ADDONS, ATTR_ARCH, ATTR_MAINTAINER,
    ATTR_INSTALLED, ATTR_BUILD, ATTR_AUTO_UPDATE, ATTR_NETWORK,
    ATTR_HOST_NETWORK,
    BOOT_AUTO, BOOT_MANUAL, CLUSTER_NODE_MASTER)
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

    def __init__(self, config, loop, addons, cluster):
        """Initialize homeassistant rest api part."""
        self.config = config
        self.loop = loop
        self.addons = addons
        self.cluster = cluster

    def _extract_addon(self, request, check_installed=True):
        """Return addon and if not exists trow a exception."""
        addon = self.addons.get(request.match_info.get('addon'))
        if not addon:
            raise RuntimeError("Addon not exists")

        if check_installed and not addon.is_installed:
            raise RuntimeError("Addon is not installed")

        return addon

    def _get_cluster_node(self, request):
        """Return cluster node if it's known and active."""
        node_slug = request.match_info.get('node')
        if node_slug is None or node_slug == CLUSTER_NODE_MASTER:
            return None
        node = self.cluster.get_node(node_slug)
        if node is None:
            raise RuntimeError("Node is unknown")
        if node.is_active is False:
            raise RuntimeError("Node is not active")
        return node

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
        node = self._get_cluster_node(request)
        if node is None:
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
            }

        return await node.addon_info(request)

    @api_process
    async def options(self, request):
        """Store user options for addon."""
        addon = self._extract_addon(request, check_installed=False)
        addon_schema = SCHEMA_OPTIONS.extend({
            vol.Optional(ATTR_OPTIONS): addon.schema,
        })
        body = await api_validate(addon_schema, request)
        node = self._get_cluster_node(request)
        if node is None:
            if not addon.is_installed:
                raise RuntimeError("Addon is not installed")

            if ATTR_OPTIONS in body:
                addon.options = body[ATTR_OPTIONS]
            if ATTR_BOOT in body:
                addon.boot = body[ATTR_BOOT]
            if ATTR_AUTO_UPDATE in body:
                addon.auto_update = body[ATTR_AUTO_UPDATE]
            if ATTR_NETWORK in body:
                addon.ports = body[ATTR_NETWORK]
            return True

        return await node.addon_options(request, body)

    @api_process
    async def install(self, request):
        """Install addon."""
        body = await api_validate(SCHEMA_VERSION, request)
        node = self._get_cluster_node(request)
        if node is None:
            return await self.install_plain(request, body)

        return await node.addon_install(request, body, self.config)

    async def install_plain(self, request, body):
        """Installing addon from pre-validated request."""
        addon = self._extract_addon(request, check_installed=False)
        version = body[ATTR_VERSION]

        return await asyncio.shield(
            addon.install(version=version), loop=self.loop)

    @api_process
    async def uninstall(self, request):
        """Uninstall addon."""
        node = self._get_cluster_node(request)
        if node is None:
            addon = self._extract_addon(request)
            return await asyncio.shield(addon.uninstall(), loop=self.loop)

        return await node.addon_uninstall(request)

    @api_process
    async def start(self, request):
        """Start addon."""
        node = self._get_cluster_node(request)
        if node is None:
            addon = self._extract_addon(request)

            # check options
            options = addon.options
            try:
                addon.schema(options)
            except vol.Invalid as ex:
                raise RuntimeError(humanize_error(options, ex)) from None

            return await asyncio.shield(addon.start(), loop=self.loop)

        return await node.addon_start(request)

    @api_process
    async def stop(self, request):
        """Stop addon."""
        node = self._get_cluster_node(request)
        if node is None:
            addon = self._extract_addon(request)
            return await asyncio.shield(addon.stop(), loop=self.loop)

        return await node.addon_stop(request)

    @api_process
    async def update(self, request):
        """Update addon."""
        body = await api_validate(SCHEMA_VERSION, request)
        node = self._get_cluster_node(request)
        if node is None:
            addon = self._extract_addon(request)
            version = body.get(ATTR_VERSION)

            return await asyncio.shield(
                addon.update(version=version), loop=self.loop)

        return await node.addon_update(request, body)

    @api_process
    async def restart(self, request):
        """Restart addon."""
        node = self._get_cluster_node(request)
        if node is None:
            addon = self._extract_addon(request)
            return await asyncio.shield(addon.restart(), loop=self.loop)

        return await node.addon_restart(request)

    @api_process_raw
    async def logs(self, request):
        """Return logs from addon."""
        node = self._get_cluster_node(request)
        if node is None:
            return await self.logs_plain(request)

        return await node.addon_logs(request)

    async def logs_plain(self, request):
        """Return plain logs without wrappers."""
        addon = self._extract_addon(request)
        return await addon.logs()
