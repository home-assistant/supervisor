"""Test multicast api."""

from unittest.mock import MagicMock

from aiohttp.test_utils import TestClient

from supervisor.host.const import LogFormat

DEFAULT_LOG_RANGE = "entries=:-100:"


async def test_api_multicast_logs(api_client: TestClient, journald_logs: MagicMock):
    """Test multicast logs."""
    resp = await api_client.get("/multicast/logs")
    assert resp.status == 200
    assert resp.content_type == "text/plain"

    journald_logs.assert_called_once_with(
        params={"SYSLOG_IDENTIFIER": "hassio_multicast"},
        range_header=DEFAULT_LOG_RANGE,
        accept=LogFormat.JOURNAL,
    )

    journald_logs.reset_mock()

    resp = await api_client.get("/multicast/logs/follow")
    assert resp.status == 200
    assert resp.content_type == "text/plain"

    journald_logs.assert_called_once_with(
        params={"SYSLOG_IDENTIFIER": "hassio_multicast", "follow": ""},
        range_header=DEFAULT_LOG_RANGE,
        accept=LogFormat.JOURNAL,
    )

    journald_logs.reset_mock()

    resp = await api_client.get("/multicast/logs/boots/0")
    assert resp.status == 200
    assert resp.content_type == "text/plain"

    journald_logs.assert_called_once_with(
        params={"SYSLOG_IDENTIFIER": "hassio_multicast", "_BOOT_ID": "ccc"},
        range_header=DEFAULT_LOG_RANGE,
        accept=LogFormat.JOURNAL,
    )

    journald_logs.reset_mock()

    resp = await api_client.get("/multicast/logs/boots/0/follow")
    assert resp.status == 200
    assert resp.content_type == "text/plain"

    journald_logs.assert_called_once_with(
        params={
            "SYSLOG_IDENTIFIER": "hassio_multicast",
            "_BOOT_ID": "ccc",
            "follow": "",
        },
        range_header=DEFAULT_LOG_RANGE,
        accept=LogFormat.JOURNAL,
    )
