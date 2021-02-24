"""Small wrapper for haveibeenpwned.com API."""
import asyncio
import io
import logging

import aiohttp

from ..exceptions import HassioError

_LOGGER: logging.Logger = logging.getLogger(__name__)
_API_CALL = "https://api.pwnedpasswords.com/range/{hash}"


async def check_pwned_password(websession: aiohttp.ClientSession, sha1_pw: str) -> bool:
    """Check if password is pwned."""
    try:
        async with websession.get(
            _API_CALL.format(hash=sha1_pw[:5]), timeout=aiohttp.ClientTimeout(total=10)
        ) as request:
            if request.status != 200:
                raise HassioError()
            data = await request.text()

        buffer = io.StringIO(data)
        for line in buffer.readline():
            if sha1_pw != line.split(":")[0]:
                continue
            return True

    except (aiohttp.ClientError, asyncio.TimeoutError) as err:
        _LOGGER.warning("Can't fetch freegeoip data: %s", err)
        raise HassioError() from err

    return False
