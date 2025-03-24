"""Common utils."""

import asyncio
from contextlib import suppress
import logging
from pathlib import Path
from typing import Any, Self

import voluptuous as vol
from voluptuous.humanize import humanize_error

from ..exceptions import ConfigurationFileError
from .json import read_json_file, write_json_file
from .yaml import read_yaml_file, write_yaml_file

_LOGGER: logging.Logger = logging.getLogger(__name__)

_DEFAULT: dict[str, Any] = {}


def find_one_filetype(path: Path, filename: str, filetypes: list[str]) -> Path:
    """Find first file matching filetypes.

    Must be run in executor.
    """
    for file in path.glob(f"**/{filename}.*"):
        if file.suffix in filetypes:
            return file
    raise ConfigurationFileError(f"{path!s}/{filename}.({filetypes}) does not exist!")


def read_json_or_yaml_file(path: Path) -> dict:
    """Read JSON or YAML file.

    Must be run in executor.
    """
    if path.suffix == ".json":
        return read_json_file(path)

    if path.suffix in [".yaml", ".yml"]:
        return read_yaml_file(path)

    raise ConfigurationFileError(f"{path} is not JSON or YAML")


def write_json_or_yaml_file(path: Path, data: dict) -> None:
    """Write JSON or YAML file.

    Must be run in executor.
    """
    if path.suffix == ".json":
        return write_json_file(path, data)

    if path.suffix in [".yaml", ".yml"]:
        return write_yaml_file(path, data)

    raise ConfigurationFileError(f"{path} is not JSON or YAML")


class FileConfiguration:
    """Baseclass for classes that uses configuration files, the files can be JSON/YAML."""

    def __init__(self, file_path: Path | None, schema: vol.Schema):
        """Initialize hass object."""
        self._file: Path | None = file_path
        self._schema: vol.Schema = schema
        self._data: dict[str, Any] = _DEFAULT

    async def load_config(self) -> Self:
        """Read in config in executor."""
        await self.read_data()
        return self

    async def reset_data(self) -> None:
        """Reset configuration to default."""
        try:
            self._data = self._schema(_DEFAULT)
        except vol.Invalid as ex:
            _LOGGER.error(
                "Can't reset %s: %s", self._file, humanize_error(self._data, ex)
            )
        else:
            await self.save_data()

    async def read_data(self) -> None:
        """Read configuration file."""
        if not self._file:
            raise RuntimeError("Path to config file must be set!")

        def _read_data() -> dict[str, Any]:
            if self._file.is_file():
                with suppress(ConfigurationFileError):
                    return read_json_or_yaml_file(self._file)
            return _DEFAULT

        self._data = await asyncio.get_running_loop().run_in_executor(None, _read_data)

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

    async def save_data(self) -> None:
        """Store data to configuration file."""
        if not self._file:
            raise RuntimeError("Path to config file must be set!")

        # Validate
        try:
            self._data = self._schema(self._data)
        except vol.Invalid as ex:
            _LOGGER.critical("Can't parse data: %s", humanize_error(self._data, ex))

            # Load last valid data
            _LOGGER.warning("Resetting %s to last version", self._file)
            self._data = _DEFAULT
            await self.read_data()
        else:
            # write
            with suppress(ConfigurationFileError):
                await asyncio.get_running_loop().run_in_executor(
                    None, write_json_or_yaml_file, self._file, self._data
                )
