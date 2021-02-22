"""Add-on Options / UI rendering."""
import logging
from pathlib import Path
import re
from typing import Any, Dict, List, Set, Union

import voluptuous as vol

from ..coresys import CoreSys, CoreSysAttributes
from ..exceptions import HardwareNotFound
from ..hardware.const import UdevSubsystem
from ..hardware.data import Device
from ..validate import network_port

_LOGGER: logging.Logger = logging.getLogger(__name__)

_STR = "str"
_INT = "int"
_FLOAT = "float"
_BOOL = "bool"
_PASSWORD = "password"
_EMAIL = "email"
_URL = "url"
_PORT = "port"
_MATCH = "match"
_LIST = "list"
_DEVICE = "device"

RE_SCHEMA_ELEMENT = re.compile(
    r"^(?:"
    r"|bool"
    r"|email"
    r"|url"
    r"|port"
    r"|device(?:\((?P<filter>subsystem=[a-z]+)\))?"
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


class AddonOptions(CoreSysAttributes):
    """Validate Add-ons Options."""

    def __init__(
        self, coresys: CoreSys, raw_schema: Dict[str, Any], name: str, slug: str
    ):
        """Validate schema."""
        self.coresys: CoreSys = coresys
        self.raw_schema: Dict[str, Any] = raw_schema
        self.devices: Set[Device] = set()
        self._name = name
        self._slug = slug

    def __call__(self, struct):
        """Create schema validator for add-ons options."""
        options = {}

        # read options
        for key, value in struct.items():
            # Ignore unknown options / remove from list
            if key not in self.raw_schema:
                _LOGGER.warning(
                    "Option '%s' does not exsist in the schema for %s (%s)",
                    key,
                    self._name,
                    self._slug,
                )
                continue

            typ = self.raw_schema[key]
            try:
                if isinstance(typ, list):
                    # nested value list
                    options[key] = self._nested_validate_list(typ[0], value, key)
                elif isinstance(typ, dict):
                    # nested value dict
                    options[key] = self._nested_validate_dict(typ, value, key)
                else:
                    # normal value
                    options[key] = self._single_validate(typ, value, key)
            except (IndexError, KeyError):
                raise vol.Invalid(
                    f"Type error for option '{key}' in {self._name} ({self._slug})"
                ) from None

        self._check_missing_options(self.raw_schema, options, "root")
        return options

    # pylint: disable=no-value-for-parameter
    def _single_validate(self, typ: str, value: Any, key: str):
        """Validate a single element."""
        # if required argument
        if value is None:
            raise vol.Invalid(
                f"Missing required option '{key}' in {self._name} ({self._slug})"
            ) from None

        # Lookup secret
        if str(value).startswith("!secret "):
            secret: str = value.partition(" ")[2]
            value = self.sys_homeassistant.secrets.get(secret)
            if value is None:
                raise vol.Invalid(
                    f"Unknown secret '{secret}' in {self._name} ({self._slug})"
                ) from None

        # parse extend data from type
        match = RE_SCHEMA_ELEMENT.match(typ)

        if not match:
            raise vol.Invalid(
                f"Unknown type '{typ}' in {self._name} ({self._slug})"
            ) from None

        # prepare range
        range_args = {}
        for group_name in _SCHEMA_LENGTH_PARTS:
            group_value = match.group(group_name)
            if group_value:
                range_args[group_name[2:]] = float(group_value)

        if typ.startswith(_STR) or typ.startswith(_PASSWORD):
            return vol.All(str(value), vol.Range(**range_args))(value)
        elif typ.startswith(_INT):
            return vol.All(vol.Coerce(int), vol.Range(**range_args))(value)
        elif typ.startswith(_FLOAT):
            return vol.All(vol.Coerce(float), vol.Range(**range_args))(value)
        elif typ.startswith(_BOOL):
            return vol.Boolean()(value)
        elif typ.startswith(_EMAIL):
            return vol.Email()(value)
        elif typ.startswith(_URL):
            return vol.Url()(value)
        elif typ.startswith(_PORT):
            return network_port(value)
        elif typ.startswith(_MATCH):
            return vol.Match(match.group("match"))(str(value))
        elif typ.startswith(_LIST):
            return vol.In(match.group("list").split("|"))(str(value))
        elif typ.startswith(_DEVICE):
            try:
                device = self.sys_hardware.get_by_path(Path(value))
            except HardwareNotFound:
                raise vol.Invalid(
                    f"Device '{value}' does not exists! in {self._name} ({self._slug})"
                ) from None

            # Have filter
            if match.group("filter"):
                str_filter = match.group("filter")
                device_filter = _create_device_filter(str_filter)
                if device not in self.sys_hardware.filter_devices(**device_filter):
                    raise vol.Invalid(
                        f"Device '{value}' don't match the filter {str_filter}! in {self._name} ({self._slug})"
                    )

            # Device valid
            self.devices.add(device)
            return str(device.path)

        raise vol.Invalid(
            f"Fatal error for option '{key}' with type '{typ}' in {self._name} ({self._slug})"
        ) from None

    def _nested_validate_list(self, typ: Any, data_list: List[Any], key: str):
        """Validate nested items."""
        options = []

        # Make sure it is a list
        if not isinstance(data_list, list):
            raise vol.Invalid(
                f"Invalid list for option '{key}' in {self._name} ({self._slug})"
            ) from None

        # Process list
        for element in data_list:
            # Nested?
            if isinstance(typ, dict):
                c_options = self._nested_validate_dict(typ, element, key)
                options.append(c_options)
            else:
                options.append(self._single_validate(typ, element, key))

        return options

    def _nested_validate_dict(
        self, typ: Dict[Any, Any], data_dict: Dict[Any, Any], key: str
    ):
        """Validate nested items."""
        options = {}

        # Make sure it is a dict
        if not isinstance(data_dict, dict):
            raise vol.Invalid(
                f"Invalid dict for option '{key}' in {self._name} ({self._slug})"
            ) from None

        # Process dict
        for c_key, c_value in data_dict.items():
            # Ignore unknown options / remove from list
            if c_key not in typ:
                _LOGGER.warning(
                    "Unknown option '%s' for %s (%s)", c_key, self._name, self._slug
                )
                continue

            # Nested?
            if isinstance(typ[c_key], list):
                options[c_key] = self._nested_validate_list(
                    typ[c_key][0], c_value, c_key
                )
            else:
                options[c_key] = self._single_validate(typ[c_key], c_value, c_key)

        self._check_missing_options(typ, options, key)
        return options

    def _check_missing_options(
        self, origin: Dict[Any, Any], exists: Dict[Any, Any], root: str
    ) -> None:
        """Check if all options are exists."""
        missing = set(origin) - set(exists)
        for miss_opt in missing:
            if isinstance(origin[miss_opt], str) and origin[miss_opt].endswith("?"):
                continue
            raise vol.Invalid(
                f"Missing option '{miss_opt}' in {root} in {self._name} ({self._slug})"
            ) from None


class UiOptions(CoreSysAttributes):
    """Render UI Add-ons Options."""

    def __init__(self, coresys: CoreSys) -> None:
        """Initialize UI option render."""
        self.coresys = coresys

    def __call__(self, raw_schema: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate UI schema."""
        ui_schema: List[Dict[str, Any]] = []

        # read options
        for key, value in raw_schema.items():
            if isinstance(value, list):
                # nested value list
                self._nested_ui_list(ui_schema, value, key)
            elif isinstance(value, dict):
                # nested value dict
                self._nested_ui_dict(ui_schema, value, key)
            else:
                # normal value
                self._single_ui_option(ui_schema, value, key)

        return ui_schema

    def _single_ui_option(
        self,
        ui_schema: List[Dict[str, Any]],
        value: str,
        key: str,
        multiple: bool = False,
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
        if value.startswith(_STR):
            ui_node["type"] = "string"
        elif value.startswith(_PASSWORD):
            ui_node["type"] = "string"
            ui_node["format"] = "password"
        elif value.startswith(_INT):
            ui_node["type"] = "integer"
        elif value.startswith(_FLOAT):
            ui_node["type"] = "float"
        elif value.startswith(_BOOL):
            ui_node["type"] = "boolean"
        elif value.startswith(_EMAIL):
            ui_node["type"] = "string"
            ui_node["format"] = "email"
        elif value.startswith(_URL):
            ui_node["type"] = "string"
            ui_node["format"] = "url"
        elif value.startswith(_PORT):
            ui_node["type"] = "integer"
        elif value.startswith(_MATCH):
            ui_node["type"] = "string"
        elif value.startswith(_LIST):
            ui_node["type"] = "select"
            ui_node["options"] = match.group("list").split("|")
        elif value.startswith(_DEVICE):
            ui_node["type"] = "select"

            # Have filter
            if match.group("filter"):
                device_filter = _create_device_filter(match.group("filter"))
                ui_node["options"] = [
                    (device.by_id or device.path).as_posix()
                    for device in self.sys_hardware.filter_devices(**device_filter)
                ]
            else:
                ui_node["options"] = [
                    (device.by_id or device.path).as_posix()
                    for device in self.sys_hardware.devices
                ]

        ui_schema.append(ui_node)

    def _nested_ui_list(
        self,
        ui_schema: List[Dict[str, Any]],
        option_list: List[Any],
        key: str,
    ) -> None:
        """UI nested list items."""
        try:
            element = option_list[0]
        except IndexError:
            _LOGGER.error("Invalid schema %s", key)
            return

        if isinstance(element, dict):
            self._nested_ui_dict(ui_schema, element, key, multiple=True)
        else:
            self._single_ui_option(ui_schema, element, key, multiple=True)

    def _nested_ui_dict(
        self,
        ui_schema: List[Dict[str, Any]],
        option_dict: Dict[str, Any],
        key: str,
        multiple: bool = False,
    ) -> None:
        """UI nested dict items."""
        ui_node = {
            "name": key,
            "type": "schema",
            "optional": True,
            "multiple": multiple,
        }

        nested_schema = []
        for c_key, c_value in option_dict.items():
            # Nested?
            if isinstance(c_value, list):
                self._nested_ui_list(nested_schema, c_value, c_key)
            else:
                self._single_ui_option(nested_schema, c_value, c_key)

        ui_node["schema"] = nested_schema
        ui_schema.append(ui_node)


def _create_device_filter(str_filter: str) -> Dict[str, Any]:
    """Generate device Filter."""
    raw_filter = dict(value.split("=") for value in str_filter.split(";"))

    clean_filter = {}
    for key, value in raw_filter.items():
        if key == "subsystem":
            clean_filter[key] = UdevSubsystem(value)
        else:
            clean_filter[key] = value

    return clean_filter
