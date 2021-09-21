"""Tools file for Supervisor."""
from contextlib import suppress
from datetime import datetime, timedelta, timezone, tzinfo
import re
from typing import Any, Optional
import zoneinfo

import ciso8601

UTC = timezone.utc


# Copyright (c) Django Software Foundation and individual contributors.
# All rights reserved.
# https://github.com/django/django/blob/master/LICENSE
DATETIME_RE = re.compile(
    r"(?P<year>\d{4})-(?P<month>\d{1,2})-(?P<day>\d{1,2})"
    r"[T ](?P<hour>\d{1,2}):(?P<minute>\d{1,2})"
    r"(?::(?P<second>\d{1,2})(?:\.(?P<microsecond>\d{1,6})\d{0,6})?)?"
    r"(?P<tzinfo>Z|[+-]\d{2}(?::?\d{2})?)?$"
)


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
    with suppress(ValueError, IndexError):
        return ciso8601.parse_datetime(dt_str)

    match = DATETIME_RE.match(dt_str)
    if not match:
        return None
    kws: dict[str, Any] = match.groupdict()
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
    return datetime.utcfromtimestamp(timestamp).replace(tzinfo=UTC)


def get_time_zone(time_zone_str: str) -> Optional[tzinfo]:
    """Get time zone from string. Return None if unable to determine."""
    try:
        return zoneinfo.ZoneInfo(time_zone_str)
    except zoneinfo.ZoneInfoNotFoundError:
        return None
