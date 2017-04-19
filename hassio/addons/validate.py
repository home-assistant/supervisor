"""Validate addons options schema."""
import voluptuous as vol

from ..const import (
    ATTR_NAME, ATTR_VERSION, ATTR_SLUG, ATTR_DESCRIPTON, ATTR_STARTUP,
    ATTR_BOOT, ATTR_MAP_SSL, ATTR_MAP_CONFIG, ATTR_OPTIONS,
    ATTR_PORTS, STARTUP_ONCE, STARTUP_AFTER, STARTUP_BEFORE, BOOT_AUTO,
    BOOT_MANUAL, ATTR_SCHEMA, ATTR_IMAGE, ATTR_MAP_HASSIO)

V_STR = 'str'
V_INT = 'int'
V_FLOAT = 'float'
V_BOOL = 'bool'
V_EMAIL = 'email'
V_URL = 'url'

ADDON_ELEMENT = vol.In([V_STR, V_INT, V_FLOAT, V_BOOL, V_EMAIL, V_URL])

# pylint: disable=no-value-for-parameter
SCHEMA_ADDON_CONFIG = vol.Schema({
    vol.Required(ATTR_NAME): vol.Coerce(str),
    vol.Required(ATTR_VERSION): vol.Coerce(str),
    vol.Required(ATTR_SLUG): vol.Coerce(str),
    vol.Required(ATTR_DESCRIPTON): vol.Coerce(str),
    vol.Required(ATTR_STARTUP):
        vol.In([STARTUP_BEFORE, STARTUP_AFTER, STARTUP_ONCE]),
    vol.Required(ATTR_BOOT):
        vol.In([BOOT_AUTO, BOOT_MANUAL]),
    vol.Optional(ATTR_PORTS): dict,
    vol.Optional(ATTR_MAP_CONFIG, default=False): vol.Boolean(),
    vol.Optional(ATTR_MAP_SSL, default=False): vol.Boolean(),
    vol.Optional(ATTR_MAP_HASSIO, default=False): vol.Boolean(),
    vol.Required(ATTR_OPTIONS): dict,
    vol.Required(ATTR_SCHEMA): {
        vol.Coerce(str): vol.Any(ADDON_ELEMENT, [
            vol.Any(ADDON_ELEMENT, {vol.Coerce(str): ADDON_ELEMENT})
        ])
    },
    vol.Optional(ATTR_IMAGE): vol.Match(r"\w*/\w*"),
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
                    options[key] = _nested_validate(typ[0], value)
                else:
                    # normal value
                    options[key] = _single_validate(typ, value)
            except (IndexError, KeyError):
                raise vol.Invalid(
                    "Type error for {}.".format(key)) from None

        return options

    return validate


# pylint: disable=no-value-for-parameter
def _single_validate(typ, value):
    """Validate a single element."""
    try:
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

        raise vol.Invalid("Fatal error for {}.".format(value))
    except TypeError:
        raise vol.Invalid(
            "Type {} error for {}.".format(typ, value)) from None


def _nested_validate(typ, data_list):
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

                c_options[c_key] = _single_validate(typ[c_key], c_value)
            options.append(c_options)
        # normal list
        else:
            options.append(_single_validate(typ, element))

    return options
