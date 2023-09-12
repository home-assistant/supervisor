"""Tools handle YAML files for Supervisor."""
import logging
from pathlib import Path

from atomicwrites import atomic_write
from yaml import Dumper, Loader, YAMLError, dump, load

from ..exceptions import YamlFileError

_LOGGER: logging.Logger = logging.getLogger(__name__)


def read_yaml_file(path: Path) -> dict:
    """Read YAML file from path."""
    try:
        with open(path, encoding="utf-8") as yaml_file:
            return load(yaml_file, Loader=Loader) or {}

    except (YAMLError, AttributeError, OSError) as err:
        raise YamlFileError(
            f"Can't read YAML file {path!s} - {err!s}", _LOGGER.error
        ) from err


def write_yaml_file(path: Path, data: dict) -> None:
    """Write a YAML file."""
    try:
        with atomic_write(path, overwrite=True) as fp:
            dump(data, fp, Dumper=Dumper)
        path.chmod(0o600)
    except (YAMLError, OSError, ValueError, TypeError) as err:
        raise YamlFileError(f"Can't write {path!s}: {err!s}", _LOGGER.error) from err
