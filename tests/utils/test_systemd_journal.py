"""Test systemd journal utilities."""

import asyncio
from unittest.mock import ANY, MagicMock

import pytest

from supervisor.exceptions import MalformedBinaryEntryError
from supervisor.host.const import LogFormatter
from supervisor.utils.systemd_journal import (
    journal_logs_reader,
    journal_plain_formatter,
    journal_verbose_formatter,
)

from tests.common import load_fixture


def _journal_logs_mock():
    """Generate mocked stream for journal_logs_reader.

    Returns tuple for mocking ClientResponse and its StreamReader
    (.content attribute in async context).
    """
    stream = asyncio.StreamReader(loop=asyncio.get_running_loop())
    journal_logs = MagicMock()
    journal_logs.__aenter__.return_value.content = stream
    return journal_logs, stream


def test_format_simple():
    """Test plain formatter."""
    fields = {"MESSAGE": "Hello, world!"}
    assert journal_plain_formatter(fields) == "Hello, world!"


def test_format_simple_newlines():
    """Test plain formatter with newlines in message."""
    fields = {"MESSAGE": "Hello,\nworld!\n"}
    assert journal_plain_formatter(fields) == "Hello,\nworld!\n"


def test_format_verbose_timestamp():
    """Test timestamp is properly formatted."""
    fields = {
        "__REALTIME_TIMESTAMP": "1000",
        "_HOSTNAME": "x",
        "SYSLOG_IDENTIFIER": "x",
        "_PID": "1",
        "MESSAGE": "x",
    }
    formatted = journal_verbose_formatter(fields)
    assert formatted.startswith(
        "1970-01-01 00:00:00.001 "
    ), f"Invalid log timestamp: {formatted}"


def test_format_verbose():
    """Test verbose formatter."""
    fields = {
        "__REALTIME_TIMESTAMP": "1379403171000000",
        "_HOSTNAME": "homeassistant",
        "SYSLOG_IDENTIFIER": "python",
        "_PID": "666",
        "MESSAGE": "Hello, world!",
    }
    assert (
        journal_verbose_formatter(fields)
        == "2013-09-17 07:32:51.000 homeassistant python[666]: Hello, world!"
    )


def test_format_verbose_newlines():
    """Test verbose formatter with newlines in message."""
    fields = {
        "__REALTIME_TIMESTAMP": "1379403171000000",
        "_HOSTNAME": "homeassistant",
        "SYSLOG_IDENTIFIER": "python",
        "_PID": "666",
        "MESSAGE": "Hello,\nworld!\n",
    }
    assert (
        journal_verbose_formatter(fields)
        == "2013-09-17 07:32:51.000 homeassistant python[666]: Hello,\nworld!\n"
    )


async def test_parsing_simple():
    """Test plain formatter."""
    journal_logs, stream = _journal_logs_mock()
    stream.feed_data(b"MESSAGE=Hello, world!\n\n")
    _, line = await anext(journal_logs_reader(journal_logs))
    assert line == "Hello, world!"


async def test_parsing_verbose():
    """Test verbose formatter."""
    journal_logs, stream = _journal_logs_mock()
    stream.feed_data(
        b"__REALTIME_TIMESTAMP=1379403171000000\n"
        b"_HOSTNAME=homeassistant\n"
        b"SYSLOG_IDENTIFIER=python\n"
        b"_PID=666\n"
        b"MESSAGE=Hello, world!\n\n"
    )
    _, line = await anext(
        journal_logs_reader(journal_logs, log_formatter=LogFormatter.VERBOSE)
    )
    assert line == "2013-09-17 07:32:51.000 homeassistant python[666]: Hello, world!"


async def test_parsing_newlines_in_message():
    """Test reading and formatting using journal logs reader."""
    journal_logs, stream = _journal_logs_mock()
    stream.feed_data(
        b"ID=1\n"
        b"MESSAGE\n\x0d\x00\x00\x00\x00\x00\x00\x00Hello,\nworld!\n"
        b"AFTER=after\n\n"
    )

    _, line = await anext(journal_logs_reader(journal_logs))
    assert line == "Hello,\nworld!"


