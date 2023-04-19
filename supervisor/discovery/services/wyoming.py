"""Discovery service for the Wyoming Protocol integration."""
from typing import Any, cast
from urllib.parse import urlparse

import voluptuous as vol

from ..const import ATTR_URI


def validate_uri(value: Any) -> str:
    """Validate an Wyoming URI.

    Currently accepts TCP URIs, can extended
    to accept UNIX sockets in the future.
    """
    uri_value = str(value)

    if urlparse(uri_value).scheme == "tcp":
        return cast(str, vol.Schema(vol.Url())(uri_value))

    raise vol.Invalid("invalid Wyoming Protocol URI")


SCHEMA = vol.Schema({vol.Required(ATTR_URI): validate_uri})
