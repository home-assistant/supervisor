"""Validate add-ons options schema."""
import logging
import re
import secrets
from typing import Any, Dict, List, Union
import uuid

import voluptuous as vol

from ..const import (
    ARCH_ALL,
    ATTR_ACCESS_TOKEN,
    ATTR_ADVANCED,
    ATTR_APPARMOR,
    ATTR_ARCH,
    ATTR_ARGS,
    ATTR_AUDIO,
    ATTR_AUDIO_INPUT,
    ATTR_AUDIO_OUTPUT,
    ATTR_AUTH_API,
    ATTR_AUTO_UART,
    ATTR_AUTO_UPDATE,
    ATTR_BOOT,
    ATTR_BUILD_FROM,
    ATTR_DESCRIPTON,
    ATTR_DEVICES,
    ATTR_DEVICETREE,
    ATTR_DISCOVERY,
    ATTR_DOCKER_API,
    ATTR_ENVIRONMENT,
    ATTR_FULL_ACCESS,
    ATTR_GPIO,
    ATTR_HASSIO_API,
    ATTR_HASSIO_ROLE,
    ATTR_HOMEASSISTANT,
    ATTR_HOMEASSISTANT_API,
    ATTR_HOST_DBUS,
    ATTR_HOST_IPC,
    ATTR_HOST_NETWORK,
    ATTR_HOST_PID,
    ATTR_IMAGE,
    ATTR_INGRESS,
    ATTR_INGRESS_ENTRY,
    ATTR_INGRESS_PANEL,
    ATTR_INGRESS_PORT,
    ATTR_INGRESS_TOKEN,
    ATTR_INIT,
    ATTR_KERNEL_MODULES,
    ATTR_LEGACY,
    ATTR_LOCATON,
    ATTR_MACHINE,
    ATTR_MAP,
    ATTR_NAME,
    ATTR_NETWORK,
    ATTR_OPTIONS,
    ATTR_PANEL_ADMIN,
    ATTR_PANEL_ICON,
    ATTR_PANEL_TITLE,
    ATTR_PORTS,
    ATTR_PORTS_DESCRIPTION,
    ATTR_PRIVILEGED,
    ATTR_PROTECTED,
    ATTR_REPOSITORY,
    ATTR_SCHEMA,
    ATTR_SERVICES,
    ATTR_SLUG,
    ATTR_SNAPSHOT_EXCLUDE,
    ATTR_SQUASH,
    ATTR_STAGE,
    ATTR_STARTUP,
    ATTR_STATE,
    ATTR_STDIN,
    ATTR_SYSTEM,
    ATTR_TIMEOUT,
    ATTR_TMPFS,
    ATTR_UDEV,
    ATTR_URL,
    ATTR_USB,
    ATTR_USER,
    ATTR_UUID,
    ATTR_VERSION,
    ATTR_VIDEO,
    ATTR_WATCHDOG,
    ATTR_WEBUI,
    BOOT_AUTO,
    BOOT_MANUAL,
    PRIVILEGED_ALL,
    ROLE_ALL,
    ROLE_DEFAULT,
    STATE_STARTED,
    STATE_STOPPED,
    AddonStages,
    AddonStartup,
)
from ..coresys import CoreSys
from ..discovery.validate import valid_discovery_service
from ..validate import (
    docker_ports,
    docker_ports_description,
    network_port,
    token,
    uuid_match,
    version_tag,
)

_LOGGER: logging.Logger = logging.getLogger(__name__)


RE_VOLUME = re.compile(r"^(config|ssl|addons|backup|share)(?::(rw|ro))?$")
RE_SERVICE = re.compile(r"^(?P<service>mqtt|mysql):(?P<rights>provide|want|need)$")

V_STR = "str"
V_INT = "int"
V_FLOAT = "float"
V_BOOL = "bool"
V_PASSWORD = "password"
V_EMAIL = "email"
V_URL = "url"
V_PORT = "port"
V_MATCH = "match"
V_LIST = "list"

RE_SCHEMA_ELEMENT = re.compile(
    r"^(?:"
    r"|bool"
    r"|email"
    r"|url"
    r"|port"
    r"|str(?:\((?P<s_min>\d+)?,(?P<s_max>\d+)?\))?"
    r"|password(?:\((?P<p_min>\d+)?,(?P<p_max>\d+)?\))?"
    r"|int(?:\((?P<i_min>\d+)?,(?P<i_max>\d+)?\))?"
    r"|float(?:\((?P<f_min>[\d\.]+)?,(?P<f_max>[\d\.]+)?\))?"
    r"|match\((?P<match>.*)\)"
    r"|list\((?P<list>.+)\)"
    r")\??$"
)

