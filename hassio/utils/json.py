"""Tools file for HassIO."""
import json
import logging

import voluptuous as vol
from voluptuous.humanize import humanize_error

_LOGGER = logging.getLogger(__name__)


def write_json_file(jsonfile, data):
    """Write a json file."""
    try:
        json_str = json.dumps(data, indent=2)
        with jsonfile.open('w') as conf_file:
            conf_file.write(json_str)
    except (OSError, json.JSONDecodeError):
        return False

    return True


def read_json_file(jsonfile):
    """Read a json file and return a dict."""
    with jsonfile.open('r') as cfile:
        return json.loads(cfile.read())


class JsonConfig(object):
    """Hass core object for handle it."""

    def __init__(self, json_file, schema):
        """Initialize hass object."""
        self._file = json_file
        self._schema = schema
        self._data = {}

        # init or load data
        if self._file.is_file():
            try:
                self._data = read_json_file(self._file)
            except (OSError, json.JSONDecodeError):
                _LOGGER.warning("Can't read %s", self._file)
                self._data = {}

        # validate
        try:
            self._data = self._schema(self._data)
        except vol.Invalid as ex:
            _LOGGER.error("Can't parse %s: %s",
                          self._file, humanize_error(self._data, ex))
            # reset data to default
            self._data = self._schema({})

    def save(self):
        """Store data to config file."""
        # validate
        try:
            self._data = self._schema(self._data)
        except vol.Invalid as ex:
            _LOGGER.error("Can't parse data: %s",
                          humanize_error(self._data, ex))
            return False

        # write
        if not write_json_file(self._file, self._data):
            _LOGGER.error("Can't store config in %s", self._file)
            return False
        return True
