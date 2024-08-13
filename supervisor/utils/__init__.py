"""Tools file for Supervisor."""

import asyncio
from functools import lru_cache
from ipaddress import IPv4Address
import logging
import os
from pathlib import Path
import re
import socket
from tempfile import TemporaryDirectory
from typing import Any

from awesomeversion import AwesomeVersion

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


async def check_port(address: IPv4Address, port: int) -> bool:
    """Check if port is mapped."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setblocking(False)
    try:
        async with asyncio.timeout(0.5):
            await asyncio.get_running_loop().sock_connect(sock, (str(address), port))
    except (OSError, TimeoutError):
        return False
    finally:
        if sock is not None:
            sock.close()
    return True


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


async def remove_folder(
    folder: Path,
    content_only: bool = False,
    excludes: list[str] | None = None,
    tmp_dir: Path | None = None,
) -> None:
    """Remove folder and reset privileged.

    Is needed to avoid issue with:
        - CAP_DAC_OVERRIDE
        - CAP_DAC_READ_SEARCH
    """
    if excludes:
        if not tmp_dir:
            raise ValueError("tmp_dir is required if excludes are provided")
        if not content_only:
            raise ValueError("Cannot delete the folder if excludes are provided")

        temp = TemporaryDirectory(dir=tmp_dir)
        temp_path = Path(temp.name)
        moved_files: list[Path] = []
        for item in folder.iterdir():
            if any(item.match(exclude) for exclude in excludes):
                moved_files.append(item.rename(temp_path / item.name))

    find_args = []
    if content_only:
        find_args.extend(["-mindepth", "1"])
    try:
        proc = await asyncio.create_subprocess_exec(
            "/usr/bin/find",
            folder,
            "-xdev",
            *find_args,
            "-delete",
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.PIPE,
            env=clean_env(),
        )

        _, error_msg = await proc.communicate()
    except OSError as err:
        _LOGGER.exception("Can't remove folder %s: %s", folder, err)
    else:
        if proc.returncode == 0:
            return
        _LOGGER.error(
            "Can't remove folder %s: %s", folder, error_msg.decode("utf-8").strip()
        )
    finally:
        if excludes:
            for item in moved_files:
                item.rename(folder / item.name)
            temp.cleanup()


def clean_env() -> dict[str, str]:
    """Return a clean env from system."""
    new_env = {}
    for key in ("HOME", "PATH", "PWD", "CWD", "SHLVL"):
        if value := os.environ.get(key):
            new_env[key] = value
    return new_env


@lru_cache
def version_is_new_enough(
    version: AwesomeVersion, want_version: AwesomeVersion
) -> bool:
    """Return True if the given version is new enough."""
    return version >= want_version
