"""Validate functions."""
import voluptuous as vol

import pytz

from .const import (
    ATTR_DEVICES, ATTR_IMAGE, ATTR_LAST_VERSION, ATTR_SESSIONS, ATTR_PASSWORD,
    ATTR_TOTP, ATTR_SECURITY, ATTR_BETA_CHANNEL, ATTR_TIMEZONE,
    ATTR_ADDONS_CUSTOM_LIST, ATTR_AUDIO_OUTPUT, ATTR_AUDIO_INPUT,
    ATTR_HOMEASSISTANT, ATTR_HASSIO, ATTR_BOOT, ATTR_LAST_BOOT, ATTR_SSL,
    ATTR_PORT, ATTR_WATCHDOG, ATTR_WAIT_BOOT)


NETWORK_PORT = vol.All(vol.Coerce(int), vol.Range(min=1, max=65535))
HASS_DEVICES = [vol.Match(r"^[^/]*$")]
ALSA_CHANNEL = vol.Match(r"\d+,\d+")
WAIT_BOOT = vol.All(vol.Coerce(int), vol.Range(min=1, max=60))


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
    vol.Optional(ATTR_DEVICES, default=[]): HASS_DEVICES,
    vol.Optional(ATTR_BOOT, default=True): vol.Boolean(),
    vol.Inclusive(ATTR_IMAGE, 'custom_hass'): vol.Coerce(str),
    vol.Inclusive(ATTR_LAST_VERSION, 'custom_hass'): vol.Coerce(str),
    vol.Optional(ATTR_PORT, default=8123): NETWORK_PORT,
    vol.Optional(ATTR_PASSWORD): vol.Any(None, vol.Coerce(str)),
    vol.Optional(ATTR_SSL, default=False): vol.Boolean(),
    vol.Optional(ATTR_WATCHDOG, default=True): vol.Boolean(),
}, extra=vol.REMOVE_EXTRA)


# pylint: disable=no-value-for-parameter
SCHEMA_UPDATER_CONFIG = vol.Schema({
    vol.Optional(ATTR_BETA_CHANNEL, default=False): vol.Boolean(),
    vol.Optional(ATTR_HOMEASSISTANT): vol.Coerce(str),
    vol.Optional(ATTR_HASSIO): vol.Coerce(str),
}, extra=vol.REMOVE_EXTRA)


# pylint: disable=no-value-for-parameter
SCHEMA_HASSIO_CONFIG = vol.Schema({
    vol.Optional(ATTR_TIMEZONE, default='UTC'): validate_timezone,
    vol.Optional(ATTR_LAST_BOOT): vol.Coerce(str),
    vol.Optional(ATTR_ADDONS_CUSTOM_LIST, default=[]): [vol.Url()],
    vol.Optional(ATTR_SECURITY, default=False): vol.Boolean(),
    vol.Optional(ATTR_TOTP): vol.Coerce(str),
    vol.Optional(ATTR_PASSWORD): vol.Coerce(str),
    vol.Optional(ATTR_SESSIONS, default={}):
        vol.Schema({vol.Coerce(str): vol.Coerce(str)}),
    vol.Optional(ATTR_AUDIO_OUTPUT): ALSA_CHANNEL,
    vol.Optional(ATTR_AUDIO_INPUT): ALSA_CHANNEL,
    vol.Optional(ATTR_WAIT_BOOT, default=5): WAIT_BOOT,
}, extra=vol.REMOVE_EXTRA)
