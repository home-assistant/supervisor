"""Init file for HassIO supervisor rest api."""
import asyncio
import logging

import voluptuous as vol

from .util import api_process, api_process_raw, api_validate
from ..addons.util import create_hash_index_list
from ..const import (
    ATTR_ADDONS, ATTR_VERSION, ATTR_LAST_VERSION, ATTR_BETA_CHANNEL,
    HASSIO_VERSION, ATTR_ADDONS_REPOSITORIES, ATTR_REPOSITORIES,
    ATTR_REPOSITORY, ATTR_DESCRIPTON, ATTR_NAME, ATTR_SLUG, ATTR_INSTALLED,
    ATTR_DETACHED, ATTR_SOURCE, ATTR_MAINTAINER, ATTR_URL)

_LOGGER = logging.getLogger(__name__)

SCHEMA_OPTIONS = vol.Schema({
    # pylint: disable=no-value-for-parameter
    vol.Optional(ATTR_BETA_CHANNEL): vol.Boolean(),
    vol.Optional(ATTR_ADDONS_REPOSITORIES): [vol.Url()],
})

SCHEMA_VERSION = vol.Schema({
    vol.Optional(ATTR_VERSION): vol.Coerce(str),
})


class APISupervisor(object):
    """Handle rest api for supervisor functions."""

    def __init__(self, config, loop, supervisor, addons, host_control):
        """Initialize supervisor rest api part."""
        self.config = config
        self.loop = loop
        self.supervisor = supervisor
        self.addons = addons
        self.host_control = host_control

    def _addons_list(self, only_installed=False):
        """Return a list of addons."""
        detached = self.addons.list_detached

        if only_installed:
            addons = self.addons.data_installed
        else:
            addons = self.addons.data_all

        data = []
        for addon, values in addons:
            i_version = self.addons.version_installed(addon)

            data.append({
                ATTR_NAME: values[ATTR_NAME],
                ATTR_SLUG: addon,
                ATTR_DESCRIPTON: values[ATTR_DESCRIPTON],
                ATTR_VERSION: values[ATTR_VERSION],
                ATTR_INSTALLED: i_version,
                ATTR_DETACHED: addon in detached,
                ATTR_REPOSITORY: values[ATTR_REPOSITORY],
            })

        return data

    def _repositories_list(self):
        """Return a list of addons repositories."""
        data = []
        list_id = create_hash_index_list(self.config.addons_repositories)

        for repository in self.addons.list_repositories:
            data.append({
                ATTR_SLUG: repository[ATTR_SLUG],
                ATTR_NAME: repository[ATTR_NAME],
                ATTR_SOURCE: list_id.get(repository[ATTR_SLUG]),
                ATTR_URL: repository.get(ATTR_URL),
                ATTR_MAINTAINER: repository.get(ATTR_MAINTAINER),
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

        if ATTR_ADDONS_REPOSITORIES in body:
            new = set(body[ATTR_ADDONS_REPOSITORIES])
            old = set(self.config.addons_repositories)

            # add new repositories
            tasks = [self.addons.add_git_repository(url) for url in
                     set(new - old)]
            if tasks:
                await asyncio.shield(
                    asyncio.wait(tasks, loop=self.loop), loop=self.loop)

            # remove old repositories
            for url in set(old - new):
                self.addons.drop_git_repository(url)

            # read repository
            self.addons.read_data_from_repositories()

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
            self.addons.reload(), self.config.fetch_update_infos(),
            self.host_control.load()
        ]
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
