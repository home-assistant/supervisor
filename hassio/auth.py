"""Manage SSO for Add-ons with Home Assistant user."""
import logging
import hashlib

from .const import FILE_HASSIO_AUTH, ATTR_PASSWORD, ATTR_USERNAME, ATTR_ADDON
from .coresys import CoreSysAttributes
from .utils.json import JsonConfig
from .validate import SCHEMA_AUTH_CONFIG
from .exceptions import AuthError, HomeAssistantAPIError

_LOGGER: logging.Logger = logging.getLogger(__name__)


class Auth(JsonConfig, CoreSysAttributes):
    """Manage SSO for Add-ons with Home Assistant user."""

    def __init__(self, coresys):
        """Initialize updater."""
        super().__init__(FILE_HASSIO_AUTH, SCHEMA_AUTH_CONFIG)
        self.coresys = coresys

    def _check_cache(self, username, password):
        """Check password in cache."""
        username_h = _rehash(username)
        password_h = _rehash(password, username)

        if self._data.get(username_h) == password_h:
            _LOGGER.info("Cache hit for %s", username)
            return True

        _LOGGER.warning("No cache hit for %s", username)
        return False

    def _update_cache(self, username, password):
        """Cache a username, password."""
        username_h = _rehash(username)
        password_h = _rehash(password, username)

        if self._data.get(username_h) == password_h:
            return

        self._data[username_h] = password_h
        self.save_data()

    def _dismatch_cache(self, username, password):
        """Remove user from cache."""
        username_h = _rehash(username)
        password_h = _rehash(password, username)

        if self._data.get(username_h) != password_h:
            return

        self._data.pop(username_h, None)
        self.save_data()

    async def check_login(self, addon, username, password):
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


def _rehash(value, salt2=""):
    """Rehash a value."""
    for idx in range(1, 20):
        value = hashlib.sha256(f"{value}{idx}{salt2}".encode()).hexdigest()
    return value
