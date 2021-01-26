"""Add-on Options / UI rendering."""
import logging
from pathlib import Path
import re
from typing import Any, Dict, List, Set, Union

import voluptuous as vol

from ..coresys import CoreSys, CoreSysAttributes
from ..exceptions import HardwareNotFound
from ..hardware.data import Device
from ..validate import network_port

_LOGGER: logging.Logger = logging.getLogger(__name__)

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
V_DEVICE = "device"

RE_SCHEMA_ELEMENT = re.compile(
    r"^(?:"
    r"|bool"
    r"|email"
    r"|url"
    r"|port"
    r"|device(?:\((?P<filter>\w+)\))?"
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
        self,
        coresys: CoreSys,
        raw_schema: Dict[str, Any],
    ):
        """Validate schema."""
        self.coresys: CoreSys = coresys
        self.raw_schema: Dict[str, Any] = raw_schema
        self.devices: Set[Device] = set()

    def __call__(self, struct):
        """Create schema validator for add-ons options."""
        options = {}

        # read options
        for key, value in struct.items():
            # Ignore unknown options / remove from list
            if key not in self.raw_schema:
                _LOGGER.warning("Unknown options %s", key)
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
                raise vol.Invalid(f"Type error for {key}") from None

        self._check_missing_options(self.raw_schema, options, "root")
        return options

    # pylint: disable=no-value-for-parameter
    def _single_validate(self, typ: str, value: Any, key: str):
        """Validate a single element."""
        # if required argument
        if value is None:
            raise vol.Invalid(f"Missing required option '{key}'") from None

        # Lookup secret
        if str(value).startswith("!secret "):
            secret: str = value.partition(" ")[2]
            value = self.sys_homeassistant.secrets.get(secret)
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
        elif typ.startswith(V_DEVICE):
            try:
                device = self.sys_hardware.get_by_path(Path(value))
            except HardwareNotFound:
                raise vol.Invalid(f"Device {value} does not exists!") from None
            self.devices.add(device)
            return str(device.path)

        raise vol.Invalid(f"Fatal error for {key} type {typ}") from None

    def _nested_validate_list(self, typ: Any, data_list: List[Any], key: str):
        """Validate nested items."""
        options = []

        # Make sure it is a list
        if not isinstance(data_list, list):
            raise vol.Invalid(f"Invalid list for {key}") from None

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
            raise vol.Invalid(f"Invalid dict for {key}") from None

        # Process dict
        for c_key, c_value in data_dict.items():
            # Ignore unknown options / remove from list
            if c_key not in typ:
                _LOGGER.warning("Unknown options %s", c_key)
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
            raise vol.Invalid(f"Missing option {miss_opt} in {root}") from None


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
        elif value.startswith(V_DEVICE):
            ui_node["type"] = "select"
            # FIXME
            ui_node["options"] = self.sys_hardware.list_devices(
                filter=match.group("filter")
            )

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
