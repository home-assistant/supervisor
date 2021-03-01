"""Tools handle YAML files for Supervisor."""
import logging
from pathlib import Path

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
