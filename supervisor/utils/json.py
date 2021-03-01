"""Tools file for Supervisor."""
from datetime import datetime
import json
import logging
from pathlib import Path
from typing import Any

from atomicwrites import atomic_write

from ..exceptions import JsonFileError

_LOGGER: logging.Logger = logging.getLogger(__name__)


class JSONEncoder(json.JSONEncoder):
    """JSONEncoder that supports Supervisor objects."""

    def default(self, o: Any) -> Any:
        """Convert Supervisor special objects.

        Hand other objects to the original method.
        """
        if isinstance(o, datetime):
            return o.isoformat()
        if isinstance(o, set):
            return list(o)
        if isinstance(o, Path):
            return str(o)
        if hasattr(o, "as_dict"):
            return o.as_dict()

        return json.JSONEncoder.default(self, o)


def write_json_file(jsonfile: Path, data: Any) -> None:
    """Write a JSON file."""
    try:
        with atomic_write(jsonfile, overwrite=True) as fp:
            fp.write(json.dumps(data, indent=2, cls=JSONEncoder))
        jsonfile.chmod(0o600)
    except (OSError, ValueError, TypeError) as err:
        _LOGGER.error("Can't write %s: %s", jsonfile, err)
        raise JsonFileError() from err


def read_json_file(jsonfile: Path) -> Any:
    """Read a JSON file and return a dict."""
    try:
        return json.loads(jsonfile.read_text())
    except (OSError, ValueError, TypeError, UnicodeDecodeError) as err:
        _LOGGER.error("Can't read json from %s: %s", jsonfile, err)
        raise JsonFileError() from err
