"""Test audio api."""

from unittest.mock import MagicMock

from aiohttp.test_utils import TestClient

from supervisor.host.const import LogFormat

DEFAULT_LOG_RANGE = "entries=:-100:"


async def test_api_audio_logs(api_client: TestClient, journald_logs: MagicMock):
    """Test audio logs."""
    resp = await api_client.get("/audio/logs")
    assert resp.status == 200
    assert resp.content_type == "text/plain"

    journald_logs.assert_called_once_with(
        params={"SYSLOG_IDENTIFIER": "hassio_audio"},
        range_header=DEFAULT_LOG_RANGE,
        accept=LogFormat.JOURNAL,
    )

    journald_logs.reset_mock()

    resp = await api_client.get("/audio/logs/follow")
    assert resp.status == 200
    assert resp.content_type == "text/plain"

    journald_logs.assert_called_once_with(
        params={"SYSLOG_IDENTIFIER": "hassio_audio", "follow": ""},
        range_header=DEFAULT_LOG_RANGE,
        accept=LogFormat.JOURNAL,
    )

    journald_logs.reset_mock()

    resp = await api_client.get("/audio/logs/boots/0")
    assert resp.status == 200
    assert resp.content_type == "text/plain"

    journald_logs.assert_called_once_with(
        params={"SYSLOG_IDENTIFIER": "hassio_audio", "_BOOT_ID": "ccc"},
        range_header=DEFAULT_LOG_RANGE,
        accept=LogFormat.JOURNAL,
    )

    journald_logs.reset_mock()

    resp = await api_client.get("/audio/logs/boots/0/follow")
    assert resp.status == 200
    assert resp.content_type == "text/plain"

    journald_logs.assert_called_once_with(
        params={"SYSLOG_IDENTIFIER": "hassio_audio", "_BOOT_ID": "ccc", "follow": ""},
        range_header=DEFAULT_LOG_RANGE,
        accept=LogFormat.JOURNAL,
    )
