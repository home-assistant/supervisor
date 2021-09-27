"""Validate add-ons options schema."""

import voluptuous as vol

from ..const import ATTR_MAINTAINER, ATTR_NAME, ATTR_URL

# pylint: disable=no-value-for-parameter
SCHEMA_REPOSITORY_CONFIG = vol.Schema(
    {
        vol.Required(ATTR_NAME): str,
        vol.Optional(ATTR_URL): vol.Url(),
        vol.Optional(ATTR_MAINTAINER): str,
    },
    extra=vol.REMOVE_EXTRA,
)
