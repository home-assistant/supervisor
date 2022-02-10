"""Small wrapper for CodeNotary."""
import asyncio
import hashlib
import json
import logging
from pathlib import Path
import shlex
from typing import Final, Union

import async_timeout
from dirhash import dirhash

from . import clean_env
from ..exceptions import CodeNotaryBackendError, CodeNotaryError, CodeNotaryUntrusted

_LOGGER: logging.Logger = logging.getLogger(__name__)

_CAS_CMD: str = (
    "cas authenticate --signerID {signer} --silent --output json --hash {sum}"
)
_CACHE: set[tuple[str, str]] = set()


_ATTR_STATUS: Final = "status"


def calc_checksum(data: Union[str, bytes]) -> str:
    """Generate checksum for CodeNotary."""
    if isinstance(data, str):
        return hashlib.sha256(data.encode()).hexdigest()
    return hashlib.sha256(data).hexdigest()


def calc_checksum_path_sourcecode(folder: Path) -> str:
    """Calculate checksum for a path source code."""
    return dirhash(folder.as_posix(), "sha256", match=["*.py"])


async def cas_validate(
    signer: str,
    checksum: str,
) -> None:
    """Validate data against CodeNotary."""
    if (checksum, signer) in _CACHE:
        return

    # Generate command for request
    command = shlex.split(_CAS_CMD.format(signer=signer, sum=checksum))

    # Request notary authorization
    _LOGGER.debug("Send cas command: %s", command)
    try:
        proc = await asyncio.create_subprocess_exec(
            *command,
            stdin=asyncio.subprocess.DEVNULL,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env=clean_env(),
        )

        async with async_timeout.timeout(10):
            data, error = await proc.communicate()
    except OSError as err:
        raise CodeNotaryError(
            f"CodeNotary fatal error: {err!s}", _LOGGER.critical
        ) from err
    except asyncio.TimeoutError:
        raise CodeNotaryError(
            "Timeout while processing CodeNotary", _LOGGER.error
        ) from None

    # Check if Notarized
    if proc.returncode != 0 and not data:
        if error:
            error = error.decode("utf-8")
            if "not notarized" in error:
                raise CodeNotaryUntrusted()
        else:
            error = "Unknown CodeNotary backend issue"
        raise CodeNotaryBackendError(error, _LOGGER.warning)

    # Parse data
    try:
        data_json = json.loads(data)
        _LOGGER.debug("CodeNotary response with: %s", data_json)
    except (json.JSONDecodeError, UnicodeDecodeError) as err:
        raise CodeNotaryError(
            f"Can't parse CodeNotary output: {data!s} - {err!s}", _LOGGER.error
        ) from err

    if data_json[_ATTR_STATUS] == 0:
        _CACHE.add((checksum, signer))
    else:
        raise CodeNotaryUntrusted()
