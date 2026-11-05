"""Utilities for working with systemd journal export format."""

from asyncio import IncompleteReadError
from collections.abc import AsyncGenerator
from datetime import UTC, datetime, tzinfo
from functools import wraps
import json
import re

from aiohttp import ClientResponse
import pyjournalexport
from pyjournalexport import JournalExportParser

from ..exceptions import MalformedBinaryEntryError
from ..host.const import LogFormatter

_RE_ANSI_CSI_COLORS_PATTERN = re.compile(r"\x1B\[[0-9;]*m")


def _strip_ansi_colors(message: str) -> str:
    """Remove ANSI color codes from a message string."""
    return _RE_ANSI_CSI_COLORS_PATTERN.sub("", message)


def formatter(required_fields: list[str]):
    """Decorate journal entry formatters with list of required fields.

    Helper decorator that can be used for getting list of required fields for a journal
    formatter function using function.required_fields function attribute.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        wrapper.required_fields = ["__CURSOR"] + required_fields
        return wrapper

    return decorator


@formatter(["MESSAGE"])
def journal_plain_formatter(
    entries: dict[str, str], no_colors: bool = False, tz: tzinfo = UTC
) -> str:
    """Format parsed journal entries as a plain message."""
    return _strip_ansi_colors(entries["MESSAGE"]) if no_colors else entries["MESSAGE"]


def _format_timestamp(timestamp: str, tz: tzinfo) -> str:
    """Format a journal timestamp in `tz` with milliseconds and the UTC offset."""
    return datetime.fromtimestamp(int(timestamp) / 1e6, tz).isoformat(
        sep=" ", timespec="milliseconds"
    )


@formatter(["__REALTIME_TIMESTAMP", "MESSAGE"])
def journal_timestamp_formatter(
    entries: dict[str, str], no_colors: bool = False, tz: tzinfo = UTC
) -> str:
    """Format parsed journal entries as a timestamp followed by the message."""
    ts = _format_timestamp(entries["__REALTIME_TIMESTAMP"], tz)
    return f"{ts} {journal_plain_formatter(entries, no_colors=no_colors)}"


@formatter(
    [
        "__REALTIME_TIMESTAMP",
        "_HOSTNAME",
        "SYSLOG_IDENTIFIER",
        "_PID",
        "MESSAGE",
    ]
)
def journal_verbose_formatter(
    entries: dict[str, str], no_colors: bool = False, tz: tzinfo = UTC
) -> str:
    """Format parsed journal entries to a journalctl-like format."""
    ts = _format_timestamp(entries["__REALTIME_TIMESTAMP"], tz)

    identifier = (
        f"{entries.get('SYSLOG_IDENTIFIER', '_UNKNOWN_')}[{entries['_PID']}]"
        if "_PID" in entries
        else entries.get("SYSLOG_IDENTIFIER", "_UNKNOWN_")
    )

    message = (
        _strip_ansi_colors(entries.get("MESSAGE", ""))
        if no_colors
        else entries.get("MESSAGE", "")
    )

    return f"{ts} {entries.get('_HOSTNAME', '')} {identifier}: {message}"


JOURNAL_READ_SIZE = 64 * 1024


async def journal_logs_reader(
    journal_logs: ClientResponse,
    log_formatter: LogFormatter = LogFormatter.PLAIN,
    no_colors: bool = False,
    tz: tzinfo = UTC,
) -> AsyncGenerator[tuple[str | None, str]]:
    """Read logs from systemd journal, formatted using the given formatter.

    Optionally strip ANSI color codes from the entries' messages. Timestamps are
    converted to the given timezone.

    Returns a generator of (cursor, formatted_entry) tuples.
    """
    match log_formatter:
        case LogFormatter.PLAIN:
            formatter_ = journal_plain_formatter
        case LogFormatter.TIMESTAMP:
            formatter_ = journal_timestamp_formatter
        case LogFormatter.VERBOSE:
            formatter_ = journal_verbose_formatter
        case _:
            raise ValueError(f"Unknown log format: {log_formatter}")

    parser = JournalExportParser(formatter_.required_fields)

    def format_entry(entry: dict[str, str]) -> tuple[str | None, str]:
        return entry.get("__CURSOR"), formatter_(entry, no_colors=no_colors, tz=tz)

    async with journal_logs as resp:
        try:
            while chunk := await resp.content.read(JOURNAL_READ_SIZE):
                for entry in parser.feed(chunk):
                    yield format_entry(entry)
            for entry in parser.close():
                yield format_entry(entry)
        except pyjournalexport.MalformedBinaryEntryError as err:
            raise MalformedBinaryEntryError(str(err)) from err


def _parse_boot_json(boot_json_bytes: bytes) -> tuple[int, str]:
    boot_dict = json.loads(boot_json_bytes.decode("utf-8"))
    return (
        int(boot_dict["index"]),
        boot_dict["boot_id"],
    )


async def journal_boots_reader(
    response: ClientResponse,
) -> AsyncGenerator[tuple[int, str]]:
    """Read boots from json-seq response from systemd journal gateway.

    Returns generator of (index, boot_id) tuples.
    """
    async with response as resp:

        async def read_record() -> bytes:
            try:
                return await resp.content.readuntil(b"\x1e")
            except IncompleteReadError as e:
                return e.partial

        while line := await read_record():
            line = line.strip(b"\x1e")
            if not line:
                continue
            yield _parse_boot_json(line)

        return
