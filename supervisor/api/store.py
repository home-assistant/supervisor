"""Init file for Supervisor Home Assistant RESTful API."""
import asyncio
from typing import Any, Awaitable, Dict, List

from aiohttp import web

from ..api.utils import api_process
from ..const import (
    ATTR_ADDONS,
    ATTR_ADVANCED,
    ATTR_AVAILABLE,
    ATTR_BUILD,
    ATTR_DESCRIPTON,
    ATTR_HOMEASSISTANT,
    ATTR_ICON,
    ATTR_INSTALLED,
    ATTR_LOGO,
    ATTR_MAINTAINER,
    ATTR_NAME,
    ATTR_REPOSITORIES,
    ATTR_REPOSITORY,
    ATTR_SLUG,
    ATTR_SOURCE,
    ATTR_STAGE,
    ATTR_UPDATE_AVAILABLE,
    ATTR_URL,
    ATTR_VERSION,
    ATTR_VERSION_LATEST,
)
from ..coresys import CoreSysAttributes
from ..exceptions import APIError
from ..store.addon import AddonStore
from ..store.repository import Repository


class APIStore(CoreSysAttributes):
    """Handle RESTful API for store functions."""

    def _extract_addon(self, request: web.Request) -> AddonStore:
        """Return add-on, throw an exception it it doesn't exist."""
        addon_slug: str = request.match_info.get("addon")
        addon_version: str = request.match_info.get("version", "latest")

        addon = self.sys_addons.store.get(addon_slug)
        if not addon:
            raise APIError(
                f"Addon {addon_slug} with version {addon_version} does not exist in the store"
            )

        return addon

    def _extract_repository(self, request: web.Request) -> Repository:
        """Return repository, throw an exception it it doesn't exist."""
        repository_slug: str = request.match_info.get("repository")

        repository = self.sys_store.get(repository_slug)
        if not repository:
            raise APIError(f"Repository {repository_slug} does not exist in the store")

        return repository

    def _generate_addon_information(self, addon: AddonStore) -> Dict[str, Any]:
        """Generate addon information."""
        return {
            ATTR_ADVANCED: addon.advanced,
            ATTR_AVAILABLE: addon.available,
            ATTR_BUILD: addon.need_build,
            ATTR_DESCRIPTON: addon.description,
            ATTR_HOMEASSISTANT: addon.homeassistant_version,
            ATTR_ICON: addon.with_icon,
            ATTR_INSTALLED: addon.is_installed,
            ATTR_LOGO: addon.with_logo,
            ATTR_NAME: addon.name,
            ATTR_REPOSITORY: addon.repository,
            ATTR_SLUG: addon.slug,
            ATTR_STAGE: addon.stage,
            ATTR_UPDATE_AVAILABLE: addon.need_update if addon.is_installed else False,
            ATTR_URL: addon.url,
            ATTR_VERSION_LATEST: addon.latest_version,
            ATTR_VERSION: addon.version if addon.is_installed else None,
        }

    def _generate_repository_information(
        self, repository: Repository
    ) -> Dict[str, Any]:
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
    async def store_info(self, request: web.Request) -> Dict[str, Any]:
        """Return store information."""
        return {
            ATTR_ADDONS: [
                self._generate_addon_information(self.sys_addons.store[addon])
                for addon in self.sys_addons.store
            ],
            ATTR_REPOSITORIES: [
                self._generate_repository_information(repository)
                for repository in self.sys_store.all
            ],
        }

    @api_process
    async def addons_list(self, request: web.Request) -> List[Dict[str, Any]]:
        """Return all store add-ons."""
        return [
            self._generate_addon_information(self.sys_addons.store[addon])
            for addon in self.sys_addons.store
        ]

    @api_process
    def addons_addon_install(self, request: web.Request) -> Awaitable[None]:
        """Install add-on."""
        addon = self._extract_addon(request)
        return asyncio.shield(addon.install())

    @api_process
    def addons_addon_update(self, request: web.Request) -> Awaitable[None]:
        """Update add-on."""
        addon = self._extract_addon(request)
        if not addon.is_installed:
            raise APIError(f"Addon {addon.slug} is not installed")
        return asyncio.shield(addon.update())

    @api_process
    async def addons_addon_info(self, request: web.Request) -> Dict[str, Any]:
        """Return add-on information."""
        addon: AddonStore = self._extract_addon(request)
        return self._generate_addon_information(addon)

    @api_process
    async def repositories_list(self, request: web.Request) -> List[Dict[str, Any]]:
        """Return all repositories."""
        return [
            self._generate_repository_information(repository)
            for repository in self.sys_store.all
        ]

    @api_process
    async def repositories_repository_info(
        self, request: web.Request
    ) -> Dict[str, Any]:
        """Return repository information."""
        repository: Repository = self._extract_repository(request)
        return self._generate_repository_information(repository)
