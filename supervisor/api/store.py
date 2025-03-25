"""Init file for Supervisor Home Assistant RESTful API."""

import asyncio
from collections.abc import Awaitable
from pathlib import Path
from typing import Any, cast

from aiohttp import web
import voluptuous as vol

from ..addons.addon import Addon
from ..addons.manager import AnyAddon
from ..addons.utils import rating_security
from ..api.const import ATTR_SIGNED
from ..api.utils import api_process, api_process_raw, api_validate
from ..const import (
    ATTR_ADDONS,
    ATTR_ADVANCED,
    ATTR_APPARMOR,
    ATTR_ARCH,
    ATTR_AUTH_API,
    ATTR_AVAILABLE,
    ATTR_BACKUP,
    ATTR_BUILD,
    ATTR_DESCRIPTON,
    ATTR_DETACHED,
    ATTR_DOCKER_API,
    ATTR_DOCUMENTATION,
    ATTR_FULL_ACCESS,
    ATTR_HASSIO_API,
    ATTR_HASSIO_ROLE,
    ATTR_HOMEASSISTANT,
    ATTR_HOMEASSISTANT_API,
    ATTR_HOST_NETWORK,
    ATTR_HOST_PID,
    ATTR_ICON,
    ATTR_INGRESS,
    ATTR_INSTALLED,
    ATTR_LOGO,
    ATTR_LONG_DESCRIPTION,
    ATTR_MAINTAINER,
    ATTR_NAME,
    ATTR_RATING,
    ATTR_REPOSITORIES,
    ATTR_REPOSITORY,
    ATTR_SLUG,
    ATTR_SOURCE,
    ATTR_STAGE,
    ATTR_UPDATE_AVAILABLE,
    ATTR_URL,
    ATTR_VERSION,
    ATTR_VERSION_LATEST,
    REQUEST_FROM,
)
from ..coresys import CoreSysAttributes
from ..exceptions import APIError, APIForbidden, APINotFound
from ..store.addon import AddonStore
from ..store.repository import Repository
from ..store.validate import validate_repository
from .const import CONTENT_TYPE_PNG, CONTENT_TYPE_TEXT

SCHEMA_UPDATE = vol.Schema(
    {
        vol.Optional(ATTR_BACKUP): bool,
    }
)

SCHEMA_ADD_REPOSITORY = vol.Schema(
    {vol.Required(ATTR_REPOSITORY): vol.All(str, validate_repository)}
)


def _read_static_text_file(path: Path) -> Any:
    """Read in a static text file asset for API output.

    Must be run in executor.
    """
    with path.open("r", errors="replace") as asset:
        return asset.read()


def _read_static_binary_file(path: Path) -> Any:
    """Read in a static binary file asset for API output.

    Must be run in executor.
    """
    with path.open("rb") as asset:
        return asset.read()


