"""Tools handle YAML files for Supervisor."""
import logging
from pathlib import Path

from atomicwrites import atomic_write
from ruamel.yaml import YAML, YAMLError

from ..exceptions import YamlFileError

_YAML = YAML()
_YAML.allow_duplicate_keys = True

_LOGGER: logging.Logger = logging.getLogger(__name__)


def read_yaml_file(path: Path) -> dict:
    """Read YAML file from path."""
    try:
        return _YAML.load(path) or {}

    except (YAMLError, AttributeError) as err:
        _LOGGER.error("Can't read YAML file %s - %s", path, err)
        raise YamlFileError() from err


def write_yaml_file(path: Path, data: dict) -> None:
    """Write a YAML file."""
    try:
        with atomic_write(path, overwrite=True) as fp:
            _YAML.dump(data, fp)
        path.chmod(0o600)
    except (YAMLError, OSError, ValueError, TypeError) as err:
        _LOGGER.error("Can't write %s: %s", path, err)
        raise YamlFileError() from err
