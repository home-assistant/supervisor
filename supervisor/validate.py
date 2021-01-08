"""Validate functions."""
import ipaddress
import re
from typing import Optional, Union
import uuid

from awesomeversion import AwesomeVersion
import voluptuous as vol

from .const import (
    ATTR_ACCESS_TOKEN,
    ATTR_ADDONS_CUSTOM_LIST,
    ATTR_AUDIO,
    ATTR_AUDIO_INPUT,
    ATTR_AUDIO_OUTPUT,
    ATTR_BOOT,
    ATTR_CHANNEL,
    ATTR_CLI,
    ATTR_DEBUG,
    ATTR_DEBUG_BLOCK,
    ATTR_DIAGNOSTICS,
    ATTR_DNS,
    ATTR_HASSOS,
    ATTR_HOMEASSISTANT,
    ATTR_IMAGE,
    ATTR_LAST_BOOT,
    ATTR_LOGGING,
    ATTR_MULTICAST,
    ATTR_OBSERVER,
    ATTR_OTA,
    ATTR_PASSWORD,
    ATTR_PORT,
    ATTR_PORTS,
    ATTR_REFRESH_TOKEN,
    ATTR_REGISTRIES,
    ATTR_SESSION,
    ATTR_SSL,
    ATTR_SUPERVISOR,
    ATTR_TIMEZONE,
    ATTR_USERNAME,
    ATTR_UUID,
    ATTR_VERSION,
    ATTR_WAIT_BOOT,
    ATTR_WATCHDOG,
    SUPERVISOR_VERSION,
    LogLevel,
    UpdateChannel,
)
from .utils.validate import validate_timezone

RE_REPOSITORY = re.compile(r"^(?P<url>[^#]+)(?:#(?P<branch>[\w\-]+))?$")
RE_REGISTRY = re.compile(r"^([a-z0-9]+(-[a-z0-9]+)*\.)+[a-z]{2,}$")

# pylint: disable=no-value-for-parameter
# pylint: disable=invalid-name
network_port = vol.All(vol.Coerce(int), vol.Range(min=1, max=65535))
wait_boot = vol.All(vol.Coerce(int), vol.Range(min=1, max=60))
docker_image = vol.Match(r"^([a-zA-Z\-\.:\d{}]+/)*?([\-\w{}]+)/([\-\w{}]+)$")
uuid_match = vol.Match(r"^[0-9a-f]{32}$")
sha256 = vol.Match(r"^[0-9a-f]{64}$")
token = vol.Match(r"^[0-9a-f]{32,256}$")


def version_tag(value: Union[str, None, int, float]) -> Optional[AwesomeVersion]:
    """Validate main version handling."""
    if value is None:
        return None
    return AwesomeVersion(value)


def dns_url(url: str) -> str:
    """Take a DNS url (str) and validates that it matches the scheme dns://<ip address>."""
    if not url.lower().startswith("dns://"):
        raise vol.Invalid("Doesn't start with dns://") from None
    address: str = url[6:]  # strip the dns:// off
    try:
        ip = ipaddress.ip_address(address)  # matches ipv4 or ipv6 addresses
    except ValueError:
        raise vol.Invalid(f"Invalid DNS URL: {url}") from None

    # Currently only IPv4 work with docker network
    if ip.version != 4:
        raise vol.Invalid(f"Only IPv4 is working for DNS: {url}") from None
    return url


dns_server_list = vol.All(vol.Length(max=8), [dns_url])


def validate_repository(repository: str) -> str:
    """Validate a valid repository."""
    data = RE_REPOSITORY.match(repository)
    if not data:
        raise vol.Invalid("No valid repository format!") from None

    # Validate URL
    # pylint: disable=no-value-for-parameter
    vol.Url()(data.group("url"))

    return repository


# pylint: disable=no-value-for-parameter
repositories = vol.All([validate_repository], vol.Unique())

docker_port = vol.All(str, vol.Match(r"^\d+(?:/tcp|/udp)?$"))
docker_ports = vol.Schema({docker_port: vol.Maybe(network_port)})
docker_ports_description = vol.Schema({docker_port: vol.Coerce(str)})


