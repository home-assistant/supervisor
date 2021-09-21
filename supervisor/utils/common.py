"""Common utils."""
import logging
from pathlib import Path
from typing import Any

import voluptuous as vol
from voluptuous.humanize import humanize_error

from ..exceptions import ConfigurationFileError
from .json import read_json_file, write_json_file
from .yaml import read_yaml_file, write_yaml_file

_LOGGER: logging.Logger = logging.getLogger(__name__)

_DEFAULT: dict[str, Any] = {}


def find_one_filetype(path: Path, filename: str, filetypes: list[str]) -> Path:
    """Find first file matching filetypes."""
    for file in path.glob(f"**/{filename}.*"):
        if file.suffix in filetypes:
            return file
    raise ConfigurationFileError(f"{path!s}/{filename}.({filetypes}) not exists!")


def read_json_or_yaml_file(path: Path) -> dict:
    """Read JSON or YAML file."""
    if path.suffix == ".json":
        return read_json_file(path)

    if path.suffix in [".yaml", ".yml"]:
        return read_yaml_file(path)

    raise ConfigurationFileError(f"{path} is not JSON or YAML")


def write_json_or_yaml_file(path: Path, data: dict) -> None:
    """Write JSON or YAML file."""
    if path.suffix == ".json":
        return write_json_file(path, data)

    if path.suffix in [".yaml", ".yml"]:
        return write_yaml_file(path, data)

    raise ConfigurationFileError(f"{path} is not JSON or YAML")


class FileConfiguration:
    """Baseclass for classes that uses configuration files, the files can be JSON/YAML."""

    def __init__(self, file_path: Path, schema: vol.Schema):
        """Initialize hass object."""
        self._file: Path = file_path
        self._schema: vol.Schema = schema
        self._data: dict[str, Any] = _DEFAULT

        self.read_data()

    def reset_data(self) -> None:
        """Reset configuration to default."""
        try:
            self._data = self._schema(_DEFAULT)
        except vol.Invalid as ex:
            _LOGGER.error(
                "Can't reset %s: %s", self._file, humanize_error(self._data, ex)
            )

    def read_data(self) -> None:
        """Read configuration file."""
        if self._file.is_file():
            try:
                self._data = read_json_or_yaml_file(self._file)
            except ConfigurationFileError:
                self._data = _DEFAULT

        # Validate
        try:
            self._data = self._schema(self._data)
        except vol.Invalid as ex:
            _LOGGER.critical(
                "Can't parse %s: %s", self._file, humanize_error(self._data, ex)
            )

            # Reset data to default
            _LOGGER.warning("Resetting %s to default", self._file)
            self._data = self._schema(_DEFAULT)

    def save_data(self) -> None:
        """Store data to configuration file."""
        # Validate
        try:
            self._data = self._schema(self._data)
        except vol.Invalid as ex:
            _LOGGER.critical("Can't parse data: %s", humanize_error(self._data, ex))

            # Load last valid data
            _LOGGER.warning("Resetting %s to last version", self._file)
            self._data = _DEFAULT
            self.read_data()
        else:
            # write
            try:
                write_json_or_yaml_file(self._file, self._data)
            except ConfigurationFileError:
                pass
