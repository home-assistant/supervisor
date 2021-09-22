"""Small wrapper for haveibeenpwned.com API."""
import asyncio
import io
import logging

import aiohttp

from ..exceptions import PwnedConnectivityError, PwnedError, PwnedSecret

_LOGGER: logging.Logger = logging.getLogger(__name__)
_API_CALL: str = "https://api.pwnedpasswords.com/range/{hash}"

_CACHE: set[str] = set()


async def check_pwned_password(websession: aiohttp.ClientSession, sha1_pw: str) -> None:
    """Check if password is pwned."""
    sha1_pw = sha1_pw.upper()

    # Chech hit cache
    sha1_short = sha1_pw[:5]
    if sha1_short in _CACHE:
        raise PwnedSecret()

    _LOGGER.debug("Check pwned state of %s", sha1_short)
    try:
        async with websession.get(
            _API_CALL.format(hash=sha1_short), timeout=aiohttp.ClientTimeout(total=10)
        ) as request:
            if request.status != 200:
                raise PwnedError(
                    f"Pwned service response with {request.status}", _LOGGER.warning
                )
            data = await request.text()

        buffer = io.StringIO(data)
        for line in buffer:
            if not sha1_pw.endswith(line.split(":")[0]):
                continue
            _CACHE.add(sha1_short)
            raise PwnedSecret()

    except (aiohttp.ClientError, asyncio.TimeoutError) as err:
        raise PwnedConnectivityError(
            f"Can't fetch HIBP data: {str(err) or 'Timeout'}", _LOGGER.warning
        ) from err