# pylint: disable=no-value-for-parameter
SCHEMA_HASS_CONFIG = vol.Schema(
    {
        vol.Optional(ATTR_UUID, default=lambda: uuid.uuid4().hex): uuid_match,
        vol.Optional(ATTR_VERSION): version_tag,
        vol.Optional(ATTR_IMAGE): docker_image,
        vol.Optional(ATTR_ACCESS_TOKEN): token,
        vol.Optional(ATTR_BOOT, default=True): vol.Boolean(),
        vol.Optional(ATTR_PORT, default=8123): network_port,
        vol.Optional(ATTR_REFRESH_TOKEN): vol.Maybe(vol.Coerce(str)),
        vol.Optional(ATTR_SSL, default=False): vol.Boolean(),
        vol.Optional(ATTR_WATCHDOG, default=True): vol.Boolean(),
        vol.Optional(ATTR_WAIT_BOOT, default=600): vol.All(
            vol.Coerce(int), vol.Range(min=60)
        ),
        vol.Optional(ATTR_AUDIO_OUTPUT, default=None): vol.Maybe(vol.Coerce(str)),
        vol.Optional(ATTR_AUDIO_INPUT, default=None): vol.Maybe(vol.Coerce(str)),
    },
    extra=vol.REMOVE_EXTRA,
)


# pylint: disable=no-value-for-parameter
SCHEMA_UPDATER_CONFIG = vol.Schema(
    {
        vol.Optional(ATTR_CHANNEL, default=UpdateChannel.STABLE): vol.Coerce(
            UpdateChannel
        ),
        vol.Optional(ATTR_HOMEASSISTANT): version_tag,
        vol.Optional(ATTR_SUPERVISOR): version_tag,
        vol.Optional(ATTR_HASSOS): version_tag,
        vol.Optional(ATTR_CLI): version_tag,
        vol.Optional(ATTR_DNS): version_tag,
        vol.Optional(ATTR_AUDIO): version_tag,
        vol.Optional(ATTR_OBSERVER): version_tag,
        vol.Optional(ATTR_MULTICAST): version_tag,
        vol.Optional(ATTR_IMAGE, default=dict): vol.Schema(
            {
                vol.Optional(ATTR_HOMEASSISTANT): docker_image,
                vol.Optional(ATTR_SUPERVISOR): docker_image,
                vol.Optional(ATTR_CLI): docker_image,
                vol.Optional(ATTR_DNS): docker_image,
                vol.Optional(ATTR_AUDIO): docker_image,
                vol.Optional(ATTR_OBSERVER): docker_image,
                vol.Optional(ATTR_MULTICAST): docker_image,
            },
            extra=vol.REMOVE_EXTRA,
        ),
        vol.Optional(ATTR_OTA): vol.Url(),
    },
    extra=vol.REMOVE_EXTRA,
)


# pylint: disable=no-value-for-parameter
SCHEMA_SUPERVISOR_CONFIG = vol.Schema(
    {
        vol.Optional(ATTR_TIMEZONE, default="UTC"): validate_timezone,
        vol.Optional(ATTR_LAST_BOOT): vol.Coerce(str),
        vol.Optional(
            ATTR_VERSION, default=AwesomeVersion(SUPERVISOR_VERSION)
        ): version_tag,
        vol.Optional(
            ATTR_ADDONS_CUSTOM_LIST,
            default=["https://github.com/hassio-addons/repository"],
        ): repositories,
        vol.Optional(ATTR_WAIT_BOOT, default=5): wait_boot,
        vol.Optional(ATTR_LOGGING, default=LogLevel.INFO): vol.Coerce(LogLevel),
        vol.Optional(ATTR_DEBUG, default=False): vol.Boolean(),
        vol.Optional(ATTR_DEBUG_BLOCK, default=False): vol.Boolean(),
        vol.Optional(ATTR_DIAGNOSTICS, default=None): vol.Maybe(vol.Boolean()),
    },
    extra=vol.REMOVE_EXTRA,
)


SCHEMA_DOCKER_CONFIG = vol.Schema(
    {
        vol.Optional(ATTR_REGISTRIES, default=dict): vol.Schema(
            {
                vol.All(str, vol.Match(RE_REGISTRY)): {
                    vol.Required(ATTR_USERNAME): str,
                    vol.Required(ATTR_PASSWORD): str,
                }
            }
        )
    }
)


SCHEMA_AUTH_CONFIG = vol.Schema({sha256: sha256})


SCHEMA_INGRESS_CONFIG = vol.Schema(
    {
        vol.Required(ATTR_SESSION, default=dict): vol.Schema(
            {token: vol.Coerce(float)}
        ),
        vol.Required(ATTR_PORTS, default=dict): vol.Schema(
            {vol.Coerce(str): network_port}
        ),
    },
    extra=vol.REMOVE_EXTRA,
)
