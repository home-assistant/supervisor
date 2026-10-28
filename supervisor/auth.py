"""Manage SSO for Apps with Home Assistant user."""

import asyncio
from contextlib import suppress
from dataclasses import dataclass
import hashlib
import logging
from typing import Any, TypedDict, cast

from .apps.app import App
from .const import (
    ATTR_GROUP_IDS,
    ATTR_PASSWORD,
    ATTR_USERNAME,
    FILE_HASSIO_AUTH,
    HomeAssistantUser,
)
from .coresys import CoreSys, CoreSysAttributes
from .exceptions import (
    AuthHomeAssistantAPIValidationError,
    AuthInvalidNonStringValueError,
    AuthListUsersError,
    AuthPasswordResetError,
    HomeAssistantAPIError,
    HomeAssistantAuthError,
    HomeAssistantWSError,
)
from .utils.common import FileConfiguration
from .utils.json import json_loads
from .validate import SCHEMA_AUTH_CONFIG

_LOGGER: logging.Logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class LoginResult:
    """Outcome of a successful login."""

    group_ids: list[str]


class BackendAuthRequest(TypedDict):
    """Model for a backend auth request.

    https://github.com/home-assistant/core/blob/ed9503324d9d255e6fb077f1614fb6d55800f389/homeassistant/components/hassio/auth.py#L66-L73
    """

    username: str
    password: str
    addon: str