class APIStore(CoreSysAttributes):
    """Handle RESTful API for store functions."""

    def _extract_addon(self, request: web.Request, installed=False) -> AnyAddon:
        """Return add-on, throw an exception it it doesn't exist."""
        addon_slug: str = request.match_info["addon"]

        if not (addon := self.sys_addons.get(addon_slug)):
            raise APINotFound(f"Addon {addon_slug} does not exist")

        if installed and not addon.is_installed:
            raise APIError(f"Addon {addon_slug} is not installed")

        if not installed and addon.is_installed:
            addon = cast(Addon, addon)
            if not addon.addon_store:
                raise APINotFound(f"Addon {addon_slug} does not exist in the store")
            return addon.addon_store

        return addon

    def _extract_repository(self, request: web.Request) -> Repository:
        """Return repository, throw an exception it it doesn't exist."""
        repository_slug: str = request.match_info["repository"]

        if repository_slug not in self.sys_store.repositories:
            raise APINotFound(
                f"Repository {repository_slug} does not exist in the store"
            )

        return self.sys_store.get(repository_slug)

    async def _generate_addon_information(
        self, addon: AddonStore, extended: bool = False
    ) -> dict[str, Any]:
        """Generate addon information."""

        installed = (
            cast(Addon, self.sys_addons.get(addon.slug, local_only=True))
            if addon.is_installed
            else None
        )

        data = {
            ATTR_ADVANCED: addon.advanced,
            ATTR_ARCH: addon.supported_arch,
            ATTR_AVAILABLE: addon.available,
            ATTR_BUILD: addon.need_build,
            ATTR_DESCRIPTON: addon.description,
            ATTR_DOCUMENTATION: addon.with_documentation,
            ATTR_HOMEASSISTANT: addon.homeassistant_version,
            ATTR_ICON: addon.with_icon,
            ATTR_INSTALLED: addon.is_installed,
            ATTR_LOGO: addon.with_logo,
            ATTR_NAME: addon.name,
            ATTR_REPOSITORY: addon.repository,
            ATTR_SLUG: addon.slug,
            ATTR_STAGE: addon.stage,
            ATTR_UPDATE_AVAILABLE: installed.need_update if installed else False,
            ATTR_URL: addon.url,
            ATTR_VERSION_LATEST: addon.latest_version,
            ATTR_VERSION: installed.version if installed else None,
        }
        if extended:
            data.update(
                {
                    ATTR_APPARMOR: addon.apparmor,
                    ATTR_AUTH_API: addon.access_auth_api,
                    ATTR_DETACHED: addon.is_detached,
                    ATTR_DOCKER_API: addon.access_docker_api,
                    ATTR_FULL_ACCESS: addon.with_full_access,
                    ATTR_HASSIO_API: addon.access_hassio_api,
                    ATTR_HASSIO_ROLE: addon.hassio_role,
                    ATTR_HOMEASSISTANT_API: addon.access_homeassistant_api,
                    ATTR_HOST_NETWORK: addon.host_network,
                    ATTR_HOST_PID: addon.host_pid,
                    ATTR_INGRESS: addon.with_ingress,
                    ATTR_LONG_DESCRIPTION: await addon.long_description(),
                    ATTR_RATING: rating_security(addon),
                    ATTR_SIGNED: addon.signed,
                }
            )

        return data

    def _generate_repository_information(
        self, repository: Repository
    ) -> dict[str, Any]:
        """Generate repository information."""
        return {
            ATTR_SLUG: repository.slug,
            ATTR_NAME: repository.name,
            ATTR_SOURCE: repository.source,
            ATTR_URL: repository.url,
            ATTR_MAINTAINER: repository.maintainer,
        }

    @api_process
    async def reload(self, request: web.Request) -> None:
        """Reload all add-on data from store."""
        await asyncio.shield(self.sys_store.reload())

    @api_process
    async def store_info(self, request: web.Request) -> dict[str, Any]:
        """Return store information."""
        return {
            ATTR_ADDONS: await asyncio.gather(
                *[
                    self._generate_addon_information(self.sys_addons.store[addon])
                    for addon in self.sys_addons.store
                ]
            ),
            ATTR_REPOSITORIES: [
                self._generate_repository_information(repository)
                for repository in self.sys_store.all
            ],
        }

    @api_process
    async def addons_list(self, request: web.Request) -> dict[str, Any]:
        """Return all store add-ons."""
        return {
            ATTR_ADDONS: await asyncio.gather(
                *[
                    self._generate_addon_information(self.sys_addons.store[addon])
                    for addon in self.sys_addons.store
                ]
            )
        }

    @api_process
    def addons_addon_install(self, request: web.Request) -> Awaitable[None]:
        """Install add-on."""
        addon = self._extract_addon(request)
        return asyncio.shield(self.sys_addons.install(addon.slug))

    @api_process
    async def addons_addon_update(self, request: web.Request) -> None:
        """Update add-on."""
        addon = self._extract_addon(request, installed=True)
        if addon == request.get(REQUEST_FROM):
            raise APIForbidden(f"Add-on {addon.slug} can't update itself!")

        body = await api_validate(SCHEMA_UPDATE, request)

        if start_task := await asyncio.shield(
            self.sys_addons.update(addon.slug, backup=body.get(ATTR_BACKUP))
        ):
            await start_task

    @api_process
    async def addons_addon_info(self, request: web.Request) -> dict[str, Any]:
        """Return add-on information."""
        return await self.addons_addon_info_wrapped(request)

    # Used by legacy routing for addons/{addon}/info, can be refactored out when that is removed (1/2023)
    async def addons_addon_info_wrapped(self, request: web.Request) -> dict[str, Any]:
        """Return add-on information directly (not api)."""
        addon = cast(AddonStore, self._extract_addon(request))
        return await self._generate_addon_information(addon, True)

    @api_process_raw(CONTENT_TYPE_PNG)
    async def addons_addon_icon(self, request: web.Request) -> bytes:
        """Return icon from add-on."""
        addon = self._extract_addon(request)
        if not addon.with_icon:
            raise APIError(f"No icon found for add-on {addon.slug}!")

        return await self.sys_run_in_executor(_read_static_binary_file, addon.path_icon)

    @api_process_raw(CONTENT_TYPE_PNG)
    async def addons_addon_logo(self, request: web.Request) -> bytes:
        """Return logo from add-on."""
        addon = self._extract_addon(request)
        if not addon.with_logo:
            raise APIError(f"No logo found for add-on {addon.slug}!")

        return await self.sys_run_in_executor(_read_static_binary_file, addon.path_logo)

    @api_process_raw(CONTENT_TYPE_TEXT)
    async def addons_addon_changelog(self, request: web.Request) -> str:
        """Return changelog from add-on."""
        # Frontend can't handle error response here, need to return 200 and error as text for now
        try:
            addon = self._extract_addon(request)
        except APIError as err:
            return str(err)

        if not addon.with_changelog:
            return f"No changelog found for add-on {addon.slug}!"

        return await self.sys_run_in_executor(
            _read_static_text_file, addon.path_changelog
        )

    @api_process_raw(CONTENT_TYPE_TEXT)
    async def addons_addon_documentation(self, request: web.Request) -> str:
        """Return documentation from add-on."""
        # Frontend can't handle error response here, need to return 200 and error as text for now
        try:
            addon = self._extract_addon(request)
        except APIError as err:
            return str(err)

        if not addon.with_documentation:
            return f"No documentation found for add-on {addon.slug}!"

        return await self.sys_run_in_executor(
            _read_static_text_file, addon.path_documentation
        )

    @api_process
    async def repositories_list(self, request: web.Request) -> list[dict[str, Any]]:
        """Return all repositories."""
        return [
            self._generate_repository_information(repository)
            for repository in self.sys_store.all
        ]

    @api_process
    async def repositories_repository_info(
        self, request: web.Request
    ) -> dict[str, Any]:
        """Return repository information."""
        repository: Repository = self._extract_repository(request)
        return self._generate_repository_information(repository)

    @api_process
    async def add_repository(self, request: web.Request):
        """Add repository to the store."""
        body = await api_validate(SCHEMA_ADD_REPOSITORY, request)
        await asyncio.shield(self.sys_store.add_repository(body[ATTR_REPOSITORY]))

    @api_process
    async def remove_repository(self, request: web.Request):
        """Remove repository from the store."""
        repository: Repository = self._extract_repository(request)
        await asyncio.shield(self.sys_store.remove_repository(repository))
