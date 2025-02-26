"""Tools handle YAML files for Supervisor."""

import logging
from pathlib import Path

from atomicwrites import atomic_write
from yaml import YAMLError, dump, load

try:
    from yaml import CDumper as Dumper, CSafeLoader as SafeLoader
except ImportError:
    from yaml import Dumper, SafeLoader

from ..exceptions import YamlFileError

_LOGGER: logging.Logger = logging.getLogger(__name__)


def read_yaml_file(path: Path) -> dict:
    """Read YAML file from path.

    Must be run in executor.
    """
    try:
        with open(path, encoding="utf-8") as yaml_file:
            return load(yaml_file, Loader=SafeLoader) or {}

    except (YAMLError, AttributeError, OSError, UnicodeDecodeError) as err:
        raise YamlFileError(
            f"Can't read YAML file {path!s} - {err!s}", _LOGGER.error
        ) from err


def write_yaml_file(path: Path, data: dict) -> None:
    """Write a YAML file.

    Must be run in executor.
    """
    try:
        with atomic_write(path, overwrite=True) as fp:
            dump(data, fp, Dumper=Dumper)
        path.chmod(0o600)
    except (YAMLError, OSError, ValueError, TypeError) as err:
        raise YamlFileError(f"Can't write {path!s}: {err!s}", _LOGGER.error) from err