_SCHEMA_LENGTH_PARTS = (
    "i_min",
    "i_max",
    "f_min",
    "f_max",
    "s_min",
    "s_max",
    "p_min",
    "p_max",
)

RE_DOCKER_IMAGE = re.compile(r"^([a-zA-Z\-\.:\d{}]+/)*?([\-\w{}]+)/([\-\w{}]+)$")
RE_DOCKER_IMAGE_BUILD = re.compile(
    r"^([a-zA-Z\-\.:\d{}]+/)*?([\-\w{}]+)/([\-\w{}]+)(:[\.\-\w{}]+)?$"
)

SCHEMA_ELEMENT = vol.Match(RE_SCHEMA_ELEMENT)

RE_MACHINE = re.compile(
    r"^!?(?:"
    r"|intel-nuc"
    r"|odroid-c2"
    r"|odroid-n2"
    r"|odroid-xu"
    r"|qemuarm-64"
    r"|qemuarm"
    r"|qemux86-64"
    r"|qemux86"
    r"|raspberrypi"
    r"|raspberrypi2"
    r"|raspberrypi3-64"
    r"|raspberrypi3"
    r"|raspberrypi4-64"
    r"|raspberrypi4"
    r"|tinker"
    r")$"
)


def _simple_startup(value) -> str:
    """Define startup schema."""
    if value == "before":
        return AddonStartup.SERVICES.value
    if value == "after":
        return AddonStartup.APPLICATION.value
    return value


