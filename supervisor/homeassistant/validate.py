"""Validate functions."""

from contextlib import suppress
import uuid

from awesomeversion import AwesomeVersion, AwesomeVersionException
import voluptuous as vol

from ..const import (
    ATTR_ACCESS_TOKEN,
    ATTR_AUDIO_INPUT,
    ATTR_AUDIO_OUTPUT,
    ATTR_BACKUPS_EXCLUDE_DATABASE,
    ATTR_BOOT,
    ATTR_DUPLICATE_LOG_FILE,
    ATTR_IMAGE,
    ATTR_PORT,
    ATTR_REFRESH_TOKEN,
    ATTR_SSL,
    ATTR_UUID,
    ATTR_VERSION,
    ATTR_WATCHDOG,
)
from ..utils import version_is_new_enough
from ..validate import docker_image, network_port, token, uuid_match, version_tag
from . import const
from .const import ATTR_OVERRIDE_IMAGE


def core_binds_app_sockets(version: AwesomeVersion | str | None) -> bool:
    """Return True if this Core version binds a socket for each app."""
    # Looked up on the module so tests can patch the unreleased constant
    if not version or not const.CORE_APP_SOCKET_MIN_VERSION.valid:
        return False
    with suppress(AwesomeVersionException, TypeError):
        return version_is_new_enough(
            AwesomeVersion(str(version)), const.CORE_APP_SOCKET_MIN_VERSION
        )
    return False


# pylint: disable=no-value-for-parameter
SCHEMA_HASS_CONFIG = vol.Schema(
    {
        vol.Optional(ATTR_UUID, default=lambda: uuid.uuid4().hex): uuid_match,
        vol.Optional(ATTR_VERSION): version_tag,
        vol.Optional(ATTR_IMAGE): docker_image,
        vol.Optional(ATTR_ACCESS_TOKEN): token,
        vol.Optional(ATTR_BOOT, default=True): vol.Boolean(),
        vol.Optional(ATTR_PORT, default=80): network_port,
        vol.Optional(ATTR_REFRESH_TOKEN): vol.Maybe(str),
        vol.Optional(ATTR_SSL, default=False): vol.Boolean(),
        vol.Optional(ATTR_WATCHDOG, default=True): vol.Boolean(),
        vol.Optional(ATTR_AUDIO_OUTPUT, default=None): vol.Maybe(str),
        vol.Optional(ATTR_AUDIO_INPUT, default=None): vol.Maybe(str),
        vol.Optional(ATTR_BACKUPS_EXCLUDE_DATABASE, default=False): vol.Boolean(),
        vol.Optional(ATTR_DUPLICATE_LOG_FILE, default=False): vol.Boolean(),
        vol.Optional(ATTR_OVERRIDE_IMAGE, default=False): vol.Boolean(),
    },
    extra=vol.REMOVE_EXTRA,
)
