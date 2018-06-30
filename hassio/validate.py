"""Validate functions."""
import uuid
import re

import voluptuous as vol
import pytz

from .const import (
    ATTR_IMAGE, ATTR_LAST_VERSION, ATTR_CHANNEL, ATTR_TIMEZONE, ATTR_HASSOS,
    ATTR_ADDONS_CUSTOM_LIST, ATTR_PASSWORD, ATTR_HOMEASSISTANT, ATTR_HASSIO,
    ATTR_BOOT, ATTR_LAST_BOOT, ATTR_SSL, ATTR_PORT, ATTR_WATCHDOG,
    ATTR_WAIT_BOOT, ATTR_UUID, CHANNEL_STABLE, CHANNEL_BETA, CHANNEL_DEV)


RE_REPOSITORY = re.compile(r"^(?P<url>[^#]+)(?:#(?P<branch>[\w\-]+))?$")

NETWORK_PORT = vol.All(vol.Coerce(int), vol.Range(min=1, max=65535))
WAIT_BOOT = vol.All(vol.Coerce(int), vol.Range(min=1, max=60))
DOCKER_IMAGE = vol.Match(r"^[\w{}]+/[\-\w{}]+$")
ALSA_DEVICE = vol.Maybe(vol.Match(r"\d+,\d+"))
CHANNELS = vol.In([CHANNEL_STABLE, CHANNEL_BETA, CHANNEL_DEV])


def validate_repository(repository):
    """Validate a valide repository."""
    data = RE_REPOSITORY.match(repository)
    if not data:
        raise vol.Invalid("No valid repository format!")

    # Validate URL
    # pylint: disable=no-value-for-parameter
    vol.Url()(data.group('url'))

    return repository


# pylint: disable=no-value-for-parameter
REPOSITORIES = vol.All([validate_repository], vol.Unique())


def validate_timezone(timezone):
    """Validate voluptuous timezone."""
    try:
        pytz.timezone(timezone)
    except pytz.exceptions.UnknownTimeZoneError:
        raise vol.Invalid(
            "Invalid time zone passed in. Valid options can be found here: "
            "http://en.wikipedia.org/wiki/List_of_tz_database_time_zones") \
                from None

    return timezone


# pylint: disable=inconsistent-return-statements
def convert_to_docker_ports(data):
    """Convert data into docker port list."""
    # dynamic ports
    if data is None:
        return None

    # single port
    if isinstance(data, int):
        return NETWORK_PORT(data)

    # port list
    if isinstance(data, list) and len(data) > 2:
        return vol.Schema([NETWORK_PORT])(data)

    # ip port mapping
    if isinstance(data, list) and len(data) == 2:
        return (vol.Coerce(str)(data[0]), NETWORK_PORT(data[1]))

    raise vol.Invalid("Can't validate docker host settings")


DOCKER_PORTS = vol.Schema({
    vol.All(vol.Coerce(str), vol.Match(r"^\d+(?:/tcp|/udp)?$")):
        convert_to_docker_ports,
})


# pylint: disable=no-value-for-parameter
SCHEMA_HASS_CONFIG = vol.Schema({
    vol.Optional(ATTR_UUID, default=lambda: uuid.uuid4().hex):
        vol.Match(r"^[0-9a-f]{32}$"),
    vol.Optional(ATTR_BOOT, default=True): vol.Boolean(),
    vol.Inclusive(ATTR_IMAGE, 'custom_hass'): DOCKER_IMAGE,
    vol.Inclusive(ATTR_LAST_VERSION, 'custom_hass'): vol.Coerce(str),
    vol.Optional(ATTR_PORT, default=8123): NETWORK_PORT,
    vol.Optional(ATTR_PASSWORD): vol.Maybe(vol.Coerce(str)),
    vol.Optional(ATTR_SSL, default=False): vol.Boolean(),
    vol.Optional(ATTR_WATCHDOG, default=True): vol.Boolean(),
    vol.Optional(ATTR_WAIT_BOOT, default=600):
        vol.All(vol.Coerce(int), vol.Range(min=60)),
}, extra=vol.REMOVE_EXTRA)


SCHEMA_UPDATER_CONFIG = vol.Schema({
    vol.Optional(ATTR_CHANNEL, default=CHANNEL_STABLE): CHANNELS,
    vol.Optional(ATTR_HOMEASSISTANT): vol.Coerce(str),
    vol.Optional(ATTR_HASSIO): vol.Coerce(str),
    vol.Optional(ATTR_HASSOS): vol.Coerce(str),
}, extra=vol.REMOVE_EXTRA)


# pylint: disable=no-value-for-parameter
SCHEMA_HASSIO_CONFIG = vol.Schema({
    vol.Optional(ATTR_TIMEZONE, default='UTC'): validate_timezone,
    vol.Optional(ATTR_LAST_BOOT): vol.Coerce(str),
    vol.Optional(ATTR_ADDONS_CUSTOM_LIST, default=[
        "https://github.com/hassio-addons/repository",
    ]): REPOSITORIES,
    vol.Optional(ATTR_WAIT_BOOT, default=5): WAIT_BOOT,
}, extra=vol.REMOVE_EXTRA)
