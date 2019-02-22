"""Tools file for Hass.io."""
import json
import logging
from pathlib import Path
from typing import Any

import voluptuous as vol
from voluptuous.humanize import humanize_error

from ..exceptions import JsonFileError

_LOGGER = logging.getLogger(__name__)


def write_json_file(jsonfile: Path, data: Any) -> None:
    """Write a JSON file."""
    try:
        json_str = json.dumps(data, indent=2)
        with jsonfile.open("w") as conf_file:
            conf_file.write(json_str)
    except (OSError, ValueError, TypeError) as err:
        _LOGGER.error("Can't write %s: %s", jsonfile, err)
        raise JsonFileError() from None


def read_json_file(jsonfile: Path) -> Any:
    """Read a JSON file and return a dict."""
    try:
        with jsonfile.open("r") as cfile:
            return json.loads(cfile.read())
    except (OSError, ValueError, TypeError, UnicodeDecodeError) as err:
        _LOGGER.error("Can't read json from %s: %s", jsonfile, err)
        raise JsonFileError() from None


class JsonConfig:
    """Hass core object for handle it."""

    def __init__(self, json_file, schema):
        """Initialize hass object."""
        self._file = json_file
        self._schema = schema
        self._data = {}

        self.read_data()

    def reset_data(self):
        """Reset JSON file to default."""
        try:
            self._data = self._schema({})
        except vol.Invalid as ex:
            _LOGGER.error(
                "Can't reset %s: %s", self._file, humanize_error(self._data, ex)
            )

    def read_data(self):
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
            self._data = self._schema({})

    def save_data(self):
        """Store data to configuration file."""
        # Validate
        try:
            self._data = self._schema(self._data)
        except vol.Invalid as ex:
            _LOGGER.error("Can't parse data: %s", humanize_error(self._data, ex))

            # Load last valid data
            _LOGGER.warning("Reset %s to last version", self._file)
            self.read_data()
        else:
            # write
            try:
                write_json_file(self._file, self._data)
            except JsonFileError:
                pass
