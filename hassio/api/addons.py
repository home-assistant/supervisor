"""Init file for HassIO homeassistant rest api."""
import asyncio
import logging

import voluptuous as vol
from voluptuous.humanize import humanize_error

from .util import (
    api_process, api_process_raw, api_validate, cluster_api_process)
from ..const import (
    ATTR_VERSION, ATTR_LAST_VERSION, ATTR_STATE, ATTR_BOOT, ATTR_OPTIONS,
    ATTR_URL, ATTR_DESCRIPTON, ATTR_DETACHED, ATTR_NAME, ATTR_REPOSITORY,
    ATTR_SLUG, ATTR_SOURCE, ATTR_REPOSITORIES, ATTR_ADDONS, ATTR_MAINTAINER,
    ATTR_BUILD, ATTR_AUTO_UPDATE, ATTR_NETWORK, ATTR_HOST_NETWORK, BOOT_AUTO,
    BOOT_MANUAL, ATTR_NODE)
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

    @api_process
    async def list(self, request):
        """Return all addons / repositories ."""
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
            ATTR_ADDONS: self.addons.get_addons_list_rest(),
            ATTR_REPOSITORIES: data_repositories,
        }

    @api_process
    def reload(self, request):
        """Reload all addons data."""
        return self.addons.reload()

    @api_process
    async def info(self, request, **kwargs):
        """Return addon information."""
        node = self.cluster.get_cluster_node(request)
        if node:
            return await node.addon_info(request)

        addon = self._extract_addon(request, check_installed=False)

        return {
            ATTR_NAME: addon.name,
            ATTR_DESCRIPTON: addon.description,
            ATTR_VERSION: addon.version_installed,
            ATTR_AUTO_UPDATE: addon.auto_update,
            ATTR_REPOSITORY: addon.repository,
            ATTR_LAST_VERSION: addon.last_version,
            ATTR_NODE: self.cluster.get_node_name(),
            ATTR_STATE: await addon.state(),
            ATTR_BOOT: addon.boot,
            ATTR_OPTIONS: addon.options,
            ATTR_URL: addon.url,
            ATTR_DETACHED: addon.is_detached,
            ATTR_BUILD: addon.need_build,
            ATTR_NETWORK: addon.ports,
            ATTR_HOST_NETWORK: addon.network_mode == 'host',
        }

    @cluster_api_process
    @api_process
    async def options(self, request, cluster_body=None):
        """Store user options for addon."""
        addon = self._extract_addon(request, check_installed=False)
        addon_schema = SCHEMA_OPTIONS.extend({
            vol.Optional(ATTR_OPTIONS): addon.schema,
        })
        body = await api_validate(addon_schema, request) \
            if cluster_body is None else addon_schema(cluster_body)
        node = self.cluster.get_cluster_node(request)
        if node:
            return await node.addon_options(request, body)

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

    @cluster_api_process
    @api_process
    async def install(self, request, cluster_body=None):
        """Install addon."""
        body = await api_validate(SCHEMA_VERSION, request) \
            if cluster_body is None else SCHEMA_VERSION(cluster_body)
        node = self.cluster.get_cluster_node(request)
        if node:
            return await node.addon_install(request, body, self.config)

        addon = self._extract_addon(request, check_installed=False)
        version = body.get(ATTR_VERSION)

        return await asyncio.shield(
            addon.install(version=version), loop=self.loop)

    @api_process
    async def uninstall(self, request):
        """Uninstall addon."""
        node = self.cluster.get_cluster_node(request)
        if node:
            return await node.addon_uninstall(request)
        addon = self._extract_addon(request)
        return await asyncio.shield(addon.uninstall(), loop=self.loop)

    @api_process
    async def start(self, request):
        """Start addon."""
        node = self.cluster.get_cluster_node(request)
        if node:
            return await node.addon_start(request)

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
        node = self.cluster.get_cluster_node(request)
        if node:
            return await node.addon_stop(request)
        addon = self._extract_addon(request)
        return await asyncio.shield(addon.stop(), loop=self.loop)

    @cluster_api_process
    @api_process
    async def update(self, request, cluster_body=None):
        """Update addon."""
        body = await api_validate(SCHEMA_VERSION, request) \
            if cluster_body is None else SCHEMA_VERSION(cluster_body)
        node = self.cluster.get_cluster_node(request)
        if node:
            return await node.addon_update(request, body)
        addon = self._extract_addon(request)
        version = body.get(ATTR_VERSION)

        return await asyncio.shield(
            addon.update(version=version), loop=self.loop)

    @api_process
    async def restart(self, request):
        """Restart addon."""
        node = self.cluster.get_cluster_node(request)
        if node:
            return await node.addon_restart(request)
        addon = self._extract_addon(request)
        return await asyncio.shield(addon.restart(), loop=self.loop)

    @api_process_raw
    async def logs(self, request):
        """Return logs from addon."""
        node = self.cluster.get_cluster_node(request)
        if node:
            return await node.addon_logs(request)

        addon = self._extract_addon(request)
        return await addon.logs()