async def test_parsing_newlines_in_multiple_fields():
    """Test entries are correctly separated with newlines in multiple fields."""
    journal_logs, stream = _journal_logs_mock()
    stream.feed_data(
        b"ID=1\n"
        b"MESSAGE\n\x0e\x00\x00\x00\x00\x00\x00\x00Hello,\nworld!\n\n"
        b"ANOTHER\n\x0e\x00\x00\x00\x00\x00\x00\x00Hello,\nworld!\n\n"
        b"AFTER=after\n\n"
        b"ID=2\n"
        b"MESSAGE\n\x0d\x00\x00\x00\x00\x00\x00\x00Hello,\nworld!\n"
        b"AFTER=after\n\n"
    )

    assert await anext(journal_logs_reader(journal_logs)) == (ANY, "Hello,\nworld!\n")
    assert await anext(journal_logs_reader(journal_logs)) == (ANY, "Hello,\nworld!")


async def test_parsing_two_messages():
    """Test reading multiple messages."""
    journal_logs, stream = _journal_logs_mock()
    stream.feed_data(
        b"MESSAGE=Hello, world!\n"
        b"ID=1\n\n"
        b"MESSAGE=Hello again, world!\n"
        b"ID=2\n\n"
    )
    stream.feed_eof()

    reader = journal_logs_reader(journal_logs)
    assert await anext(reader) == (ANY, "Hello, world!")
    assert await anext(reader) == (ANY, "Hello again, world!")
    with pytest.raises(StopAsyncIteration):
        await anext(reader)


async def test_cursor_callback():
    """Test reading multiple messages."""
    journal_logs, stream = _journal_logs_mock()
    stream.feed_data(
        b"__CURSOR=cursor1\n"
        b"MESSAGE=Hello, world!\n"
        b"ID=1\n\n"
        b"__CURSOR=cursor2\n"
        b"MESSAGE=Hello again, world!\n"
        b"ID=2\n\n"
        b"MESSAGE=No cursor\n"
        b"ID=2\n\n"
    )
    stream.feed_eof()

    reader = journal_logs_reader(journal_logs)
    assert await anext(reader) == ("cursor1", "Hello, world!")
    assert await anext(reader) == ("cursor2", "Hello again, world!")
    assert await anext(reader) == (None, "No cursor")
    with pytest.raises(StopAsyncIteration):
        await anext(reader)


async def test_cursor_callback_no_cursor():
    """Test reading multiple messages."""
    journal_logs, stream = _journal_logs_mock()
    stream.feed_data(
        b"MESSAGE=Hello, world!\n"
        b"ID=1\n\n"
        b"MESSAGE=Hello again, world!\n"
        b"ID=2\n\n"
    )
    stream.feed_eof()

    reader = journal_logs_reader(journal_logs)
    assert await anext(reader) == (ANY, "Hello, world!")
    assert await anext(reader) == (ANY, "Hello again, world!")
    with pytest.raises(StopAsyncIteration):
        await anext(reader)


async def test_parsing_malformed_binary_message():
    """Test that malformed binary message raises MalformedBinaryEntryError."""
    journal_logs, stream = _journal_logs_mock()
    stream.feed_data(
        b"ID=1\n"
        b"MESSAGE\n\x0d\x00\x00\x00\x00\x00\x00\x00Hello, world!"
        b"AFTER=after\n\n"
    )

    with pytest.raises(MalformedBinaryEntryError):
        await anext(journal_logs_reader(journal_logs))


async def test_parsing_journal_host_logs():
    """Test parsing of real host logs."""
    journal_logs, stream = _journal_logs_mock()
    stream.feed_data(load_fixture("logs_export_host.txt").encode("utf-8"))
    _, line = await anext(journal_logs_reader(journal_logs))
    assert line == "Started Hostname Service."


async def test_parsing_colored_supervisor_logs():
    """Test parsing of real logs with ANSI escape sequences."""
    journal_logs, stream = _journal_logs_mock()
    stream.feed_data(load_fixture("logs_export_supervisor.txt").encode("utf-8"))
    _, line = await anext(journal_logs_reader(journal_logs))
    assert (
        line
        == "\x1b[32m24-03-04 23:56:56 INFO (MainThread) [__main__] Closing Supervisor\x1b[0m"
    )
