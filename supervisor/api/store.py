"""Init file for Supervisor Home Assistant RESTful API."""

import asyncio
from pathlib import Path
from typing import Any, cast

from aiohttp import web
import voluptuous as vol

from ..addons.addon import App
from ..addons.manager import AnyApp
from ..addons.utils import rating_security
from ..api.const import ATTR_SIGNED
from ..api.utils import api_process, api_process_raw, api_validate
from ..const import (
    ATTR_ADDONS,
    ATTR_ADVANCED,
    ATTR_APPARMOR,
    ATTR_APPS,
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
    ATTR_JOB_ID,
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
from ..exceptions import APIError, APIForbidden, APINotFound, StoreAppNotFoundError
from ..resolution.const import ContextType, SuggestionType
from ..store.addon import AppStore
from ..store.repository import Repository
from ..store.validate import validate_repository
from .const import ATTR_BACKGROUND, CONTENT_TYPE_PNG, CONTENT_TYPE_TEXT
from .utils import background_task

SCHEMA_UPDATE = vol.Schema(
    {
        vol.Optional(ATTR_BACKUP): bool,
        vol.Optional(ATTR_BACKGROUND, default=False): bool,
    }
)

SCHEMA_ADD_REPOSITORY = vol.Schema(
    {vol.Required(ATTR_REPOSITORY): vol.All(str, validate_repository)}
)

SCHEMA_INSTALL = vol.Schema(
    {
        vol.Optional(ATTR_BACKGROUND, default=False): bool,
    }
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

    def _extract_app(self, request: web.Request, installed=False) -> AnyApp:
        """Return app, throw an exception it it doesn't exist."""
        app_slug: str = request.match_info["app"]

        if not (app := self.sys_apps.get(app_slug)):
            raise StoreAppNotFoundError(app=app_slug)

        if installed and not app.is_installed:
            raise APIError(f"App {app_slug} is not installed")

        if not installed and app.is_installed:
            app = cast(App, app)
            if not app.app_store:
                raise StoreAppNotFoundError(app=app_slug)
            return app.app_store

        return app

    def _extract_repository(self, request: web.Request) -> Repository:
        """Return repository, throw an exception it it doesn't exist."""
        repository_slug: str = request.match_info["repository"]

        if repository_slug not in self.sys_store.repositories:
            raise APINotFound(
                f"Repository {repository_slug} does not exist in the store"
            )

        return self.sys_store.get(repository_slug)

    async def _generate_app_information(
        self, app: AppStore, extended: bool = False
    ) -> dict[str, Any]:
        """Generate app information."""

        installed = self.sys_apps.get_local_only(app.slug) if app.is_installed else None

        data = {
            ATTR_ADVANCED: app.advanced,
            ATTR_ARCH: app.supported_arch,
            ATTR_AVAILABLE: app.available,
            ATTR_BUILD: app.need_build,
            ATTR_DESCRIPTON: app.description,
            ATTR_DOCUMENTATION: app.with_documentation,
            ATTR_HOMEASSISTANT: app.homeassistant_version,
            ATTR_ICON: app.with_icon,
            ATTR_INSTALLED: app.is_installed,
            ATTR_LOGO: app.with_logo,
            ATTR_NAME: app.name,
            ATTR_REPOSITORY: app.repository,
            ATTR_SLUG: app.slug,
            ATTR_STAGE: app.stage,
            ATTR_UPDATE_AVAILABLE: installed.need_update if installed else False,
            ATTR_URL: app.url,
            ATTR_VERSION_LATEST: app.latest_version,
            ATTR_VERSION: installed.version if installed else None,
        }
        if extended:
            data.update(
                {
                    ATTR_APPARMOR: app.apparmor,
                    ATTR_AUTH_API: app.access_auth_api,
                    ATTR_DETACHED: app.is_detached,
                    ATTR_DOCKER_API: app.access_docker_api,
                    ATTR_FULL_ACCESS: app.with_full_access,
                    ATTR_HASSIO_API: app.access_hassio_api,
                    ATTR_HASSIO_ROLE: app.hassio_role,
                    ATTR_HOMEASSISTANT_API: app.access_homeassistant_api,
                    ATTR_HOST_NETWORK: app.host_network,
                    ATTR_HOST_PID: app.host_pid,
                    ATTR_INGRESS: app.with_ingress,
                    ATTR_LONG_DESCRIPTION: await app.long_description(),
                    ATTR_RATING: rating_security(app),
                    ATTR_SIGNED: app.signed,
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

    async def _all_store_apps_info(self) -> list[dict[str, Any]]:
        """Return gathered info for all apps in the store."""
        return list(
            await asyncio.gather(
                *[
                    self._generate_app_information(self.sys_apps.store[app])
                    for app in self.sys_apps.store
                ]
            )
        )

    @api_process
    async def reload(self, request: web.Request) -> None:
        """Reload all app data from store."""
        await asyncio.shield(self.sys_store.reload())

    @api_process
    async def store_info(self, request: web.Request) -> dict[str, Any]:
        """Return store information (v2: uses "apps" key)."""
        return {
            ATTR_APPS: await self._all_store_apps_info(),
            ATTR_REPOSITORIES: [
                self._generate_repository_information(repository)
                for repository in self.sys_store.all
            ],
        }

    @api_process
    async def store_info_v1(self, request: web.Request) -> dict[str, Any]:
        """Return store information (v1: uses "addons" key)."""
        return {
            ATTR_ADDONS: await self._all_store_apps_info(),
            ATTR_REPOSITORIES: [
                self._generate_repository_information(repository)
                for repository in self.sys_store.all
            ],
        }

    @api_process
    async def apps_list(self, request: web.Request) -> dict[str, Any]:
        """Return all store apps (v2: uses "apps" key)."""
        return {ATTR_APPS: await self._all_store_apps_info()}

    @api_process
    async def apps_list_v1(self, request: web.Request) -> dict[str, Any]:
        """Return all store apps (v1: uses "addons" key)."""
        return {ATTR_ADDONS: await self._all_store_apps_info()}

    @api_process
    async def apps_app_install(self, request: web.Request) -> dict[str, str] | None:
        """Install app."""
        app = self._extract_app(request)
        body = await api_validate(SCHEMA_INSTALL, request)

        background = body[ATTR_BACKGROUND]

        install_task, job_id = await background_task(
            self, self.sys_apps.install, app.slug
        )

        if background and not install_task.done():
            return {ATTR_JOB_ID: job_id}

        return await install_task

    @api_process
    async def apps_app_update(self, request: web.Request) -> dict[str, str] | None:
        """Update app."""
        app = self._extract_app(request, installed=True)
        if app == request.get(REQUEST_FROM):
            raise APIForbidden(f"App {app.slug} can't update itself!")

        body = await api_validate(SCHEMA_UPDATE, request)
        background = body[ATTR_BACKGROUND]

        update_task, job_id = await background_task(
            self,
            self.sys_apps.update,
            app.slug,
            backup=body.get(ATTR_BACKUP),
        )

        if background and not update_task.done():
            return {ATTR_JOB_ID: job_id}

        if start_task := await update_task:
            await start_task
        return None

    @api_process
    async def apps_app_info(self, request: web.Request) -> dict[str, Any]:
        """Return app information."""
        return await self.apps_app_info_wrapped(request)

    # Used by legacy routing for apps/{app}/info, can be refactored out when that is removed (1/2023)
    async def apps_app_info_wrapped(self, request: web.Request) -> dict[str, Any]:
        """Return app information directly (not api)."""
        app = cast(AppStore, self._extract_app(request))
        return await self._generate_app_information(app, True)

    @api_process_raw(CONTENT_TYPE_PNG)
    async def apps_app_icon(self, request: web.Request) -> bytes:
        """Return icon from app."""
        app = self._extract_app(request)
        if not app.with_icon:
            raise APIError(f"No icon found for app {app.slug}!")

        return await self.sys_run_in_executor(_read_static_binary_file, app.path_icon)

    @api_process_raw(CONTENT_TYPE_PNG)
    async def apps_app_logo(self, request: web.Request) -> bytes:
        """Return logo from app."""
        app = self._extract_app(request)
        if not app.with_logo:
            raise APIError(f"No logo found for app {app.slug}!")

        return await self.sys_run_in_executor(_read_static_binary_file, app.path_logo)

    @api_process_raw(CONTENT_TYPE_TEXT)
    async def apps_app_changelog(self, request: web.Request) -> str:
        """Return changelog from app."""
        # Frontend can't handle error response here, need to return 200 and error as text for now
        try:
            app = self._extract_app(request)
        except APIError as err:
            return str(err)

        if not app.with_changelog:
            return f"No changelog found for app {app.slug}!"

        return await self.sys_run_in_executor(
            _read_static_text_file, app.path_changelog
        )

    @api_process_raw(CONTENT_TYPE_TEXT)
    async def apps_app_documentation(self, request: web.Request) -> str:
        """Return documentation from app."""
        # Frontend can't handle error response here, need to return 200 and error as text for now
        try:
            app = self._extract_app(request)
        except APIError as err:
            return str(err)

        if not app.with_documentation:
            return f"No documentation found for app {app.slug}!"

        return await self.sys_run_in_executor(
            _read_static_text_file, app.path_documentation
        )

    @api_process
    async def apps_app_availability(self, request: web.Request) -> None:
        """Check app availability for current system."""
        app = cast(AppStore, self._extract_app(request))
        app.validate_availability()

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
    async def add_repository(self, request: web.Request) -> None:
        """Add repository to the store."""
        body = await api_validate(SCHEMA_ADD_REPOSITORY, request)
        await asyncio.shield(self.sys_store.add_repository(body[ATTR_REPOSITORY]))

    @api_process
    async def remove_repository(self, request: web.Request) -> None:
        """Remove repository from the store."""
        repository: Repository = self._extract_repository(request)
        await asyncio.shield(self.sys_store.remove_repository(repository))

    @api_process
    async def repositories_repository_repair(self, request: web.Request) -> None:
        """Repair repository."""
        repository: Repository = self._extract_repository(request)
        await asyncio.shield(repository.reset())

        # If we have an execute reset suggestion on this repository, dismiss it and the issue
        for suggestion in self.sys_resolution.suggestions:
            if (
                suggestion.type == SuggestionType.EXECUTE_RESET
                and suggestion.context == ContextType.STORE
                and suggestion.reference == repository.slug
            ):
                for issue in self.sys_resolution.issues_for_suggestion(suggestion):
                    self.sys_resolution.dismiss_issue(issue)
                return
