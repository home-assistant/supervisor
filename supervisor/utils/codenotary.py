"""Small wrapper for CodeNotary."""
import asyncio
import hashlib
import json
import logging
from pathlib import Path
import shlex
from typing import Optional, Set, Tuple, Union

import async_timeout

from ..exceptions import CodeNotaryError, CodeNotaryUntrusted

_LOGGER: logging.Logger = logging.getLogger(__name__)

_VCN_CMD: str = "vcn authenticate --silent --output json"
_CACHE: Set[Tuple[str, Path, str, str]] = set()


_ATTR_ERROR = "error"
_ATTR_VERIFICATION = "verification"
_ATTR_STATUS = "status"


def calc_checksum(data: Union[str, bytes]) -> str:
    """Generate checksum for CodeNotary."""
    if isinstance(data, str):
        return hashlib.sha256(data.encode()).hexdigest()
    return hashlib.sha256(data).hexdigest()


async def vcn_validate(
    checksum: Optional[str] = None,
    path: Optional[Path] = None,
    org: Optional[str] = None,
    signer: Optional[str] = None,
) -> None:
    """Validate data against CodeNotary."""
    if (checksum, path, org, signer) in _CACHE:
        return
    command = shlex.split(_VCN_CMD)

    # Generate command for request
    if org:
        command.extend(["--org", org])
    elif signer:
        command.extend(["--signer", signer])

    if checksum:
        command.extend(["--hash", checksum])
    elif path:
        if path.is_dir:
            command.append(f"dir:/{path!s}")
        else:
            command.append(path.as_posix())
    else:
        RuntimeError("At least path or checksum need to be set!")

    # Request notary authorization
    _LOGGER.debug("Send vcn command: %s", command)
    try:
        proc = await asyncio.create_subprocess_exec(
            *command,
            stdin=asyncio.subprocess.DEVNULL,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.DEVNULL,
        )

        async with async_timeout.timeout(10):
            data, _ = await proc.communicate()
    except OSError as err:
        raise CodeNotaryError(
            f"CodeNotary fatal error: {err!s}", _LOGGER.critical
        ) from err
    except asyncio.TimeoutError:
        raise CodeNotaryError(
            "Timeout while processing CodeNotary", _LOGGER.error
        ) from None

    # Parse data
    try:
        data_json = json.loads(data)
        _LOGGER.debug("CodeNotary response with: %s", data_json)
    except (json.JSONDecodeError, UnicodeDecodeError) as err:
        raise CodeNotaryError(
            f"Can't parse CodeNotary output: {data!s} - {err!s}", _LOGGER.error
        ) from err

    if _ATTR_ERROR in data_json:
        raise CodeNotaryError(data_json[_ATTR_ERROR], _LOGGER.warning)

    if data_json[_ATTR_VERIFICATION][_ATTR_STATUS] == 0:
        _CACHE.add((checksum, path, org, signer))
    else:
        raise CodeNotaryUntrusted()
