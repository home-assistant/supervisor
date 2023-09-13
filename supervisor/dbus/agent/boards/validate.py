"""Validation for board config."""

import voluptuous as vol

from ....const import (
    ATTR_ACTIVITY_LED,
    ATTR_DISK_LED,
    ATTR_HEARTBEAT_LED,
    ATTR_POWER_LED,
    ATTR_USER_LED,
)

SCHEMA_BASE_BOARD = vol.Schema({}, extra=vol.REMOVE_EXTRA)

SCHEMA_GREEN_BOARD = vol.Schema(
    {
        vol.Optional(ATTR_ACTIVITY_LED, default=True): vol.Boolean(),
        vol.Optional(ATTR_POWER_LED, default=True): vol.Boolean(),
        vol.Optional(ATTR_USER_LED, default=True): vol.Boolean(),
    },
    extra=vol.REMOVE_EXTRA,
)

SCHEMA_YELLOW_BOARD = vol.Schema(
    {
        vol.Optional(ATTR_DISK_LED, default=True): vol.Boolean(),
        vol.Optional(ATTR_HEARTBEAT_LED, default=True): vol.Boolean(),
        vol.Optional(ATTR_POWER_LED, default=True): vol.Boolean(),
    },
    extra=vol.REMOVE_EXTRA,
)
