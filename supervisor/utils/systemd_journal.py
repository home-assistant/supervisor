"""Utilities for working with systemd journal export format."""

from asyncio import IncompleteReadError
from collections.abc import AsyncGenerator, Iterable
from datetime import UTC, datetime, tzinfo
from functools import wraps
import json
import re

from aiohttp import ClientResponse

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

# An entry made only of "NAME=value" lines; binary fields have no "=" on
# their name line.
_RE_SIMPLE_ENTRY = re.compile(rb"(?:[^\n=]+=[^\n]*\n)+")


class JournalExportParser:
    """Incremental parser for the systemd journal export format.

    Feed it the raw stream in any chunking and it returns the completed
    entries as dicts holding only the requested fields.
    """

    def __init__(self, fields: Iterable[str]) -> None:
        """Initialize the parser for the given field names."""
        self._keys = [(name, f"\n{name}=".encode()) for name in fields]
        self._names = {key[1:-1]: name for name, key in self._keys}
        # A newline always precedes the parse position so a "NAME=" search also
        # matches the first field of an entry
        self._buf = bytearray(b"\n")
        self._pos = 1
        # Where the search for the end of the current entry can resume, and the
        # buffer length a binary field needs before the entry can be parsed
        self._scan = 0
        self._need = 0

    def feed(self, data: bytes) -> list[dict[str, str]]:
        """Parse data and return the entries completed by it."""
        self._buf += data
        if len(self._buf) < self._need:
            return []

        entries: list[dict[str, str]] = []
        while self._pos < len(self._buf) and (entry := self._parse_entry()) is not None:
            if entry:
                entries.append(entry)

        # Drop consumed data once it outweighs the pending entry, which keeps
        # the copying linear for entries spanning many reads
        if self._pos - 1 > len(self._buf) // 2:
            del self._buf[: self._pos - 1]
            self._scan = max(0, self._scan - (self._pos - 1))
            self._pos = 1
        return entries

    def close(self) -> list[dict[str, str]]:
        """Return a trailing entry that was cut off at the end of the stream."""
        if self._pos >= len(self._buf):
            return []
        # Check the binary framing against the real bytes before terminating
        # the entry, as the terminator could stand in for a missing separator
        self._parse_fields(self._pos)
        if len(self._buf) < self._need:
            raise MalformedBinaryEntryError("Stream ended inside a binary field")
        return self.feed(b"\n\n")

    def _parse_entry(self) -> dict[str, str] | None:
        """Parse the entry at the current position, or return None if incomplete."""
        buf, pos = self._buf, self._pos
        end = buf.find(b"\n\n", max(pos - 1, self._scan))
        if end == -1:
            self._scan = len(buf) - 1
            return None
        self._scan = 0
        self._need = 0
        if end == pos - 1:
            # Empty line, e.g. at EOF or between entries
            self._pos = pos + 1
            return {}

        entry: dict[str, str] = {}
        if _RE_SIMPLE_ENTRY.fullmatch(buf, pos, end + 1):
            for name, key in self._keys:
                # Last occurrence wins for repeated fields
                start = buf.rfind(key, pos - 1, end + 1)
                if start != -1:
                    start += len(key)
                    entry[name] = buf[start : buf.index(b"\n", start)].decode(
                        "utf-8", errors="replace"
                    )
            self._pos = end + 2
            return entry

        # The entry has binary fields whose data may contain anything, including
        # "\n\n", so walk it field by field
        if (parsed := self._parse_fields(pos)) is None:
            return None
        entry, self._pos = parsed
        return entry

    def _parse_fields(self, pos: int) -> tuple[dict[str, str], int] | None:
        """Parse the fields of the entry at pos, or return None if incomplete."""
        buf = self._buf
        entry: dict[str, str] = {}
        while True:
            line_end = buf.find(b"\n", pos)
            if line_end == -1:
                return None
            if line_end == pos:
                return entry, pos + 1

            sep = buf.find(b"=", pos, line_end)
            if sep != -1:
                field = bytes(buf[pos:sep])
                data_start, data_end = sep + 1, line_end
            else:
                # Binary field: name, newline, little endian 64-bit size, data, newline
                field = bytes(buf[pos:line_end])
                data_start = line_end + 9
                if len(buf) < data_start:
                    self._need = data_start
                    return None
                data_end = data_start + int.from_bytes(
                    buf[line_end + 1 : data_start], byteorder="little"
                )
                if len(buf) <= data_end:
                    self._need = data_end + 1
                    return None
                if buf[data_end] != 0x0A:
                    raise MalformedBinaryEntryError(
                        f"Failed parsing binary entry {buf[data_start : data_end + 1].decode('utf-8', errors='replace')}"
                    )
            pos = data_end + 1
            if field in self._names:
                entry[self._names[field]] = buf[data_start:data_end].decode(
                    "utf-8", errors="replace"
                )


async def journal_logs_reader(
    journal_logs: ClientResponse,
    log_formatter: LogFormatter = LogFormatter.PLAIN,
    no_colors: bool = False,
    tz: tzinfo = UTC,
) -> AsyncGenerator[list[tuple[str | None, str]]]:
    """Read logs from systemd journal, formatted using the given formatter.

    Optionally strip ANSI color codes from the entries' messages. Timestamps are
    converted to the given timezone.

    Returns a generator of (cursor, formatted_entry) tuple lists. Each list holds
    the entries completed by one read from the stream, so a consumer that writes
    a list at a time does not add latency when following logs.
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

    def format_batch(entries: list[dict[str, str]]) -> list[tuple[str | None, str]]:
        return [
            (entry.get("__CURSOR"), formatter_(entry, no_colors=no_colors, tz=tz))
            for entry in entries
        ]

    async with journal_logs as resp:
        while chunk := await resp.content.read(JOURNAL_READ_SIZE):
            if batch := format_batch(parser.feed(chunk)):
                yield batch
        if batch := format_batch(parser.close()):
            yield batch


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
