"""Validate utils."""

import pytz
import voluptuous as vol


def schema_or(schema):
    """Allow schema or empty."""

    def _wrapper(value):
        """Wrapper for validator."""
        if not value:
            return value
        return schema(value)

    return _wrapper


def validate_timezone(timezone):
    """Validate voluptuous timezone."""
    try:
        pytz.timezone(timezone)
    except pytz.exceptions.UnknownTimeZoneError:
        raise vol.Invalid(
            "Invalid time zone passed in. Valid options can be found here: "
            "http://en.wikipedia.org/wiki/List_of_tz_database_time_zones"
        ) from None

    return timezone
