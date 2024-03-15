"""Utilities for working with systemd journal export format."""
from collections.abc import AsyncGenerator, Iterable
from datetime import datetime
from functools import wraps
import struct

from aiohttp import ClientResponse

from supervisor.host.const import LogFormatter


class IncompleteEntryError(Exception):
    """Entry doesn't contain complete (binary) data.

    Raised when a journal entry isn't complete, likely because it contains
    multiple newlines in binary fields.
    """


class MultipleEntriesError(Exception):
    """Raised when a journal entry contains multiple entries."""


def parse_journal_export_entry(
    data: bytes, fields: Iterable[str] | None = None
) -> dict[str, str]:
    """Parse a single journal entry of Journal Export Format.

    Takes a bytes buffer `data` containing a single journal entry (nothing more, nothing
    less) and returns dict of entry: value pairs, optionally filtered by the `fields`
    argument.
    """
    entries = {}

    if not data:
        return entries

    for line in (lines := iter(data.split(b"\n"))):
        if not line:
            # previous line was a newline - only at the end of message or binary data
            try:
                if next(lines) == b"":
                    break
                raise MultipleEntriesError()
            except StopIteration as ex:
                raise IncompleteEntryError() from ex

        # Split the field name and value
        if b"=" in line:
            # Journal fields consisting only of valid non-control UTF-8 codepoints
            # are serialized as they are (i.e. the field name, followed by '=',
            # followed by field data), followed by a newline as separator to the next
            # field. Note that fields containing newlines cannot be formatted like
            # this. Non-control UTF-8 codepoints are the codepoints with value at or
            # above 32 (' '), or equal to 9 (TAB).
            field_name, field_value = (x.decode("utf-8") for x in line.split(b"=", 1))
            if fields and field_name not in fields:
                continue
        else:
            # Other journal fields are serialized in a special binary safe way:
            # field name, followed by newline,
            field_name = line.decode("utf-8")
            data = next(lines)
            # followed by a binary 64-bit little endian size value,
            length = struct.unpack_from("<Q", data)[0]
            # followed by the binary field data,
            # followed by a newline as separator to the next field.
            data = data[8:]
            # handle newlines in binary data
            while len(data) < length:
                data += b"\n" + next(lines)
            if fields and field_name not in fields:
                # we needed at least iterate up to the end of the data
                continue
            field_value = data.decode("utf-8")

        entries[field_name] = field_value

    return entries


def formatter(required_fields: list[str]):
    """Decorate journal entry formatters with list of required fields.

    Helper decorator that can be used for getting list of required fields for a journal
    formatter function using function.required_fields function attribute.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        wrapper.required_fields = required_fields
        return wrapper

    return decorator


@formatter(["MESSAGE"])
def journal_plain_formatter(entries: dict[str, str]) -> str:
    """Format parsed journal entries as a plain message."""
    return entries["MESSAGE"]


@formatter(
    [
        "__REALTIME_TIMESTAMP",
        "_HOSTNAME",
        "SYSLOG_IDENTIFIER",
        "_PID",
        "MESSAGE",
    ]
)
def journal_verbose_formatter(entries: dict[str, str]) -> str:
    """Format parsed journal entries to a journalctl-like format."""
    ts = datetime.fromtimestamp(int(entries["__REALTIME_TIMESTAMP"]) / 1e6).isoformat(
        sep=" ", timespec="milliseconds"
    )

    identifier = (
        f"{entries["SYSLOG_IDENTIFIER"]}[{entries["_PID"]}]"
        if "_PID" in entries
        else entries["SYSLOG_IDENTIFIER"]
    )

    return f"{ts} {entries["_HOSTNAME"]} {identifier}: " f"{entries["MESSAGE"]}"


async def journal_logs_reader(
    journal_logs: ClientResponse,
    log_formatter: LogFormatter = LogFormatter.PLAIN,
) -> AsyncGenerator[str, None]:
    """Read logs from systemd journal line by line, formatted using the given formatter."""
    match log_formatter:
        case LogFormatter.PLAIN:
            formatter_ = journal_plain_formatter
        case LogFormatter.VERBOSE:
            formatter_ = journal_verbose_formatter
        case _:
            raise ValueError(f"Unknown log format: {log_formatter}")

    async with journal_logs as resp:
        incomplete = b""
        while not resp.content.at_eof():
            entry = await resp.content.readuntil(b"\n\n")
            entry = incomplete + entry
            try:
                entries = parse_journal_export_entry(
                    entry, fields=formatter_.required_fields
                )
                incomplete = b""
            except IncompleteEntryError:
                incomplete = entry
                continue
            yield formatter_(entries)
