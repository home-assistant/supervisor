"""Tools file for Supervisor."""
import json
import logging
from pathlib import Path
from typing import Any, Dict

import voluptuous as vol
from voluptuous.humanize import humanize_error

from ..exceptions import JsonFileError

_LOGGER: logging.Logger = logging.getLogger(__name__)

_DEFAULT: Dict[str, Any] = {}


def write_json_file(jsonfile: Path, data: Any) -> None:
    """Write a JSON file."""
    try:
        jsonfile.write_text(json.dumps(data, indent=2))
    except (OSError, ValueError, TypeError) as err:
        _LOGGER.error("Can't write %s: %s", jsonfile, err)
        raise JsonFileError()


def read_json_file(jsonfile: Path) -> Any:
    """Read a JSON file and return a dict."""
    try:
        return json.loads(jsonfile.read_text())
    except (OSError, ValueError, TypeError, UnicodeDecodeError) as err:
        _LOGGER.error("Can't read json from %s: %s", jsonfile, err)
        raise JsonFileError()


class JsonConfig:
    """Hass core object for handle it."""

    def __init__(self, json_file: Path, schema: vol.Schema):
        """Initialize hass object."""
        self._file: Path = json_file
        self._schema: vol.Schema = schema
        self._data: Dict[str, Any] = _DEFAULT

        self.read_data()

    def reset_data(self) -> None:
        """Reset JSON file to default."""
        try:
            self._data = self._schema({})
        except vol.Invalid as ex:
            _LOGGER.error(
                "Can't reset %s: %s", self._file, humanize_error(self._data, ex)
            )

    def read_data(self) -> None:
        """Read JSON file & validate."""
        if self._file.is_file():
            try:
                self._data = read_json_file(self._file)
            except JsonFileError:
                self._data = {}

        # Validate
        try:
            self._data = self._schema(self._data)
        except vol.Invalid as ex:
            _LOGGER.error(
                "Can't parse %s: %s", self._file, humanize_error(self._data, ex)
            )

            # Reset data to default
            _LOGGER.warning("Reset %s to default", self._file)
            self._data = self._schema(_DEFAULT)

    def save_data(self) -> None:
        """Store data to configuration file."""
        # Validate
        try:
            self._data = self._schema(self._data)
        except vol.Invalid as ex:
            _LOGGER.error("Can't parse data: %s", humanize_error(self._data, ex))

            # Load last valid data
            _LOGGER.warning("Reset %s to last version", self._file)
            self._data = _DEFAULT
            self.read_data()
        else:
            # write
            try:
                write_json_file(self._file, self._data)
            except JsonFileError:
                pass
