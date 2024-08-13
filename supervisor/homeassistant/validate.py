"""Validate functions."""

import uuid

import voluptuous as vol

from ..const import (
    ATTR_ACCESS_TOKEN,
    ATTR_AUDIO_INPUT,
    ATTR_AUDIO_OUTPUT,
    ATTR_BACKUPS_EXCLUDE_DATABASE,
    ATTR_BOOT,
    ATTR_IMAGE,
    ATTR_PORT,
    ATTR_REFRESH_TOKEN,
    ATTR_SSL,
    ATTR_UUID,
    ATTR_VERSION,
    ATTR_WATCHDOG,
)
from ..validate import docker_image, network_port, token, uuid_match, version_tag
from .const import ATTR_OVERRIDE_IMAGE

# pylint: disable=no-value-for-parameter
SCHEMA_HASS_CONFIG = vol.Schema(
    {
        vol.Optional(ATTR_UUID, default=lambda: uuid.uuid4().hex): uuid_match,
        vol.Optional(ATTR_VERSION): version_tag,
        vol.Optional(ATTR_IMAGE): docker_image,
        vol.Optional(ATTR_ACCESS_TOKEN): token,
        vol.Optional(ATTR_BOOT, default=True): vol.Boolean(),
        vol.Optional(ATTR_PORT, default=8123): network_port,
        vol.Optional(ATTR_REFRESH_TOKEN): vol.Maybe(str),
        vol.Optional(ATTR_SSL, default=False): vol.Boolean(),
        vol.Optional(ATTR_WATCHDOG, default=True): vol.Boolean(),
        vol.Optional(ATTR_AUDIO_OUTPUT, default=None): vol.Maybe(str),
        vol.Optional(ATTR_AUDIO_INPUT, default=None): vol.Maybe(str),
        vol.Optional(ATTR_BACKUPS_EXCLUDE_DATABASE, default=False): vol.Boolean(),
        vol.Optional(ATTR_OVERRIDE_IMAGE, default=False): vol.Boolean(),
    },
    extra=vol.REMOVE_EXTRA,
)
