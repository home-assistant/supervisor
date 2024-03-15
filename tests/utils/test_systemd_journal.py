"""Test systemd journal utilities."""
from unittest.mock import AsyncMock, MagicMock

import pytest

from supervisor.utils.systemd_journal import (
    IncompleteEntryError,
    MultipleEntriesError,
    journal_logs_reader,
    journal_plain_formatter,
    journal_verbose_formatter,
    parse_journal_export_entry,
)


def test_parse_simple():
    """Simple parsing test."""
    entry = b"A=1\nB=2\n\n"
    entries = parse_journal_export_entry(entry)
    assert entries == {
        "A": "1",
        "B": "2",
    }


def test_parse_selected_fields():
    """Test extracting only selected fields."""
    entry = b"A=1\nB=2\n\n"
    entries = parse_journal_export_entry(entry, fields=("A",))
    assert entries == {
        "A": "1",
    }


def test_parse_binary_newlines():
    """Test parsing binary message with newlines."""
    entry = (
        b"BEFORE=before\n"
        b"_SELINUX_CONTEXT\n\x0b\x00\x00\x00\x00\x00\x00\x00unconfined\n\n"
        b"AFTER=after\n\n"
    )
    entries = parse_journal_export_entry(entry)
    assert entries == {
        "_SELINUX_CONTEXT": "unconfined\n",
        "BEFORE": "before",
        "AFTER": "after",
    }


def test_parse_binary_only_newlines():
    """Test parsing binary message containing only newlines."""
    entry = (
        b"BEFORE=before\n"
        b"_SELINUX_CONTEXT\n\x0b\x00\x00\x00\x00\x00\x00\x00\n\n\n\n\n\n\n\n\n\n\n\n"
        b"AFTER=after\n\n"
    )
    entries = parse_journal_export_entry(entry)
    assert entries == {
        "_SELINUX_CONTEXT": "\n\n\n\n\n\n\n\n\n\n\n",
        "BEFORE": "before",
        "AFTER": "after",
    }


def test_parse_multiple_messages():
    """Parsing multiple journal entries raises error."""
    entry = b"A=1\nB=2\n\n" b"A=3\nB=4\n\n"
    with pytest.raises(MultipleEntriesError):
        parse_journal_export_entry(entry)


def test_parse_multiple_messages_binary():
    """Message followed by another message starting with binary field raises error."""
    entry = (
        b"A=1\nB=2\n\n"
        b"_SELINUX_CONTEXT\n\x0b\x00\x00\x00\x00\x00\x00\x00unconfined\n\n\n"
    )
    with pytest.raises(MultipleEntriesError):
        parse_journal_export_entry(entry)


def test_parse_binary_multiple_newlines_incomplete_raises_error():
    """Incomplete binary message with newlines raises error."""
    entry = (
        b"BEFORE=before\n"
        b"_SELINUX_CONTEXT\n\x0b\x00\x00\x00\x00\x00\x00\x00unconfined\n\n"
    )
    with pytest.raises(IncompleteEntryError):
        parse_journal_export_entry(entry)


def test_format_simple():
    """Test plain formatter."""
    fields = {"MESSAGE": "Hello, world!"}
    assert journal_plain_formatter(fields) == "Hello, world!"


def test_format_simple_newlines():
    """Test plain formatter with newlines in message."""
    fields = {"MESSAGE": "Hello,\nworld!\n"}
    assert journal_plain_formatter(fields) == "Hello,\nworld!\n"


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
        == "2013-09-17 09:32:51.000 homeassistant python[666]: Hello, world!"
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
        == "2013-09-17 09:32:51.000 homeassistant python[666]: Hello,\nworld!\n"
    )


async def test_journal_logs_reader():
    """Test reading and formatting using journal logs reader."""
    entry = (
        b"MESSAGE=Hello, world!\n"
        b"_SELINUX_CONTEXT\n\x0b\x00\x00\x00\x00\x00\x00\x00unconfined\n\n"
        b"AFTER=after"
    )

    journal_logs = MagicMock()
    at_eof = MagicMock(return_value=False)
    at_eof.side_effect = [False, True]
    readuntil = AsyncMock(
        return_value=entry,
    )

    journal_logs.__aenter__.return_value.content.readuntil = readuntil
    journal_logs.__aenter__.return_value.content.at_eof = at_eof

    async for line in journal_logs_reader(journal_logs):
        assert line == "Hello, world!"

    assert at_eof.call_count == 2
    assert readuntil.call_count == 1


async def test_journal_logs_reader_two_messages():
    """Test reading multiple messages."""
    entry1 = b"MESSAGE=Hello, world!\n" b"ID=1"
    entry2 = b"MESSAGE=Hello again, world!\n" b"ID=2"

    journal_logs = MagicMock()
    at_eof = MagicMock(return_value=False)
    at_eof.side_effect = [False, False, True]

    readuntil = AsyncMock(return_value=entry1, side_effect=[entry1, entry2])

    journal_logs.__aenter__.return_value.content.readuntil = readuntil
    journal_logs.__aenter__.return_value.content.at_eof = at_eof

    async for line in journal_logs_reader(journal_logs):
        if readuntil.call_count == 1:
            assert line == "Hello, world!"
        if readuntil.call_count == 2:
            assert line == "Hello again, world!"

    assert at_eof.call_count == 3
    assert readuntil.call_count == 2


async def test_journal_logs_reader_incomplete_readuntil():
    """Test fetching remaining data after incomplete readuntil."""
    entry_incomplete = (
        b"BEFORE=before\n"
        b"_SELINUX_CONTEXT\n\x0b\x00\x00\x00\x00\x00\x00\x00unconfined\n\n"
    )
    entry_complete = (
        b"BEFORE=before\n"
        b"_SELINUX_CONTEXT\n\x0b\x00\x00\x00\x00\x00\x00\x00unconfined\n\n"
        b"MESSAGE=Hello, world!\n\n"
    )

    journal_logs = MagicMock()
    at_eof = MagicMock(return_value=False)
    at_eof.side_effect = [False, False, True]

    readuntil = AsyncMock(
        return_value=entry_incomplete, side_effect=[entry_incomplete, entry_complete]
    )

    journal_logs.__aenter__.return_value.content.readuntil = readuntil
    journal_logs.__aenter__.return_value.content.at_eof = at_eof

    async for line in journal_logs_reader(journal_logs):
        assert line == "Hello, world!"

    assert at_eof.call_count == 3
    assert readuntil.call_count == 2
