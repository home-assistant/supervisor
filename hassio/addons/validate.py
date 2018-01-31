"""Validate addons options schema."""
import logging
import re
import uuid

import voluptuous as vol

from ..const import (
    ATTR_NAME, ATTR_VERSION, ATTR_SLUG, ATTR_DESCRIPTON, ATTR_STARTUP,
    ATTR_BOOT, ATTR_MAP, ATTR_OPTIONS, ATTR_PORTS, STARTUP_ONCE,
    STARTUP_SYSTEM, STARTUP_SERVICES, STARTUP_APPLICATION, STARTUP_INITIALIZE,
    BOOT_AUTO, BOOT_MANUAL, ATTR_SCHEMA, ATTR_IMAGE, ATTR_URL, ATTR_MAINTAINER,
    ATTR_ARCH, ATTR_DEVICES, ATTR_ENVIRONMENT, ATTR_HOST_NETWORK, ARCH_ARMHF,
    ARCH_AARCH64, ARCH_AMD64, ARCH_I386, ATTR_TMPFS, ATTR_PRIVILEGED,
    ATTR_USER, ATTR_STATE, ATTR_SYSTEM, STATE_STARTED, STATE_STOPPED,
    ATTR_LOCATON, ATTR_REPOSITORY, ATTR_TIMEOUT, ATTR_NETWORK, ATTR_UUID,
    ATTR_AUTO_UPDATE, ATTR_WEBUI, ATTR_AUDIO, ATTR_AUDIO_INPUT, ATTR_HOST_IPC,
    ATTR_AUDIO_OUTPUT, ATTR_HASSIO_API, ATTR_BUILD_FROM, ATTR_SQUASH,
    ATTR_ARGS, ATTR_GPIO, ATTR_HOMEASSISTANT_API, ATTR_STDIN, ATTR_LEGACY,
    ATTR_HOST_DBUS, ATTR_AUTO_UART)
from ..validate import NETWORK_PORT, DOCKER_PORTS, ALSA_CHANNEL

_LOGGER = logging.getLogger(__name__)


RE_VOLUME = re.compile(r"^(config|ssl|addons|backup|share)(?::(rw|:ro))?$")

V_STR = 'str'
V_INT = 'int'
V_FLOAT = 'float'
V_BOOL = 'bool'
V_EMAIL = 'email'
V_URL = 'url'
V_PORT = 'port'
V_MATCH = 'match'

RE_SCHEMA_ELEMENT = re.compile(
    r"^(?:"
    r"|str|bool|email|url|port"
    r"|int(?:\((?P<i_min>\d+)?,(?P<i_max>\d+)?\))?"
    r"|float(?:\((?P<f_min>[\d\.]+)?,(?P<f_max>[\d\.]+)?\))?"
    r"|match\((?P<match>.*)\)"
    r")\??$"
)

SCHEMA_ELEMENT = vol.Match(RE_SCHEMA_ELEMENT)

ARCH_ALL = [
    ARCH_ARMHF, ARCH_AARCH64, ARCH_AMD64, ARCH_I386
]

STARTUP_ALL = [
    STARTUP_ONCE, STARTUP_INITIALIZE, STARTUP_SYSTEM, STARTUP_SERVICES,
    STARTUP_APPLICATION
]

PRIVILEGED_ALL = [
    "NET_ADMIN",
    "SYS_ADMIN",
    "SYS_RAWIO",
    "SYS_TIME",
    "SYS_NICE"
]

BASE_IMAGE = {
    ARCH_ARMHF: "homeassistant/armhf-base:latest",
    ARCH_AARCH64: "homeassistant/aarch64-base:latest",
    ARCH_I386: "homeassistant/i386-base:latest",
    ARCH_AMD64: "homeassistant/amd64-base:latest",
}


def _simple_startup(value):
    """Simple startup schema."""
    if value == "before":
        return STARTUP_SERVICES
    if value == "after":
        return STARTUP_APPLICATION
    return value


