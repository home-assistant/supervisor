"""Validate functions."""
import re
import uuid
import ipaddress

import voluptuous as vol

from .const import (
    ATTR_ACCESS_TOKEN,
    ATTR_ADDONS_CUSTOM_LIST,
    ATTR_BOOT,
    ATTR_CHANNEL,
    ATTR_DEBUG,
    ATTR_DEBUG_BLOCK,
    ATTR_DNS,
    ATTR_HASSIO,
    ATTR_HASSOS,
    ATTR_HASSOS_CLI,
    ATTR_HOMEASSISTANT,
    ATTR_IMAGE,
    ATTR_LAST_BOOT,
    ATTR_LAST_VERSION,
    ATTR_LOGGING,
    ATTR_PASSWORD,
    ATTR_PORT,
    ATTR_PORTS,
    ATTR_REFRESH_TOKEN,
    ATTR_SERVERS,
    ATTR_SESSION,
    ATTR_SSL,
    ATTR_TIMEZONE,
    ATTR_UUID,
    ATTR_VERSION,
    ATTR_WAIT_BOOT,
    ATTR_WATCHDOG,
    CHANNEL_BETA,
    CHANNEL_DEV,
    CHANNEL_STABLE,
    DNS_SERVERS,
)
from .utils.validate import validate_timezone

RE_REPOSITORY = re.compile(r"^(?P<url>[^#]+)(?:#(?P<branch>[\w\-]+))?$")

# pylint: disable=no-value-for-parameter
NETWORK_PORT = vol.All(vol.Coerce(int), vol.Range(min=1, max=65535))
WAIT_BOOT = vol.All(vol.Coerce(int), vol.Range(min=1, max=60))
DOCKER_IMAGE = vol.Match(r"^[\w{}]+/[\-\w{}]+$")
ALSA_DEVICE = vol.Maybe(vol.Match(r"\d+,\d+"))
CHANNELS = vol.In([CHANNEL_STABLE, CHANNEL_BETA, CHANNEL_DEV])
UUID_MATCH = vol.Match(r"^[0-9a-f]{32}$")
SHA256 = vol.Match(r"^[0-9a-f]{64}$")
TOKEN = vol.Match(r"^[0-9a-f]{32,256}$")
LOG_LEVEL = vol.In(["debug", "info", "warning", "error", "critical"])
DNS_SERVER_LIST = vol.All(vol.Length(max=8), [dns_url])


def dns_url(url: str) -> str:
    """ takes a DNS url (str) and validates that it matches the scheme dns://<ip address>."""
    if not url.lower().startswith("dns://"):
        raise vol.error.Invalid("Doesn't start with dns://")
    address = url[6:]  # strip the dns:// off
    try:
        ipaddress.ip_address(address)  # matches ipv4 or ipv6 addresses
    except ValueError:
        raise vol.error.Invalid("Invalid DNS URL: {}".format(url))
    return dns_url


def validate_repository(repository: str) -> str:
    """Validate a valid repository."""
    data = RE_REPOSITORY.match(repository)
    if not data:
        raise vol.Invalid("No valid repository format!")

    # Validate URL
    # pylint: disable=no-value-for-parameter
    vol.Url()(data.group("url"))

    return repository


# pylint: disable=no-value-for-parameter
REPOSITORIES = vol.All([validate_repository], vol.Unique())


DOCKER_PORTS = vol.Schema(
    {
        vol.All(vol.Coerce(str), vol.Match(r"^\d+(?:/tcp|/udp)?$")): vol.Maybe(
            NETWORK_PORT
        )
    }
)

DOCKER_PORTS_DESCRIPTION = vol.Schema(
    {vol.All(vol.Coerce(str), vol.Match(r"^\d+(?:/tcp|/udp)?$")): vol.Coerce(str)}
)


# pylint: disable=no-value-for-parameter
SCHEMA_HASS_CONFIG = vol.Schema(
    {
        vol.Optional(ATTR_UUID, default=lambda: uuid.uuid4().hex): UUID_MATCH,
        vol.Optional(ATTR_VERSION): vol.Maybe(vol.Coerce(str)),
        vol.Optional(ATTR_ACCESS_TOKEN): TOKEN,
        vol.Optional(ATTR_BOOT, default=True): vol.Boolean(),
        vol.Inclusive(ATTR_IMAGE, "custom_hass"): DOCKER_IMAGE,
        vol.Inclusive(ATTR_LAST_VERSION, "custom_hass"): vol.Coerce(str),
        vol.Optional(ATTR_PORT, default=8123): NETWORK_PORT,
        vol.Optional(ATTR_PASSWORD): vol.Maybe(vol.Coerce(str)),
        vol.Optional(ATTR_REFRESH_TOKEN): vol.Maybe(vol.Coerce(str)),
        vol.Optional(ATTR_SSL, default=False): vol.Boolean(),
        vol.Optional(ATTR_WATCHDOG, default=True): vol.Boolean(),
        vol.Optional(ATTR_WAIT_BOOT, default=600): vol.All(
            vol.Coerce(int), vol.Range(min=60)
        ),
    },
    extra=vol.REMOVE_EXTRA,
)


SCHEMA_UPDATER_CONFIG = vol.Schema(
    {
        vol.Optional(ATTR_CHANNEL, default=CHANNEL_STABLE): CHANNELS,
        vol.Optional(ATTR_HOMEASSISTANT): vol.Coerce(str),
        vol.Optional(ATTR_HASSIO): vol.Coerce(str),
        vol.Optional(ATTR_HASSOS): vol.Coerce(str),
        vol.Optional(ATTR_HASSOS_CLI): vol.Coerce(str),
        vol.Optional(ATTR_DNS): vol.Coerce(str),
    },
    extra=vol.REMOVE_EXTRA,
)


# pylint: disable=no-value-for-parameter
SCHEMA_HASSIO_CONFIG = vol.Schema(
    {
        vol.Optional(ATTR_TIMEZONE, default="UTC"): validate_timezone,
        vol.Optional(ATTR_LAST_BOOT): vol.Coerce(str),
        vol.Optional(
            ATTR_ADDONS_CUSTOM_LIST,
            default=["https://github.com/hassio-addons/repository"],
        ): REPOSITORIES,
        vol.Optional(ATTR_WAIT_BOOT, default=5): WAIT_BOOT,
        vol.Optional(ATTR_LOGGING, default="info"): LOG_LEVEL,
        vol.Optional(ATTR_DEBUG, default=False): vol.Boolean(),
        vol.Optional(ATTR_DEBUG_BLOCK, default=False): vol.Boolean(),
    },
    extra=vol.REMOVE_EXTRA,
)


SCHEMA_AUTH_CONFIG = vol.Schema({SHA256: SHA256})


SCHEMA_INGRESS_CONFIG = vol.Schema(
    {
        vol.Required(ATTR_SESSION, default=dict): vol.Schema(
            {TOKEN: vol.Coerce(float)}
        ),
        vol.Required(ATTR_PORTS, default=dict): vol.Schema(
            {vol.Coerce(str): NETWORK_PORT}
        ),
    },
    extra=vol.REMOVE_EXTRA,
)


SCHEMA_DNS_CONFIG = vol.Schema(
    {
        vol.Optional(ATTR_VERSION): vol.Maybe(vol.Coerce(str)),
        vol.Optional(ATTR_SERVERS, default=DNS_SERVERS): DNS_SERVER_LIST,
    },
    extra=vol.REMOVE_EXTRA,
)
