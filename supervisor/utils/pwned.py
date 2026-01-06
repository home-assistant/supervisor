"""Small wrapper for haveibeenpwned.com API."""

import io
import logging

import aiohttp

from ..exceptions import PwnedConnectivityError, PwnedError, PwnedSecret

_LOGGER: logging.Logger = logging.getLogger(__name__)
_API_CALL: str = "https://api.pwnedpasswords.com/range/{hash}"

_CACHE: set[str] = set()
_OFFLINE_MODE: bool = False  # Track offline state


async def _check_connection(websession: aiohttp.ClientSession) -> bool:
    """Check if internet connection is available."""
    try:
        async with websession.get(
            _API_CALL.format(hash="00000"),
            timeout=aiohttp.ClientTimeout(total=5)
        ) as response:
            return response.status == 200
    except (aiohttp.ClientError, TimeoutError):
        return False


async def check_pwned_password(
    websession: aiohttp.ClientSession, 
    sha1_pw: str,
    offline_mode: bool = True
) -> None:
    """Check if password is pwned.
    
    Args:
        websession: aiohttp ClientSession
        sha1_pw: SHA1 hash of password
        offline_mode: If True, bypass check when offline. If False, raise error.
    """
    global _OFFLINE_MODE
    
    sha1_pw = sha1_pw.upper()
    sha1_short = sha1_pw[:5]

    # Check hit cache
    if sha1_short in _CACHE:
        raise PwnedSecret()

    _LOGGER.debug("Check pwned state of %s", sha1_short)
    
    # Check connection first
    if not await _check_connection(websession):
        _LOGGER.warning("No internet connection - offline mode enabled")
        _OFFLINE_MODE = True
        if offline_mode:
            _LOGGER.info("Bypassing pwned password check (offline)")
            return None # Allow access when offline
        else:
            raise PwnedConnectivityError(
                "No internet connection and offline mode disabled",
                _LOGGER.warning
            )
    
    _OFFLINE_MODE = False
    
    try:
        async with websession.get(
            _API_CALL.format(hash=sha1_short), 
            timeout=aiohttp.ClientTimeout(total=10)
        ) as request:
            if request.status != 200:
                raise PwnedError(
                    f"Pwned service response with {request.status}", 
                    _LOGGER.warning
                )
            data = await request.text()

        buffer = io.StringIO(data)
        for line in buffer:
            if not sha1_pw.endswith(line.split(":")[0]):
                continue
            _CACHE.add(sha1_short)
            raise PwnedSecret()

    except (aiohttp.ClientError, TimeoutError) as err:
        _LOGGER.error(f"Can't fetch HIBP data: {str(err) or 'Timeout'}")
        
        if offline_mode:
            _LOGGER.warning("Bypassing check due to connectivity error")
            return None
        else:
            raise PwnedConnectivityError(
                f"Can't fetch HIBP data: {str(err) or 'Timeout'}", 
                _LOGGER.warning
            ) from err


def is_offline() -> bool:
    """Check if system is in offline mode."""
    return _OFFLINE_MODE
