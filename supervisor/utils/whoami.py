"""Small wrapper for whoami API."""
import asyncio
from datetime import datetime
import logging
import ssl

import aiohttp
import attr

from ..exceptions import WhoamiConnectivityError, WhoamiError, WhoamiSSLError
from .dt import utc_from_timestamp

_LOGGER: logging.Logger = logging.getLogger(__name__)
_API_CALL: str = "whoami.home-assistant.io/v1"


@attr.s(slots=True, frozen=True)
class WhoamiData:
    """Client Whoami data."""

    timezone: str = attr.ib()
    dt_utc: datetime = attr.ib()


async def retrieve_whoami(
    websession: aiohttp.ClientSession, with_ssl: bool = True
) -> WhoamiData:
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
            data = await request.json()

        return WhoamiData(
            data["timezone"], utc_from_timestamp(float(data["timestamp"]))
        )

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
