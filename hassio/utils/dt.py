"""Tools file for Hass.io."""
import asyncio
from datetime import datetime, timedelta, timezone, tzinfo
import logging
import re
from typing import Any, Dict, Optional

import aiohttp
import pytz

UTC = pytz.utc

GEOIP_URL = "http://ip-api.com/json/"

_LOGGER: logging.Logger = logging.getLogger(__name__)


# Copyright (c) Django Software Foundation and individual contributors.
# All rights reserved.
# https://github.com/django/django/blob/master/LICENSE
DATETIME_RE = re.compile(
    r"(?P<year>\d{4})-(?P<month>\d{1,2})-(?P<day>\d{1,2})"
    r"[T ](?P<hour>\d{1,2}):(?P<minute>\d{1,2})"
    r"(?::(?P<second>\d{1,2})(?:\.(?P<microsecond>\d{1,6})\d{0,6})?)?"
    r"(?P<tzinfo>Z|[+-]\d{2}(?::?\d{2})?)?$"
)


async def fetch_timezone(websession):
    """Read timezone from freegeoip."""
    data = {}
    try:
        async with websession.get(GEOIP_URL, timeout=10) as request:
            data = await request.json()

    except (aiohttp.ClientError, asyncio.TimeoutError) as err:
        _LOGGER.warning("Can't fetch freegeoip data: %s", err)
    except ValueError as err:
        _LOGGER.warning("Error on parse freegeoip data: %s", err)

    return data.get("timezone", "UTC")


# Copyright (c) Django Software Foundation and individual contributors.
# All rights reserved.
# https://github.com/django/django/blob/master/LICENSE
def parse_datetime(dt_str):
    """Parse a string and return a datetime.datetime.

    This function supports time zone offsets. When the input contains one,
    the output uses a timezone with a fixed offset from UTC.
    Raises ValueError if the input is well formatted but not a valid datetime.
    Returns None if the input isn't well formatted.
    """
    match = DATETIME_RE.match(dt_str)
    if not match:
        return None
    kws: Dict[str, Any] = match.groupdict()
    if kws["microsecond"]:
        kws["microsecond"] = kws["microsecond"].ljust(6, "0")
    tzinfo_str = kws.pop("tzinfo")

    tzinfo_val: Optional[tzinfo] = None
    if tzinfo_str == "Z":
        tzinfo_val = UTC
    elif tzinfo_str is not None:
        offset_mins = int(tzinfo_str[-2:]) if len(tzinfo_str) > 3 else 0
        offset_hours = int(tzinfo_str[1:3])
        offset = timedelta(hours=offset_hours, minutes=offset_mins)
        if tzinfo_str[0] == "-":
            offset = -offset
        tzinfo_val = timezone(offset)
    else:
        tzinfo_val = None
    kws = {k: int(v) for k, v in kws.items() if v is not None}
    kws["tzinfo"] = tzinfo_val
    return datetime(**kws)


def utcnow() -> datetime:
    """Return the current timestamp including timezone."""
    return datetime.now(UTC)


def utc_from_timestamp(timestamp: float) -> datetime:
    """Return a UTC time from a timestamp."""
    return UTC.localize(datetime.utcfromtimestamp(timestamp))
