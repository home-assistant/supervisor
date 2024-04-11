"""Utilities for working with systemd journal export format."""
from collections.abc import AsyncGenerator
from datetime import UTC, datetime
from functools import wraps

from aiohttp import ClientResponse

from supervisor.exceptions import MalformedBinaryEntryError
from supervisor.host.const import LogFormatter


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
    ts = datetime.fromtimestamp(
        int(entries["__REALTIME_TIMESTAMP"]) / 1e6, UTC
    ).isoformat(sep=" ", timespec="milliseconds")
    ts = ts[: ts.index(".") + 4]  # strip TZ offset

    identifier = (
        f"{entries.get("SYSLOG_IDENTIFIER", "_UNKNOWN_")}[{entries["_PID"]}]"
        if "_PID" in entries
        else entries.get("SYSLOG_IDENTIFIER", "_UNKNOWN_")
    )

    return f"{ts} {entries.get("_HOSTNAME", "")} {identifier}: {entries.get("MESSAGE", "")}"


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
        entries: dict[str, str] = {}
        while not resp.content.at_eof():
            line = await resp.content.readuntil(b"\n")
            # newline means end of message, also empty line is sometimes returned
            # at EOF (likely race between at_eof and EOF check in readuntil)
            if line == b"\n" or not line:
                if entries:
                    yield formatter_(entries)
                entries = {}
                continue

            # Journal fields consisting only of valid non-control UTF-8 codepoints
            # are serialized as they are (i.e. the field name, followed by '=',
            # followed by field data), followed by a newline as separator to the next
            # field. Note that fields containing newlines cannot be formatted like
            # this. Non-control UTF-8 codepoints are the codepoints with value at or
            # above 32 (' '), or equal to 9 (TAB).
            name, sep, data = line.partition(b"=")
            if not sep:
                # Other journal fields are serialized in a special binary safe way:
                # field name, followed by newline
                name = name[:-1]  # strip \n
                # followed by a binary 64-bit little endian size value,
                length_raw = await resp.content.readexactly(8)
                length = int.from_bytes(length_raw, byteorder="little")
                # followed by the binary field data,
                data = await resp.content.readexactly(length + 1)
                # followed by a newline as separator to the next field.
                if not data.endswith(b"\n"):
                    raise MalformedBinaryEntryError(
                        f"Failed parsing binary entry {data}"
                    )

            name = name.decode("utf-8")
            if name not in formatter_.required_fields:
                # we must read to the end of the entry in the stream, so we can
                # only continue the loop here
                continue

            # strip \n for simple fields before decoding
            entries[name] = data[:-1].decode("utf-8")