# pylint: disable=no-value-for-parameter
SCHEMA_ADDON_CONFIG = vol.Schema({
    vol.Required(ATTR_NAME): vol.Coerce(str),
    vol.Required(ATTR_VERSION): vol.Coerce(str),
    vol.Required(ATTR_SLUG): vol.Coerce(str),
    vol.Required(ATTR_DESCRIPTON): vol.Coerce(str),
    vol.Optional(ATTR_URL): vol.Url(),
    vol.Optional(ATTR_ARCH, default=ARCH_ALL): [vol.In(ARCH_ALL)],
    vol.Required(ATTR_STARTUP):
        vol.All(_simple_startup, vol.In(STARTUP_ALL)),
    vol.Required(ATTR_BOOT):
        vol.In([BOOT_AUTO, BOOT_MANUAL]),
    vol.Optional(ATTR_PORTS): DOCKER_PORTS,
    vol.Optional(ATTR_WEBUI):
        vol.Match(r"^(?:https?|\[PROTO:\w+\]):\/\/\[HOST\]:\[PORT:\d+\].*$"),
    vol.Optional(ATTR_HOST_NETWORK, default=False): vol.Boolean(),
    vol.Optional(ATTR_HOST_IPC, default=False): vol.Boolean(),
    vol.Optional(ATTR_HOST_DBUS, default=False): vol.Boolean(),
    vol.Optional(ATTR_DEVICES): [vol.Match(r"^(.*):(.*):([rwm]{1,3})$")],
    vol.Optional(ATTR_AUTO_UART, default=False): vol.Boolean(),
    vol.Optional(ATTR_TMPFS):
        vol.Match(r"^size=(\d)*[kmg](,uid=\d{1,4})?(,rw)?$"),
    vol.Optional(ATTR_MAP, default=list): [vol.Match(RE_VOLUME)],
    vol.Optional(ATTR_ENVIRONMENT): {vol.Match(r"\w*"): vol.Coerce(str)},
    vol.Optional(ATTR_PRIVILEGED): [vol.In(PRIVILEGED_ALL)],
    vol.Optional(ATTR_AUDIO, default=False): vol.Boolean(),
    vol.Optional(ATTR_GPIO, default=False): vol.Boolean(),
    vol.Optional(ATTR_HASSIO_API, default=False): vol.Boolean(),
    vol.Optional(ATTR_HOMEASSISTANT_API, default=False): vol.Boolean(),
    vol.Optional(ATTR_STDIN, default=False): vol.Boolean(),
    vol.Optional(ATTR_LEGACY, default=False): vol.Boolean(),
    vol.Required(ATTR_OPTIONS): dict,
    vol.Required(ATTR_SCHEMA): vol.Any(vol.Schema({
        vol.Coerce(str): vol.Any(SCHEMA_ELEMENT, [
            vol.Any(
                SCHEMA_ELEMENT,
                {vol.Coerce(str): vol.Any(SCHEMA_ELEMENT, [SCHEMA_ELEMENT])}
            ),
        ], vol.Schema({
            vol.Coerce(str): vol.Any(SCHEMA_ELEMENT, [SCHEMA_ELEMENT])
        }))
    }), False),
    vol.Optional(ATTR_IMAGE): vol.Match(r"^[\w{}]+/[\-\w{}]+$"),
    vol.Optional(ATTR_TIMEOUT, default=10):
        vol.All(vol.Coerce(int), vol.Range(min=10, max=120)),
}, extra=vol.REMOVE_EXTRA)


# pylint: disable=no-value-for-parameter
SCHEMA_REPOSITORY_CONFIG = vol.Schema({
    vol.Required(ATTR_NAME): vol.Coerce(str),
    vol.Optional(ATTR_URL): vol.Url(),
    vol.Optional(ATTR_MAINTAINER): vol.Coerce(str),
}, extra=vol.REMOVE_EXTRA)


# pylint: disable=no-value-for-parameter
SCHEMA_BUILD_CONFIG = vol.Schema({
    vol.Optional(ATTR_BUILD_FROM, default=BASE_IMAGE): vol.Schema({
        vol.In(ARCH_ALL): vol.Match(r"(?:^[\w{}]+/)?[\-\w{}]+:[\.\-\w{}]+$"),
    }),
    vol.Optional(ATTR_SQUASH, default=False): vol.Boolean(),
    vol.Optional(ATTR_ARGS, default=dict): vol.Schema({
        vol.Coerce(str): vol.Coerce(str)
    }),
}, extra=vol.REMOVE_EXTRA)


# pylint: disable=no-value-for-parameter
SCHEMA_ADDON_USER = vol.Schema({
    vol.Required(ATTR_VERSION): vol.Coerce(str),
    vol.Optional(ATTR_UUID, default=lambda: uuid.uuid4().hex):
        vol.Match(r"^[0-9a-f]{32}$"),
    vol.Optional(ATTR_OPTIONS, default=dict): dict,
    vol.Optional(ATTR_AUTO_UPDATE, default=False): vol.Boolean(),
    vol.Optional(ATTR_BOOT):
        vol.In([BOOT_AUTO, BOOT_MANUAL]),
    vol.Optional(ATTR_NETWORK): DOCKER_PORTS,
    vol.Optional(ATTR_AUDIO_OUTPUT): ALSA_CHANNEL,
    vol.Optional(ATTR_AUDIO_INPUT): ALSA_CHANNEL,
}, extra=vol.REMOVE_EXTRA)


