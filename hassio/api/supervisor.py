"""Init file for HassIO supervisor rest api."""
import asyncio
import logging

import voluptuous as vol

from .util import api_process, api_process_raw, api_validate
from ..const import (
    ATTR_ADDONS, ATTR_VERSION, ATTR_LAST_VERSION, ATTR_BETA_CHANNEL,
    HASSIO_VERSION, ATTR_ADDONS_REPOSITORIES, ATTR_REPOSITORIES,
    ATTR_REPOSITORY, ATTR_DESCRIPTON, ATTR_NAME, ATTR_SLUG, ATTR_INSTALLED,
    ATTR_DETACHED, ATTR_SOURCE, ATTR_MAINTAINER, ATTR_URL, ATTR_ARCH,
    ATTR_BUILD, ATTR_TIMEZONE)
from ..tools import validate_timezone

_LOGGER = logging.getLogger(__name__)

SCHEMA_OPTIONS = vol.Schema({
    # pylint: disable=no-value-for-parameter
    vol.Optional(ATTR_BETA_CHANNEL): vol.Boolean(),
    vol.Optional(ATTR_ADDONS_REPOSITORIES): [vol.Url()],
    vol.Optional(ATTR_TIMEZONE): validate_timezone,
})

SCHEMA_VERSION = vol.Schema({
    vol.Optional(ATTR_VERSION): vol.Coerce(str),
})


class APISupervisor(object):
    """Handle rest api for supervisor functions."""

    def __init__(self, config, loop, supervisor, snapshots, addons,
                 host_control, websession):
        """Initialize supervisor rest api part."""
        self.config = config
        self.loop = loop
        self.supervisor = supervisor
        self.addons = addons
        self.snapshots = snapshots
        self.host_control = host_control
        self.websession = websession

    def _addons_list(self, only_installed=False):
        """Return a list of addons."""
        data = []
        for addon in self.addons.list_addons:
            if only_installed and not addon.is_installed:
                continue

            data.append({
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

        return data

    def _repositories_list(self):
        """Return a list of addons repositories."""
        data = []
        for repository in self.addons.list_repositories:
            data.append({
                ATTR_SLUG: repository.slug,
                ATTR_NAME: repository.name,
                ATTR_SOURCE: repository.source,
                ATTR_URL: repository.url,
                ATTR_MAINTAINER: repository.maintainer,
            })

        return data

    @api_process
    async def ping(self, request):
        """Return ok for signal that the api is ready."""
        return True

    @api_process
    async def info(self, request):
        """Return host information."""
        return {
            ATTR_VERSION: HASSIO_VERSION,
            ATTR_LAST_VERSION: self.config.last_hassio,
            ATTR_BETA_CHANNEL: self.config.upstream_beta,
            ATTR_ARCH: self.config.arch,
            ATTR_TIMEZONE: self.config.timezone,
            ATTR_ADDONS: self._addons_list(only_installed=True),
            ATTR_ADDONS_REPOSITORIES: self.config.addons_repositories,
        }

    @api_process
    async def available_addons(self, request):
        """Return information for all available addons."""
        return {
            ATTR_ADDONS: self._addons_list(),
            ATTR_REPOSITORIES: self._repositories_list(),
        }

    @api_process
    async def options(self, request):
        """Set supervisor options."""
        body = await api_validate(SCHEMA_OPTIONS, request)

        if ATTR_BETA_CHANNEL in body:
            self.config.upstream_beta = body[ATTR_BETA_CHANNEL]

        if ATTR_TIMEZONE in body:
            self.config.timezone = body[ATTR_TIMEZONE]

        if ATTR_ADDONS_REPOSITORIES in body:
            new = set(body[ATTR_ADDONS_REPOSITORIES])
            await asyncio.shield(self.addons.load_repositories(new))

        return True

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
        tasks = [
            self.addons.reload(),
            self.snapshots.reload(),
            self.config.fetch_update_infos(self.websession),
            self.host_control.load()
        ]
        results, _ = await asyncio.shield(
            asyncio.wait(tasks, loop=self.loop), loop=self.loop)

        for result in results:
            if result.exception() is not None:
                raise RuntimeError("Some reload task fails!")

        return True

    @api_process_raw()
    def logs(self, request):
        """Return supervisor docker logs.

        Return a coroutine.
        """
        return self.supervisor.logs()
