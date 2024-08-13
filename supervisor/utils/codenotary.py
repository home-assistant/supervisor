"""Small wrapper for CodeNotary."""

from __future__ import annotations

import asyncio
import hashlib
import json
import logging
from pathlib import Path
import shlex
from typing import Final

from dirhash import dirhash

from ..exceptions import CodeNotaryBackendError, CodeNotaryError, CodeNotaryUntrusted
from . import clean_env

_LOGGER: logging.Logger = logging.getLogger(__name__)

_CAS_CMD: str = (
    "cas authenticate --signerID {signer} --silent --output json --hash {sum}"
)
_CACHE: set[tuple[str, str]] = set()


_ATTR_ERROR: Final = "error"
_ATTR_STATUS: Final = "status"
_FALLBACK_ERROR: Final = "Unknown CodeNotary backend issue"


def calc_checksum(data: str | bytes) -> str:
    """Generate checksum for CodeNotary."""
    if isinstance(data, str):
        return hashlib.sha256(data.encode()).hexdigest()
    return hashlib.sha256(data).hexdigest()


def calc_checksum_path_sourcecode(folder: Path) -> str:
    """Calculate checksum for a path source code.

    Need catch OSError.
    """
    return dirhash(folder.as_posix(), "sha256", match=["*.py"])


# pylint: disable=unreachable
async def cas_validate(
    signer: str,
    checksum: str,
) -> None:
    """Validate data against CodeNotary."""
    return
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

        async with asyncio.timeout(15):
            data, error = await proc.communicate()
    except TimeoutError:
        raise CodeNotaryBackendError(
            "Timeout while processing CodeNotary", _LOGGER.warning
        ) from None
    except OSError as err:
        raise CodeNotaryError(
            f"CodeNotary fatal error: {err!s}", _LOGGER.critical
        ) from err

    # Check if Notarized
    if proc.returncode != 0 and not data:
        if error:
            try:
                error = error.decode("utf-8")
            except UnicodeDecodeError as err:
                raise CodeNotaryBackendError(_FALLBACK_ERROR, _LOGGER.warning) from err
            if "not notarized" in error:
                raise CodeNotaryUntrusted()
        else:
            error = _FALLBACK_ERROR
        raise CodeNotaryBackendError(error, _LOGGER.warning)

    # Parse data
    try:
        data_json = json.loads(data)
        _LOGGER.debug("CodeNotary response with: %s", data_json)
    except (json.JSONDecodeError, UnicodeDecodeError) as err:
        raise CodeNotaryError(
            f"Can't parse CodeNotary output: {data!s} - {err!s}", _LOGGER.error
        ) from err

    if _ATTR_ERROR in data_json:
        raise CodeNotaryBackendError(data_json[_ATTR_ERROR], _LOGGER.warning)

    if data_json[_ATTR_STATUS] == 0:
        _CACHE.add((checksum, signer))
    else:
        raise CodeNotaryUntrusted()