SCHEMA_ADDON_SYSTEM = SCHEMA_ADDON_CONFIG.extend({
    vol.Required(ATTR_LOCATON): vol.Coerce(str),
    vol.Required(ATTR_REPOSITORY): vol.Coerce(str),
})


SCHEMA_ADDONS_FILE = vol.Schema({
    vol.Optional(ATTR_USER, default=dict): {
        vol.Coerce(str): SCHEMA_ADDON_USER,
    },
    vol.Optional(ATTR_SYSTEM, default=dict): {
        vol.Coerce(str): SCHEMA_ADDON_SYSTEM,
    }
})


SCHEMA_ADDON_SNAPSHOT = vol.Schema({
    vol.Required(ATTR_USER): SCHEMA_ADDON_USER,
    vol.Required(ATTR_SYSTEM): SCHEMA_ADDON_SYSTEM,
    vol.Required(ATTR_STATE): vol.In([STATE_STARTED, STATE_STOPPED]),
    vol.Required(ATTR_VERSION): vol.Coerce(str),
}, extra=vol.REMOVE_EXTRA)


def validate_options(raw_schema):
    """Validate schema."""
    def validate(struct):
        """Create schema validator for addons options."""
        options = {}

        # read options
        for key, value in struct.items():
            # Ignore unknown options / remove from list
            if key not in raw_schema:
                _LOGGER.warning("Unknown options %s", key)
                continue

            typ = raw_schema[key]
            try:
                if isinstance(typ, list):
                    # nested value list
                    options[key] = _nested_validate_list(typ[0], value, key)
                elif isinstance(typ, dict):
                    # nested value dict
                    options[key] = _nested_validate_dict(typ, value, key)
                else:
                    # normal value
                    options[key] = _single_validate(typ, value, key)
            except (IndexError, KeyError):
                raise vol.Invalid(f"Type error for {key}") from None

        _check_missing_options(raw_schema, options, 'root')
        return options

    return validate


# pylint: disable=no-value-for-parameter
# pylint: disable=inconsistent-return-statements
def _single_validate(typ, value, key):
    """Validate a single element."""
    # if required argument
    if value is None:
        raise vol.Invalid(f"Missing required option '{key}'")

    # parse extend data from type
    match = RE_SCHEMA_ELEMENT.match(typ)

    # prepare range
    range_args = {}
    for group_name in ('i_min', 'i_max', 'f_min', 'f_max'):
        group_value = match.group(group_name)
        if group_value:
            range_args[group_name[2:]] = float(group_value)

    if typ.startswith(V_STR):
        return str(value)
    elif typ.startswith(V_INT):
        return vol.All(vol.Coerce(int), vol.Range(**range_args))(value)
    elif typ.startswith(V_FLOAT):
        return vol.All(vol.Coerce(float), vol.Range(**range_args))(value)
    elif typ.startswith(V_BOOL):
        return vol.Boolean()(value)
    elif typ.startswith(V_EMAIL):
        return vol.Email()(value)
    elif typ.startswith(V_URL):
        return vol.Url()(value)
    elif typ.startswith(V_PORT):
        return NETWORK_PORT(value)
    elif typ.startswith(V_MATCH):
        return vol.Match(match.group('match'))(str(value))

    raise vol.Invalid(f"Fatal error for {key} type {typ}")


def _nested_validate_list(typ, data_list, key):
    """Validate nested items."""
    options = []

    for element in data_list:
        # Nested?
        if isinstance(typ, dict):
            c_options = _nested_validate_dict(typ, element, key)
            options.append(c_options)
        else:
            options.append(_single_validate(typ, element, key))

    return options


def _nested_validate_dict(typ, data_dict, key):
    """Validate nested items."""
    options = {}

    for c_key, c_value in data_dict.items():
        # Ignore unknown options / remove from list
        if c_key not in typ:
            _LOGGER.warning("Unknown options %s", c_key)
            continue

        # Nested?
        if isinstance(typ[c_key], list):
            options[c_key] = _nested_validate_list(typ[c_key][0],
                                                   c_value, c_key)
        else:
            options[c_key] = _single_validate(typ[c_key], c_value, c_key)

    _check_missing_options(typ, options, key)
    return options


def _check_missing_options(origin, exists, root):
    """Check if all options are exists."""
    missing = set(origin) - set(exists)
    for miss_opt in missing:
        if isinstance(origin[miss_opt], str) and \
                origin[miss_opt].endswith("?"):
            continue
        raise vol.Invalid(f"Missing option {miss_opt} in {root}")