# pylint: disable=no-value-for-parameter
SCHEMA_ADDON_CONFIG = vol.Schema(
    {
        vol.Required(ATTR_NAME): vol.Coerce(str),
        vol.Required(ATTR_VERSION): vol.All(version_tag, str),
        vol.Required(ATTR_SLUG): vol.Coerce(str),
        vol.Required(ATTR_DESCRIPTON): vol.Coerce(str),
        vol.Required(ATTR_ARCH): [vol.In(ARCH_ALL)],
        vol.Optional(ATTR_MACHINE): vol.All([vol.Match(RE_MACHINE)], vol.Unique()),
        vol.Optional(ATTR_URL): vol.Url(),
        vol.Required(ATTR_STARTUP): vol.All(_simple_startup, vol.Coerce(AddonStartup)),
        vol.Required(ATTR_BOOT): vol.In([BOOT_AUTO, BOOT_MANUAL]),
        vol.Optional(ATTR_INIT, default=True): vol.Boolean(),
        vol.Optional(ATTR_ADVANCED, default=False): vol.Boolean(),
        vol.Optional(ATTR_STAGE, default=AddonStages.STABLE): vol.Coerce(AddonStages),
        vol.Optional(ATTR_PORTS): docker_ports,
        vol.Optional(ATTR_PORTS_DESCRIPTION): docker_ports_description,
        vol.Optional(ATTR_WATCHDOG): vol.Match(
            r"^(?:https?|\[PROTO:\w+\]|tcp):\/\/\[HOST\]:\[PORT:\d+\].*$"
        ),
        vol.Optional(ATTR_WEBUI): vol.Match(
            r"^(?:https?|\[PROTO:\w+\]):\/\/\[HOST\]:\[PORT:\d+\].*$"
        ),
        vol.Optional(ATTR_INGRESS, default=False): vol.Boolean(),
        vol.Optional(ATTR_INGRESS_PORT, default=8099): vol.Any(
            network_port, vol.Equal(0)
        ),
        vol.Optional(ATTR_INGRESS_ENTRY): vol.Coerce(str),
        vol.Optional(ATTR_PANEL_ICON, default="mdi:puzzle"): vol.Coerce(str),
        vol.Optional(ATTR_PANEL_TITLE): vol.Coerce(str),
        vol.Optional(ATTR_PANEL_ADMIN, default=True): vol.Boolean(),
        vol.Optional(ATTR_HOMEASSISTANT): vol.Maybe(vol.Coerce(str)),
        vol.Optional(ATTR_HOST_NETWORK, default=False): vol.Boolean(),
        vol.Optional(ATTR_HOST_PID, default=False): vol.Boolean(),
        vol.Optional(ATTR_HOST_IPC, default=False): vol.Boolean(),
        vol.Optional(ATTR_HOST_DBUS, default=False): vol.Boolean(),
        vol.Optional(ATTR_DEVICES): [vol.Match(r"^(.*):(.*):([rwm]{1,3})$")],
        vol.Optional(ATTR_AUTO_UART, default=False): vol.Boolean(),
        vol.Optional(ATTR_UDEV, default=False): vol.Boolean(),
        vol.Optional(ATTR_TMPFS): vol.Match(r"^size=(\d)*[kmg](,uid=\d{1,4})?(,rw)?$"),
        vol.Optional(ATTR_MAP, default=list): [vol.Match(RE_VOLUME)],
        vol.Optional(ATTR_ENVIRONMENT): {vol.Match(r"\w*"): vol.Coerce(str)},
        vol.Optional(ATTR_PRIVILEGED): [vol.In(PRIVILEGED_ALL)],
        vol.Optional(ATTR_APPARMOR, default=True): vol.Boolean(),
        vol.Optional(ATTR_FULL_ACCESS, default=False): vol.Boolean(),
        vol.Optional(ATTR_AUDIO, default=False): vol.Boolean(),
        vol.Optional(ATTR_VIDEO, default=False): vol.Boolean(),
        vol.Optional(ATTR_GPIO, default=False): vol.Boolean(),
        vol.Optional(ATTR_USB, default=False): vol.Boolean(),
        vol.Optional(ATTR_DEVICETREE, default=False): vol.Boolean(),
        vol.Optional(ATTR_KERNEL_MODULES, default=False): vol.Boolean(),
        vol.Optional(ATTR_HASSIO_API, default=False): vol.Boolean(),
        vol.Optional(ATTR_HASSIO_ROLE, default=ROLE_DEFAULT): vol.In(ROLE_ALL),
        vol.Optional(ATTR_HOMEASSISTANT_API, default=False): vol.Boolean(),
        vol.Optional(ATTR_STDIN, default=False): vol.Boolean(),
        vol.Optional(ATTR_LEGACY, default=False): vol.Boolean(),
        vol.Optional(ATTR_DOCKER_API, default=False): vol.Boolean(),
        vol.Optional(ATTR_AUTH_API, default=False): vol.Boolean(),
        vol.Optional(ATTR_SERVICES): [vol.Match(RE_SERVICE)],
        vol.Optional(ATTR_DISCOVERY): [valid_discovery_service],
        vol.Optional(ATTR_SNAPSHOT_EXCLUDE): [vol.Coerce(str)],
        vol.Required(ATTR_OPTIONS): dict,
        vol.Required(ATTR_SCHEMA): vol.Any(
            vol.Schema(
                {
                    vol.Coerce(str): vol.Any(
                        SCHEMA_ELEMENT,
                        [
                            vol.Any(
                                SCHEMA_ELEMENT,
                                {
                                    vol.Coerce(str): vol.Any(
                                        SCHEMA_ELEMENT, [SCHEMA_ELEMENT]
                                    )
                                },
                            )
                        ],
                        vol.Schema(
                            {vol.Coerce(str): vol.Any(SCHEMA_ELEMENT, [SCHEMA_ELEMENT])}
                        ),
                    )
                }
            ),
            False,
        ),
        vol.Optional(ATTR_IMAGE): vol.Match(RE_DOCKER_IMAGE),
        vol.Optional(ATTR_TIMEOUT, default=10): vol.All(
            vol.Coerce(int), vol.Range(min=10, max=300)
        ),
    },
    extra=vol.REMOVE_EXTRA,
)


# pylint: disable=no-value-for-parameter
SCHEMA_BUILD_CONFIG = vol.Schema(
    {
        vol.Optional(ATTR_BUILD_FROM, default=dict): vol.Schema(
            {vol.In(ARCH_ALL): vol.Match(RE_DOCKER_IMAGE_BUILD)}
        ),
        vol.Optional(ATTR_SQUASH, default=False): vol.Boolean(),
        vol.Optional(ATTR_ARGS, default=dict): vol.Schema(
            {vol.Coerce(str): vol.Coerce(str)}
        ),
    },
    extra=vol.REMOVE_EXTRA,
)


