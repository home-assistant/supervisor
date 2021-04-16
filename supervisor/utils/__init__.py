"""Tools file for Supervisor."""
import asyncio
from ipaddress import IPv4Address
import logging
import os
from pathlib import Path
import re
import socket
from typing import Any, Dict

_LOGGER: logging.Logger = logging.getLogger(__name__)

RE_STRING: re.Pattern = re.compile(r"\x1b(\[.*?[@-~]|\].*?(\x07|\x1b\\))")


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


def clean_env() -> Dict[str, str]:
    """Return a clean env from system."""
    new_env = {}
    for key in ("HOME", "PATH", "PWD", "CWD", "SHLVL"):
        if value := os.environ.get(key):
            new_env[key] = value
    return new_env
