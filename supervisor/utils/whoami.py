"""Small wrapper for whoami API."""
import asyncio
import logging
import ssl
from typing import Dict, Union

import aiohttp

from ..exceptions import WhoamiConnectivityError, WhoamiError, WhoamiSSLError

_LOGGER: logging.Logger = logging.getLogger(__name__)
_API_CALL: str = "whoami.home-assistant.io/v1"

_CACHE: Dict[str, Union[str, int]] = {}


async def check_connectivity_backend(
    websession: aiohttp.ClientSession, with_ssl: bool = True
) -> None:
    """Check if password is pwned."""
    url: str = f"http{'s' if with_ssl else ''}://{_API_CALL}"

    _LOGGER.debug("Check whoami to verify connectivity/system with: %s", url)
    try:
        async with websession.get(
            url, timeout=aiohttp.ClientTimeout(total=10)
        ) as request:
            if request.status != 200:
                raise WhoamiError(
                    f"Whoami service response with {request.status}", _LOGGER.warning
                )
            _CACHE.update(await request.json())

    except aiohttp.ClientSSLError as err:
        if isinstance(err, ssl.CertificateError):
            raise WhoamiError(
                f"Whoami possible MITMA detected: {err!s}", _LOGGER.critical
            ) from err

        # Expired certificate / Date ISSUE
        raise WhoamiSSLError(
            f"Whoami service failed with SSL verification: {err!s}", _LOGGER.warning
        ) from err

    except (aiohttp.ClientError, asyncio.TimeoutError) as err:
        raise WhoamiConnectivityError(
            f"Can't fetch Whoami data: {str(err) or 'Timeout'}", _LOGGER.warning
        ) from err
