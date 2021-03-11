"""Small wrapper for haveibeenpwned.com API."""
import asyncio
import io
import logging

import aiohttp

from ..exceptions import PwnedConnectivityError, PwnedError

_LOGGER: logging.Logger = logging.getLogger(__name__)
_API_CALL = "https://api.pwnedpasswords.com/range/{hash}"

_CACHE = set()


async def check_pwned_password(websession: aiohttp.ClientSession, sha1_pw: str) -> bool:
    """Check if password is pwned."""
    sha1_pw = sha1_pw.upper()
    if sha1_pw[:5] in _CACHE:
        return True

    try:
        async with websession.get(
            _API_CALL.format(hash=sha1_pw[:5]), timeout=aiohttp.ClientTimeout(total=10)
        ) as request:
            if request.status != 200:
                raise PwnedError()
            data = await request.text()

        buffer = io.StringIO(data)
        for line in buffer:
            if not sha1_pw.endswith(line.split(":")[0]):
                continue
            _CACHE.add(sha1_pw[:5])
            return True

    except (aiohttp.ClientError, asyncio.TimeoutError) as err:
        _LOGGER.warning("Can't fetch hibp data: %s", err)
        raise PwnedConnectivityError() from err

    return False
