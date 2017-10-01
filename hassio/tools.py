"""Tools file for HassIO."""
import asyncio
from contextlib import suppress
from datetime import datetime, timedelta, timezone
import json
import logging
import re

import aiohttp
import async_timeout
import pytz
import voluptuous as vol
from voluptuous.humanize import humanize_error

_LOGGER = logging.getLogger(__name__)

FREEGEOIP_URL = "https://freegeoip.io/json/"

RE_STRING = re.compile(r"\x1b(\[.*?[@-~]|\].*?(\x07|\x1b\\))")

RE_YAML_CAPTER = re.compile(
    r"(^(?P<name>\w+):\n(?P<data>(?:^[ ].*\n?|\n)*)$)", re.M)
RE_YAML_OPTS = re.compile(
    r"(^[ ]+(?P<param>\w+): (\"|')?(?P<value>.*)(\"|')?\n?$)", re.M)

# Copyright (c) Django Software Foundation and individual contributors.
# All rights reserved.
# https://github.com/django/django/blob/master/LICENSE
RE_DATETIME = re.compile(
    r"(?P<year>\d{4})-(?P<month>\d{1,2})-(?P<day>\d{1,2})"
    r"[T ](?P<hour>\d{1,2}):(?P<minute>\d{1,2})"
    r"(?::(?P<second>\d{1,2})(?:\.(?P<microsecond>\d{1,6})\d{0,6})?)?"
    r"(?P<tzinfo>Z|[+-]\d{2}(?::?\d{2})?)?$"
)


def write_json_file(jsonfile, data):
    """Write a json file."""
    try:
        json_str = json.dumps(data, indent=2)
        with jsonfile.open('w') as conf_file:
            conf_file.write(json_str)
    except (OSError, json.JSONDecodeError):
        return False

    return True


def read_json_file(jsonfile):
    """Read a json file and return a dict."""
    with jsonfile.open('r') as cfile:
        return json.loads(cfile.read())


async def fetch_timezone(websession):
    """Read timezone from freegeoip."""
    data = {}
    with suppress(aiohttp.ClientError, asyncio.TimeoutError,
                  json.JSONDecodeError, KeyError):
        with async_timeout.timeout(10, loop=websession.loop):
            async with websession.get(FREEGEOIP_URL) as request:
                data = await request.json()

    return data.get('time_zone', 'UTC')


def convert_to_ascii(raw):
    """Convert binary to ascii and remove colors."""
    return RE_STRING.sub("", raw.decode())


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
    match = RE_DATETIME.match(dt_str)
    if not match:
        return None
    kws = match.groupdict()  # type: Dict[str, Any]
    if kws['microsecond']:
        kws['microsecond'] = kws['microsecond'].ljust(6, '0')
    tzinfo_str = kws.pop('tzinfo')

    tzinfo = None  # type: Optional[dt.tzinfo]
    if tzinfo_str == 'Z':
        tzinfo = pytz.utc
    elif tzinfo_str is not None:
        offset_mins = int(tzinfo_str[-2:]) if len(tzinfo_str) > 3 else 0
        offset_hours = int(tzinfo_str[1:3])
        offset = timedelta(hours=offset_hours, minutes=offset_mins)
        if tzinfo_str[0] == '-':
            offset = -offset
        tzinfo = timezone(offset)
    else:
        tzinfo = None
    kws = {k: int(v) for k, v in kws.items() if v is not None}
    kws['tzinfo'] = tzinfo
    return datetime(**kws)


def parse_yaml_file(yamlfile):
    """Parse a simple yaml (2 depts) file with regex."""
    with yamlfile.open('r') as yaml:
        data = yaml.read()

    yaml_data = {}
    # read level 1
    for capter in RE_YAML_CAPTER.finditer(data):
        options = {}

        # read level 2
        for option in RE_YAML_OPTS(capter.group('data')):
            options[option.group('param')] = option.group('value')

        yaml_data[capter.group('name')] = options

    return yaml_data


class JsonConfig(object):
    """Hass core object for handle it."""

    def __init__(self, json_file, schema):
        """Initialize hass object."""
        self._file = json_file
        self._schema = schema
        self._data = {}

        # init or load data
        if self._file.is_file():
            try:
                self._data = read_json_file(self._file)
            except (OSError, json.JSONDecodeError):
                _LOGGER.warning("Can't read %s", self._file)
                self._data = {}

        # validate
        try:
            self._data = self._schema(self._data)
        except vol.Invalid as ex:
            _LOGGER.error("Can't parse %s -> %s",
                          self._file, humanize_error(self._data, ex))
            # reset data to default
            self._data = self._schema({})

    def save(self):
        """Store data to config file."""
        # validate
        try:
            self._data = self._schema(self._data)
        except vol.Invalid as ex:
            _LOGGER.error("Can't parse data -> %s",
                          humanize_error(self._data, ex))
            return False

        # write
        if not write_json_file(self._file, self._data):
            _LOGGER.error("Can't store config in %s", self._file)
            return False
        return True


class AsyncThrottle(object):
    """
    Decorator that prevents a function from being called more than once every
    time period.
    """
    def __init__(self, delta):
        """Initialize async throttle."""
        self.throttle_period = delta
        self.time_of_last_call = datetime.min

    def __call__(self, method):
        """Throttle function"""
        async def wrapper(*args, **kwargs):
            """Throttle function wrapper"""
            now = datetime.now()
            time_since_last_call = now - self.time_of_last_call

            if time_since_last_call > self.throttle_period:
                self.time_of_last_call = now
                return await method(*args, **kwargs)

        return wrapper
