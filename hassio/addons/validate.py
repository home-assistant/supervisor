"""Validate addons options schema."""
import voluptuous as vol

from ..const import (
    ATTR_NAME, ATTR_VERSION, ATTR_SLUG, ATTR_DESCRIPTON, ATTR_STARTUP,
    ATTR_BOOT, ATTR_MAP, ATTR_OPTIONS, ATTR_PORTS, STARTUP_ONCE, STARTUP_AFTER,
    STARTUP_BEFORE, STARTUP_INITIALIZE, BOOT_AUTO, BOOT_MANUAL, ATTR_SCHEMA,
    ATTR_IMAGE, ATTR_URL, ATTR_MAINTAINER, ATTR_ARCH, ATTR_DEVICES,
    ATTR_ENVIRONMENT, ATTR_HOST_NETWORK, ARCH_ARMHF, ARCH_AARCH64, ARCH_AMD64,
    ARCH_I386, ATTR_TMPFS, ATTR_PRIVILEGED, CONF_USER, CONF_STATE, CONF_SYSTEM,
    CONF_VERSION, STATE_STARTED, STATE_STOPPED, ATTR_LOCATON, ATTR_REPOSITORY)


MAP_VOLUME = r"^(config|ssl|addons|backup|share)(?::(rw|:ro))?$"

V_STR = 'str'
V_INT = 'int'
V_FLOAT = 'float'
V_BOOL = 'bool'
V_EMAIL = 'email'
V_URL = 'url'

ADDON_ELEMENT = vol.In([V_STR, V_INT, V_FLOAT, V_BOOL, V_EMAIL, V_URL])

ARCH_ALL = [
    ARCH_ARMHF, ARCH_AARCH64, ARCH_AMD64, ARCH_I386
]

PRIVILEGE_ALL = [
    "NET_ADMIN"
]


def check_network(data):
    """Validate network settings."""
    host_network = data[ATTR_HOST_NETWORK]

    if ATTR_PORTS in data and host_network:
        raise vol.Invalid("Hostnetwork & ports are not allow!")

    return data


# pylint: disable=no-value-for-parameter
SCHEMA_ADDON_CONFIG = vol.Schema(vol.All({
    vol.Required(ATTR_NAME): vol.Coerce(str),
    vol.Required(ATTR_VERSION): vol.Coerce(str),
    vol.Required(ATTR_SLUG): vol.Coerce(str),
    vol.Required(ATTR_DESCRIPTON): vol.Coerce(str),
    vol.Optional(ATTR_URL): vol.Url(),
    vol.Optional(ATTR_ARCH, default=ARCH_ALL): [vol.In(ARCH_ALL)],
    vol.Required(ATTR_STARTUP):
        vol.In([STARTUP_BEFORE, STARTUP_AFTER, STARTUP_ONCE,
                STARTUP_INITIALIZE]),
    vol.Required(ATTR_BOOT):
        vol.In([BOOT_AUTO, BOOT_MANUAL]),
    vol.Optional(ATTR_PORTS): dict,
    vol.Optional(ATTR_HOST_NETWORK, default=False): vol.Boolean(),
    vol.Optional(ATTR_DEVICES): [vol.Match(r"^(.*):(.*):([rwm]{1,3})$")],
    vol.Optional(ATTR_TMPFS):
        vol.Match(r"^size=(\d)*[kmg](,uid=\d{1,4})?(,rw)?$"),
    vol.Optional(ATTR_MAP, default=[]): [vol.Match(MAP_VOLUME)],
    vol.Optional(ATTR_ENVIRONMENT): {vol.Match(r"\w*"): vol.Coerce(str)},
    vol.Optional(ATTR_PRIVILEGED): [vol.In(PRIVILEGE_ALL)],
    vol.Required(ATTR_OPTIONS): dict,
    vol.Required(ATTR_SCHEMA): vol.Any({
        vol.Coerce(str): vol.Any(ADDON_ELEMENT, [
            vol.Any(ADDON_ELEMENT, {vol.Coerce(str): ADDON_ELEMENT})
        ])
    }, False),
    vol.Optional(ATTR_IMAGE): vol.Match(r"\w*/\w*"),
}, check_network), extra=vol.ALLOW_EXTRA)


# pylint: disable=no-value-for-parameter
SCHEMA_REPOSITORY_CONFIG = vol.Schema({
    vol.Required(ATTR_NAME): vol.Coerce(str),
    vol.Optional(ATTR_URL): vol.Url(),
    vol.Optional(ATTR_MAINTAINER): vol.Coerce(str),
}, extra=vol.ALLOW_EXTRA)


SCHEMA_ADDON_USER = vol.Schema({
    vol.Required(ATTR_VERSION): vol.Coerce(str),
    vol.Required(ATTR_OPTIONS): dict,
    vol.Optional(ATTR_BOOT):
        vol.In([BOOT_AUTO, BOOT_MANUAL]),
})


SCHEMA_ADDON_SYSTEM = SCHEMA_ADDON_USER.extend({
    vol.Required(ATTR_LOCATON): vol.Coerce(str),
    vol.Required(ATTR_REPOSITORY): vol.Coerce(str),
})


SCHEMA_ADDON_SNAPSHOT = vol.Schema({
    vol.Required(CONF_USER): SCHEMA_ADDON_USER,
    vol.Required(CONF_SYSTEM): SCHEMA_ADDON_SYSTEM,
    vol.Required(CONF_STATE): vol.In([STATE_STARTED, STATE_STOPPED]),
    vol.Required(CONF_VERSION): vol.Coerce(str),
})


def validate_options(raw_schema):
    """Validate schema."""
    def validate(struct):
        """Create schema validator for addons options."""
        options = {}

        # read options
        for key, value in struct.items():
            if key not in raw_schema:
                raise vol.Invalid("Unknown options {}.".format(key))

            typ = raw_schema[key]
            try:
                if isinstance(typ, list):
                    # nested value
                    options[key] = _nested_validate(typ[0], value, key)
                else:
                    # normal value
                    options[key] = _single_validate(typ, value, key)
            except (IndexError, KeyError):
                raise vol.Invalid(
                    "Type error for {}.".format(key)) from None

        return options

    return validate


# pylint: disable=no-value-for-parameter
def _single_validate(typ, value, key):
    """Validate a single element."""
    try:
        # if required argument
        if value is None:
            raise vol.Invalid("Missing required option '{}'.".format(key))

        if typ == V_STR:
            return str(value)
        elif typ == V_INT:
            return int(value)
        elif typ == V_FLOAT:
            return float(value)
        elif typ == V_BOOL:
            return vol.Boolean()(value)
        elif typ == V_EMAIL:
            return vol.Email()(value)
        elif typ == V_URL:
            return vol.Url()(value)

        raise vol.Invalid("Fatal error for {} type {}.".format(key, typ))
    except ValueError:
        raise vol.Invalid(
            "Type {} error for '{}' on {}.".format(typ, value, key)) from None


def _nested_validate(typ, data_list, key):
    """Validate nested items."""
    options = []

    for element in data_list:
        # dict list
        if isinstance(typ, dict):
            c_options = {}
            for c_key, c_value in element.items():
                if c_key not in typ:
                    raise vol.Invalid(
                        "Unknown nested options {}.".format(c_key))

                c_options[c_key] = _single_validate(typ[c_key], c_value, c_key)
            options.append(c_options)
        # normal list
        else:
            options.append(_single_validate(typ, element, key))

    return options
