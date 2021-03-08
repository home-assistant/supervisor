"""Validate resolution configuration schema."""

import voluptuous as vol

from ..const import ATTR_CHECKS, ATTR_ENABLED

SCHEMA_CHECK = vol.Schema(
    {
        vol.Required(ATTR_ENABLED): bool,
    },
    extra=vol.REMOVE_EXTRA,
)

SCHEMA_CHECK_CONFIG = vol.Schema(
    {
        vol.Required(ATTR_CHECKS, default=dict): {str: SCHEMA_CHECK},
    },
    extra=vol.REMOVE_EXTRA,
)