# pylint: disable=no-value-for-parameter
SCHEMA_ADDON_USER = vol.Schema(
    {
        vol.Required(ATTR_VERSION): vol.Coerce(str),
        vol.Optional(ATTR_IMAGE): vol.Coerce(str),
        vol.Optional(ATTR_UUID, default=lambda: uuid.uuid4().hex): uuid_match,
        vol.Optional(ATTR_ACCESS_TOKEN): token,
        vol.Optional(ATTR_INGRESS_TOKEN, default=secrets.token_urlsafe): vol.Coerce(
            str
        ),
        vol.Optional(ATTR_OPTIONS, default=dict): dict,
        vol.Optional(ATTR_AUTO_UPDATE, default=False): vol.Boolean(),
        vol.Optional(ATTR_BOOT): vol.In([BOOT_AUTO, BOOT_MANUAL]),
        vol.Optional(ATTR_NETWORK): docker_ports,
        vol.Optional(ATTR_AUDIO_OUTPUT): vol.Maybe(vol.Coerce(str)),
        vol.Optional(ATTR_AUDIO_INPUT): vol.Maybe(vol.Coerce(str)),
        vol.Optional(ATTR_PROTECTED, default=True): vol.Boolean(),
        vol.Optional(ATTR_INGRESS_PANEL, default=False): vol.Boolean(),
        vol.Optional(ATTR_WATCHDOG, default=False): vol.Boolean(),
    },
    extra=vol.REMOVE_EXTRA,
)


SCHEMA_ADDON_SYSTEM = SCHEMA_ADDON_CONFIG.extend(
    {
        vol.Required(ATTR_LOCATON): vol.Coerce(str),
        vol.Required(ATTR_REPOSITORY): vol.Coerce(str),
    }
)


SCHEMA_ADDONS_FILE = vol.Schema(
    {
        vol.Optional(ATTR_USER, default=dict): {vol.Coerce(str): SCHEMA_ADDON_USER},
        vol.Optional(ATTR_SYSTEM, default=dict): {vol.Coerce(str): SCHEMA_ADDON_SYSTEM},
    }
)


SCHEMA_ADDON_SNAPSHOT = vol.Schema(
    {
        vol.Required(ATTR_USER): SCHEMA_ADDON_USER,
        vol.Required(ATTR_SYSTEM): SCHEMA_ADDON_SYSTEM,
        vol.Required(ATTR_STATE): vol.In([STATE_STARTED, STATE_STOPPED]),
        vol.Required(ATTR_VERSION): vol.Coerce(str),
    },
    extra=vol.REMOVE_EXTRA,
)


def validate_options(coresys: CoreSys, raw_schema: Dict[str, Any]):
    """Validate schema."""

    def validate(struct):
        """Create schema validator for add-ons options."""
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
                    options[key] = _nested_validate_list(coresys, typ[0], value, key)
                elif isinstance(typ, dict):
                    # nested value dict
                    options[key] = _nested_validate_dict(coresys, typ, value, key)
                else:
                    # normal value
                    options[key] = _single_validate(coresys, typ, value, key)
            except (IndexError, KeyError):
                raise vol.Invalid(f"Type error for {key}") from None

        _check_missing_options(raw_schema, options, "root")
        return options

    return validate


# pylint: disable=no-value-for-parameter
# pylint: disable=inconsistent-return-statements
def _single_validate(coresys: CoreSys, typ: str, value: Any, key: str):
    """Validate a single element."""
    # if required argument
    if value is None:
        raise vol.Invalid(f"Missing required option '{key}'") from None

    # Lookup secret
    if str(value).startswith("!secret "):
        secret: str = value.partition(" ")[2]
        value = coresys.secrets.get(secret)
        if value is None:
            raise vol.Invalid(f"Unknown secret {secret}") from None

    # parse extend data from type
    match = RE_SCHEMA_ELEMENT.match(typ)

    if not match:
        raise vol.Invalid(f"Unknown type {typ}") from None

    # prepare range
    range_args = {}
    for group_name in _SCHEMA_LENGTH_PARTS:
        group_value = match.group(group_name)
        if group_value:
            range_args[group_name[2:]] = float(group_value)

    if typ.startswith(V_STR) or typ.startswith(V_PASSWORD):
        return vol.All(str(value), vol.Range(**range_args))(value)
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
        return network_port(value)
    elif typ.startswith(V_MATCH):
        return vol.Match(match.group("match"))(str(value))
    elif typ.startswith(V_LIST):
        return vol.In(match.group("list").split("|"))(str(value))

    raise vol.Invalid(f"Fatal error for {key} type {typ}") from None


def _nested_validate_list(coresys, typ, data_list, key):
    """Validate nested items."""
    options = []

    # Make sure it is a list
    if not isinstance(data_list, list):
        raise vol.Invalid(f"Invalid list for {key}") from None

    # Process list
    for element in data_list:
        # Nested?
        if isinstance(typ, dict):
            c_options = _nested_validate_dict(coresys, typ, element, key)
            options.append(c_options)
        else:
            options.append(_single_validate(coresys, typ, element, key))

    return options