class Auth(FileConfiguration, CoreSysAttributes):
    """Manage SSO for Apps with Home Assistant user."""

    def __init__(self, coresys: CoreSys) -> None:
        """Initialize updater."""
        super().__init__(FILE_HASSIO_AUTH, SCHEMA_AUTH_CONFIG)
        self.coresys: CoreSys = coresys

        self._running: dict[str, asyncio.Task] = {}

    def _cache_entry(self, username_h: str) -> tuple[str, list[str]] | None:
        """Return the cached password hash and group IDs of a user."""
        entry = self._data.get(username_h)
        if entry is None:
            return None
        if isinstance(entry, str):
            return entry, []
        return entry[ATTR_PASSWORD], list(entry[ATTR_GROUP_IDS])

    def _check_cache(self, username: str, password: str) -> bool | None:
        """Check password in cache."""
        username_h = self._rehash(username)
        password_h = self._rehash(password, username)

        if (entry := self._cache_entry(username_h)) is None:
            _LOGGER.debug("Username '%s' not is in cache", username)
            return None

        if entry[0] == password_h:
            _LOGGER.debug("Username '%s' is in cache", username)
            return True
        return False

    def _cached_login(self, username: str) -> LoginResult:
        """Return the cached login result of a user."""
        entry = self._cache_entry(self._rehash(username))
        return LoginResult(group_ids=entry[1] if entry else [])

    async def _update_cache(
        self, username: str, password: str, group_ids: list[str]
    ) -> None:
        """Cache a username, password and group IDs."""
        username_h = self._rehash(username)
        password_h = self._rehash(password, username)

        if self._cache_entry(username_h) == (password_h, group_ids):
            return

        self._data[username_h] = {
            ATTR_PASSWORD: password_h,
            ATTR_GROUP_IDS: group_ids,
        }
        await self.save_data()

    async def _dismatch_cache(self, username: str, password: str) -> None:
        """Remove user from cache."""
        username_h = self._rehash(username)
        password_h = self._rehash(password, username)

        if (entry := self._cache_entry(username_h)) is None or entry[0] != password_h:
            return

        self._data.pop(username_h, None)
        await self.save_data()

    async def check_login(
        self, app: App, username: str | None, password: str | None
    ) -> LoginResult | None:
        """Check username login, return None if the login is invalid."""
        if username is None or password is None:
            raise AuthInvalidNonStringValueError(_LOGGER.error)

        _LOGGER.info("Auth request from '%s' for '%s'", app.slug, username)

        # Get from cache
        cache_hit = self._check_cache(username, password)

        # Check API state
        if not await self.sys_homeassistant.api.check_api_state():
            _LOGGER.info("Home Assistant not running, checking cache")
            return self._cached_login(username) if cache_hit else None

        # A mismatch may be a changed password, so only trust positive hits
        if cache_hit is not True:
            return await self._backend_login(app, username, password)

        # Home Assistant Core take over 1-2sec to validate it
        # Let's use the cache and update the cache in background
        if username not in self._running:
            task = self.sys_create_task(
                self._refresh_cached_login(app, username, password)
            )
            # Cleanup must also run if the task is cancelled before it starts
            task.add_done_callback(lambda _: self._running.pop(username, None))
            self._running[username] = task

        return self._cached_login(username)

    async def _refresh_cached_login(
        self, app: App, username: str, password: str
    ) -> None:
        """Re-validate a cached login against Core in the background.

        Nothing awaits this task, so failures already logged by the request
        path are consumed here instead of surfacing as unretrieved task errors.
        """
        with suppress(AuthHomeAssistantAPIValidationError, HomeAssistantAuthError):
            await self._backend_login(app, username, password)

    async def _backend_login(
        self, app: App, username: str, password: str
    ) -> LoginResult | None:
        """Check username login on core, return None if the login is invalid."""
        try:
            async with self.sys_homeassistant.api.make_request(
                "post",
                "api/hassio_auth",
                json=cast(
                    dict[str, Any],
                    BackendAuthRequest(
                        username=username, password=password, addon=app.slug
                    ),
                ),
            ) as req:
                if req.status == 200:
                    _LOGGER.info("Successful login for '%s'", username)
                    group_ids = _group_ids_from_body(await req.read())
                    await self._update_cache(username, password, group_ids)
                    return LoginResult(group_ids=group_ids)

                _LOGGER.warning("Unauthorized login for '%s'", username)
                await self._dismatch_cache(username, password)
                return None
        except HomeAssistantAuthError:
            # Core rejected Supervisor, not the app's user. The credentials
            # were never checked, so leave the cache alone.
            raise
        except HomeAssistantAPIError as err:
            _LOGGER.error("Can't request auth on Home Assistant: %s", err)

        raise AuthHomeAssistantAPIValidationError

    async def change_password(self, username: str, password: str) -> None:
        """Change user password login."""
        try:
            async with self.sys_homeassistant.api.make_request(
                "post",
                "api/hassio_auth/password_reset",
                json={ATTR_USERNAME: username, ATTR_PASSWORD: password},
            ) as req:
                if req.status == 200:
                    _LOGGER.info("Successful password reset for '%s'", username)
                    return

                _LOGGER.warning("The user '%s' is not registered", username)
        except HomeAssistantAuthError:
            raise
        except HomeAssistantAPIError as err:
            _LOGGER.error("Can't request password reset on Home Assistant: %s", err)

        raise AuthPasswordResetError(user=username)

    async def list_users(self) -> list[HomeAssistantUser]:
        """List users on the Home Assistant instance."""
        try:
            return await self.sys_homeassistant.list_users()
        except HomeAssistantWSError as err:
            _LOGGER.error("Can't request listing users on Home Assistant: %s", err)
            raise AuthListUsersError from err

    @staticmethod
    def _rehash(value: str, salt2: str = "") -> str:
        """Rehash a value."""
        for idx in range(1, 20):
            value = hashlib.sha256(f"{value}{idx}{salt2}".encode()).hexdigest()
        return value


def _group_ids_from_body(body: bytes) -> list[str]:
    """Return the group IDs Core reported for a login.

    Core versions predating the field answer with an empty body.
    """
    if not body:
        return []
    data = json_loads(body)
    if not isinstance(data, dict):
        return []
    group_ids = data.get(ATTR_GROUP_IDS)
    if not isinstance(group_ids, list):
        return []
    return [group_id for group_id in group_ids if isinstance(group_id, str)]
