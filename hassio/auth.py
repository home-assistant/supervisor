"""Manage SSO for Add-ons with Home Assistant user."""
import hashlib
import logging

from .addons.addon import Addon
from .const import ATTR_ADDON, ATTR_PASSWORD, ATTR_USERNAME, FILE_HASSIO_AUTH
from .coresys import CoreSys, CoreSysAttributes
from .exceptions import AuthError, HomeAssistantAPIError
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
            _LOGGER.info("Cache hit for %s", username)
            return True

        _LOGGER.warning("No cache hit for %s", username)
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
        _LOGGER.info("Auth request from %s for %s", addon.slug, username)

        # Check API state
        if not await self.sys_homeassistant.check_api_state():
            _LOGGER.info("Home Assistant not running, check cache")
            return self._check_cache(username, password)

        try:
            async with self.sys_homeassistant.make_request(
                "post",
                "api/hassio_auth",
                json={
                    ATTR_USERNAME: username,
                    ATTR_PASSWORD: password,
                    ATTR_ADDON: addon.slug,
                },
            ) as req:

                if req.status == 200:
                    _LOGGER.info("Success login from %s", username)
                    self._update_cache(username, password)
                    return True

                _LOGGER.warning("Wrong login from %s", username)
                self._dismatch_cache(username, password)
                return False
        except HomeAssistantAPIError:
            _LOGGER.error("Can't request auth on Home Assistant!")

        raise AuthError()

    async def change_password(self, username: str, password: str) -> None:
        """Change user password login."""
        try:
            async with self.sys_homeassistant.make_request(
                "post",
                "api/hassio_auth/password_reset",
                json={ATTR_USERNAME: username, ATTR_PASSWORD: password,},
            ) as req:
                if req.status == 200:
                    _LOGGER.info("Success password reset %s", username)
                    return

                _LOGGER.warning("Wrong password reset %s", username)
        except HomeAssistantAPIError:
            _LOGGER.error("Can't request password reset on Home Assistant!")

        raise AuthError()

    @staticmethod
    def _rehash(value: str, salt2: str = "") -> str:
        """Rehash a value."""
        for idx in range(1, 20):
            value = hashlib.sha256(f"{value}{idx}{salt2}".encode()).hexdigest()
        return value
