"""Tools file for Supervisor."""

from functools import partial
import logging
from pathlib import Path
from typing import TYPE_CHECKING, Any

from atomicwrites import atomic_write
import orjson

from ..exceptions import JsonFileError

_LOGGER: logging.Logger = logging.getLogger(__name__)


def json_dumps(data: Any) -> str:
    """Dump json string."""
    return json_bytes(data).decode("utf-8")


def json_encoder_default(obj: Any) -> Any:
    """Convert Supervisor special objects."""
    if isinstance(obj, (set, tuple)):
        return list(obj)
    if isinstance(obj, float):
        return float(obj)
    if isinstance(obj, Path):
        return obj.as_posix()
    raise TypeError


if TYPE_CHECKING:

    def json_bytes(obj: Any) -> bytes:
        """Dump json bytes."""

else:
    json_bytes = partial(
        orjson.dumps,  # pylint: disable=no-member
        option=orjson.OPT_NON_STR_KEYS,  # pylint: disable=no-member
        default=json_encoder_default,
    )
    """Dump json bytes."""


# pylint - https://github.com/ijl/orjson/issues/248
json_loads = orjson.loads  # pylint: disable=no-member


def write_json_file(jsonfile: Path, data: Any) -> None:
    """Write a JSON file.

    Must be run in executor.
    """
    try:
        with atomic_write(jsonfile, overwrite=True) as fp:
            fp.write(
                orjson.dumps(  # pylint: disable=no-member
                    data,
                    option=orjson.OPT_INDENT_2  # pylint: disable=no-member
                    | orjson.OPT_NON_STR_KEYS,  # pylint: disable=no-member
                    default=json_encoder_default,
                ).decode("utf-8")
            )
        jsonfile.chmod(0o600)
    except (OSError, ValueError, TypeError) as err:
        raise JsonFileError(
            f"Can't write {jsonfile!s}: {err!s}", _LOGGER.error
        ) from err


def read_json_file(jsonfile: Path) -> Any:
    """Read a JSON file and return a dict.

    Must be run in executor.
    """
    try:
        return json_loads(jsonfile.read_bytes())
    except (OSError, ValueError, TypeError, UnicodeDecodeError) as err:
        raise JsonFileError(
            f"Can't read json from {jsonfile!s}: {err!s}", _LOGGER.error
        ) from err
