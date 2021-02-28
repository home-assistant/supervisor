"""Tools file for Supervisor."""
import asyncio
from ipaddress import IPv4Address
import logging
from pathlib import Path
import re
import socket
from typing import Any, List, Optional

from ..exceptions import HassioError
from .json import read_json_file
from .yaml import read_yaml_file

_LOGGER: logging.Logger = logging.getLogger(__name__)

RE_STRING: re.Pattern = re.compile(r"\x1b(\[.*?[@-~]|\].*?(\x07|\x1b\\))")


def find_one_filetype(
    path: Path, filename: str, filetypes: List[str]
) -> Optional[Path]:
    """Find first file matching filetypes."""
    for file in path.glob(f"**/{filename}.*"):
        if file.suffix in filetypes:
            return file
    return None


def read_json_or_yaml_file(path: Path) -> dict:
    """Read JSON or YAML file."""
    if path.suffix == ".json":
        return read_json_file(path)

    if path.suffix in [".yaml", ".yml"]:
        return read_yaml_file(path)

    raise HassioError(f"{path} is not JSON or YAML")


def convert_to_ascii(raw: bytes) -> str:
    """Convert binary to ascii and remove colors."""
    return RE_STRING.sub("", raw.decode())


def process_lock(method):
    """Wrap function with only run once."""

    async def wrap_api(api, *args, **kwargs):
        """Return api wrapper."""
        if api.lock.locked():
            _LOGGER.error(
                "Can't execute %s while a task is in progress", method.__name__
            )
            return False

        async with api.lock:
            return await method(api, *args, **kwargs)

    return wrap_api


def check_port(address: IPv4Address, port: int) -> bool:
    """Check if port is mapped."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(0.5)
    try:
        result = sock.connect_ex((str(address), port))
        sock.close()

        # Check if the port is available
        if result == 0:
            return True
    except OSError:
        pass
    return False


def check_exception_chain(err: Exception, object_type: Any) -> bool:
    """Check if exception chain include sub exception.

    It's not full recursive because we need mostly only access to the latest.
    """
    if issubclass(type(err), object_type):
        return True

    if not err.__context__:
        return False

    return check_exception_chain(err.__context__, object_type)


def get_message_from_exception_chain(err: Exception) -> str:
    """Get the first message from the exception chain."""
    if str(err):
        return str(err)

    if not err.__context__:
        return ""

    return get_message_from_exception_chain(err.__context__)


async def remove_folder(folder: Path, content_only: bool = False) -> None:
    """Remove folder and reset privileged.

    Is needed to avoid issue with:
        - CAP_DAC_OVERRIDE
        - CAP_DAC_READ_SEARCH
    """
    del_folder = f"{folder}" + "/{,.[!.],..?}*" if content_only else f"{folder}"
    try:
        proc = await asyncio.create_subprocess_exec(
            "bash", "-c", f"rm -rf {del_folder}", stdout=asyncio.subprocess.DEVNULL
        )

        _, error_msg = await proc.communicate()
    except OSError as err:
        error_msg = str(err)
    else:
        if proc.returncode == 0:
            return

    _LOGGER.error("Can't remove folder %s: %s", folder, error_msg)
