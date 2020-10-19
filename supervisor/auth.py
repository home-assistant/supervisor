"""Manage SSO for Add-ons with Home Assistant user."""
import hashlib
import logging

from .addons.addon import Addon
from .const import ATTR_ADDON, ATTR_PASSWORD, ATTR_USERNAME, FILE_HASSIO_AUTH
from .coresys import CoreSys, CoreSysAttributes
from .exceptions import AuthError, AuthPasswordResetError, HomeAssistantAPIError
from .utils.json import JsonConfig
from .validate import SCHEMA_AUTH_CONFIG

_LOGGER: logging.Logger = logging.getLogger(__name__)


class Auth(JsonConfig, CoreSysAttributes):
    """Manage SSO for Add-ons with Home Assistant user."""

    def __init__(self, coresys: CoreSys) -> None:
        """Initialize updater."""
        super().__init__(FILE_HASSIO_AUTH, SCHEMA_AUTH_CONFIG)
        self.coresys: CoreSys = coresys

    def _check_cache(self, username: str, password: str) -> bool:
        """Check password in cache."""
        username_h = self._rehash(username)
        password_h = self._rehash(password, username)

        if self._data.get(username_h) == password_h:
            _LOGGER.debug("Username '%s' is in cache", username)
            return True

        _LOGGER.warning("Username '%s' not is in cache", username)
        return False

    def _update_cache(self, username: str, password: str) -> None:
        """Cache a username, password."""
        username_h = self._rehash(username)
        password_h = self._rehash(password, username)

        if self._data.get(username_h) == password_h:
            return

        self._data[username_h] = password_h
        self.save_data()

    def _dismatch_cache(self, username: str, password: str) -> None:
        """Remove user from cache."""
        username_h = self._rehash(username)
        password_h = self._rehash(password, username)

        if self._data.get(username_h) != password_h:
            return

        self._data.pop(username_h, None)
        self.save_data()

    async def check_login(self, addon: Addon, username: str, password: str) -> bool:
        """Check username login."""
        if password is None:
            _LOGGER.error("None as password is not supported!")
            raise AuthError()
        _LOGGER.info("Auth request from '%s' for '%s'", addon.slug, username)

        # Get from cache
        cache_hit = self._check_cache(username, password)

        # Check API state
        if not await self.sys_homeassistant.api.check_api_state():
            _LOGGER.debug("Home Assistant not running, checking cache")
            return cache_hit

        # Home Assistant Core take over 1-2sec to validate it
        # Let's use the cache and if they don't hit, we ask on core
        if cache_hit:
            return True

        # Ask on Core
        try:
            async with self.sys_homeassistant.api.make_request(
                "post",
                "api/hassio_auth",
                json={
                    ATTR_USERNAME: username,
                    ATTR_PASSWORD: password,
                    ATTR_ADDON: addon.slug,
                },
            ) as req:

                if req.status == 200:
                    _LOGGER.info("Successful login for '%s'", username)
                    self._update_cache(username, password)
                    return True

                _LOGGER.warning("Unauthorized login for '%s'", username)
                self._dismatch_cache(username, password)
                return False
        except HomeAssistantAPIError:
            _LOGGER.error("Can't request auth on Home Assistant!")

        raise AuthError()

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
        except HomeAssistantAPIError:
            _LOGGER.error("Can't request password reset on Home Assistant!")

        raise AuthPasswordResetError()

    @staticmethod
    def _rehash(value: str, salt2: str = "") -> str:
        """Rehash a value."""
        for idx in range(1, 20):
            value = hashlib.sha256(f"{value}{idx}{salt2}".encode()).hexdigest()
        return value