def _nested_validate_dict(coresys, typ, data_dict, key):
    """Validate nested items."""
    options = {}

    # Make sure it is a dict
    if not isinstance(data_dict, dict):
        raise vol.Invalid(f"Invalid dict for {key}") from None

    # Process dict
    for c_key, c_value in data_dict.items():
        # Ignore unknown options / remove from list
        if c_key not in typ:
            _LOGGER.warning("Unknown options %s", c_key)
            continue

        # Nested?
        if isinstance(typ[c_key], list):
            options[c_key] = _nested_validate_list(
                coresys, typ[c_key][0], c_value, c_key
            )
        else:
            options[c_key] = _single_validate(coresys, typ[c_key], c_value, c_key)

    _check_missing_options(typ, options, key)
    return options


def _check_missing_options(origin, exists, root):
    """Check if all options are exists."""
    missing = set(origin) - set(exists)
    for miss_opt in missing:
        if isinstance(origin[miss_opt], str) and origin[miss_opt].endswith("?"):
            continue
        raise vol.Invalid(f"Missing option {miss_opt} in {root}") from None


def schema_ui_options(raw_schema: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Generate UI schema."""
    ui_schema: List[Dict[str, Any]] = []

    # read options
    for key, value in raw_schema.items():
        if isinstance(value, list):
            # nested value list
            _nested_ui_list(ui_schema, value, key)
        elif isinstance(value, dict):
            # nested value dict
            _nested_ui_dict(ui_schema, value, key)
        else:
            # normal value
            _single_ui_option(ui_schema, value, key)

    return ui_schema


def _single_ui_option(
    ui_schema: List[Dict[str, Any]], value: str, key: str, multiple: bool = False
) -> None:
    """Validate a single element."""
    ui_node: Dict[str, Union[str, bool, float, List[str]]] = {"name": key}

    # If multiple
    if multiple:
        ui_node["multiple"] = True

    # Parse extend data from type
    match = RE_SCHEMA_ELEMENT.match(value)
    if not match:
        return

    # Prepare range
    for group_name in _SCHEMA_LENGTH_PARTS:
        group_value = match.group(group_name)
        if not group_value:
            continue
        if group_name[2:] == "min":
            ui_node["lengthMin"] = float(group_value)
        elif group_name[2:] == "max":
            ui_node["lengthMax"] = float(group_value)

    # If required
    if value.endswith("?"):
        ui_node["optional"] = True
    else:
        ui_node["required"] = True

    # Data types
    if value.startswith(V_STR):
        ui_node["type"] = "string"
    elif value.startswith(V_PASSWORD):
        ui_node["type"] = "string"
        ui_node["format"] = "password"
    elif value.startswith(V_INT):
        ui_node["type"] = "integer"
    elif value.startswith(V_FLOAT):
        ui_node["type"] = "float"
    elif value.startswith(V_BOOL):
        ui_node["type"] = "boolean"
    elif value.startswith(V_EMAIL):
        ui_node["type"] = "string"
        ui_node["format"] = "email"
    elif value.startswith(V_URL):
        ui_node["type"] = "string"
        ui_node["format"] = "url"
    elif value.startswith(V_PORT):
        ui_node["type"] = "integer"
    elif value.startswith(V_MATCH):
        ui_node["type"] = "string"
    elif value.startswith(V_LIST):
        ui_node["type"] = "select"
        ui_node["options"] = match.group("list").split("|")

    ui_schema.append(ui_node)


def _nested_ui_list(
    ui_schema: List[Dict[str, Any]], option_list: List[Any], key: str
) -> None:
    """UI nested list items."""
    try:
        element = option_list[0]
    except IndexError:
        _LOGGER.error("Invalid schema %s", key)
        return

    if isinstance(element, dict):
        _nested_ui_dict(ui_schema, element, key, multiple=True)
    else:
        _single_ui_option(ui_schema, element, key, multiple=True)


def _nested_ui_dict(
    ui_schema: List[Dict[str, Any]],
    option_dict: Dict[str, Any],
    key: str,
    multiple: bool = False,
) -> None:
    """UI nested dict items."""
    ui_node = {"name": key, "type": "schema", "optional": True, "multiple": multiple}

    nested_schema = []
    for c_key, c_value in option_dict.items():
        # Nested?
        if isinstance(c_value, list):
            _nested_ui_list(nested_schema, c_value, c_key)
        else:
            _single_ui_option(nested_schema, c_value, c_key)

    ui_node["schema"] = nested_schema
    ui_schema.append(ui_node)
