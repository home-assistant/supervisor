"""Tools file for HassIO."""
import json
import logging

import voluptuous as vol
from voluptuous.humanize import humanize_error

_LOGGER = logging.getLogger(__name__)


def write_json_file(jsonfile, data):
    """Write a json file."""
    json_str = json.dumps(data, indent=2)
    with jsonfile.open('w') as conf_file:
        conf_file.write(json_str)


def read_json_file(jsonfile):
    """Read a json file and return a dict."""
    with jsonfile.open('r') as cfile:
        return json.loads(cfile.read())


class JsonConfig:
    """Hass core object for handle it."""

    def __init__(self, json_file, schema):
        """Initialize hass object."""
        self._file = json_file
        self._schema = schema
        self._data = {}

        self.read_data()

    def reset_data(self):
        """Reset json file to default."""
        try:
            self._data = self._schema({})
        except vol.Invalid as ex:
            _LOGGER.error("Can't reset %s: %s",
                          self._file, humanize_error(self._data, ex))

    def read_data(self):
        """Read json file & validate."""
        if self._file.is_file():
            try:
                self._data = read_json_file(self._file)
            except (OSError, json.JSONDecodeError):
                _LOGGER.warning("Can't read %s", self._file)
                self._data = {}

        # Validate
        try:
            self._data = self._schema(self._data)
        except vol.Invalid as ex:
            _LOGGER.error("Can't parse %s: %s",
                          self._file, humanize_error(self._data, ex))

            # Reset data to default
            _LOGGER.warning("Reset %s to default", self._file)
            self._data = self._schema({})

    def save_data(self):
        """Store data to config file."""
        # Validate
        try:
            self._data = self._schema(self._data)
        except vol.Invalid as ex:
            _LOGGER.error("Can't parse data: %s",
                          humanize_error(self._data, ex))

            # Load last valid data
            _LOGGER.warning("Reset %s to last version", self._file)
            self.read_data()
            return

        # write
        try:
            write_json_file(self._file, self._data)
        except (OSError, json.JSONDecodeError) as err:
            _LOGGER.error("Can't store config in %s: %s", self._file, err)
