"""Validate utils."""

import voluptuous as vol

from .dt import get_time_zone


def schema_or(schema):
    """Allow schema or empty."""

    def _wrapper(value):
        """Define a wrapper for validator."""
        if not value:
            return value
        return schema(value)

    return _wrapper


def validate_timezone(timezone):
    """Validate voluptuous timezone."""
    if get_time_zone(timezone) is not None:
        return timezone
    raise vol.Invalid(
        "Invalid time zone passed in. Valid options can be found here: "
        "http://en.wikipedia.org/wiki/List_of_tz_database_time_zones"
    ) from None
