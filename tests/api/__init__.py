"""Test for API calls."""

from unittest.mock import MagicMock

from aiohttp.test_utils import TestClient

from supervisor.host.const import LogFormat

DEFAULT_LOG_RANGE = "entries=:-99:100"
DEFAULT_LOG_RANGE_FOLLOW = "entries=:-99:18446744073709551615"


async def common_test_api_advanced_logs(
    path_prefix: str,
    syslog_identifier: str,
    api_client: TestClient,
    journald_logs: MagicMock,
):
    """Template for tests of endpoints using advanced logs."""
    resp = await api_client.get(f"{path_prefix}/logs")
    assert resp.status == 200
    assert resp.content_type == "text/plain"

    journald_logs.assert_called_once_with(
        params={"SYSLOG_IDENTIFIER": syslog_identifier},
        range_header=DEFAULT_LOG_RANGE,
        accept=LogFormat.JOURNAL,
    )

    journald_logs.reset_mock()

    resp = await api_client.get(f"{path_prefix}/logs/follow")
    assert resp.status == 200
    assert resp.content_type == "text/plain"

    journald_logs.assert_called_once_with(
        params={"SYSLOG_IDENTIFIER": syslog_identifier, "follow": ""},
        range_header=DEFAULT_LOG_RANGE_FOLLOW,
        accept=LogFormat.JOURNAL,
    )

    journald_logs.reset_mock()

    resp = await api_client.get(f"{path_prefix}/logs/boots/0")
    assert resp.status == 200
    assert resp.content_type == "text/plain"

    journald_logs.assert_called_once_with(
        params={"SYSLOG_IDENTIFIER": syslog_identifier, "_BOOT_ID": "ccc"},
        range_header=DEFAULT_LOG_RANGE,
        accept=LogFormat.JOURNAL,
    )

    journald_logs.reset_mock()

    resp = await api_client.get(f"{path_prefix}/logs/boots/0/follow")
    assert resp.status == 200
    assert resp.content_type == "text/plain"

    journald_logs.assert_called_once_with(
        params={
            "SYSLOG_IDENTIFIER": syslog_identifier,
            "_BOOT_ID": "ccc",
            "follow": "",
        },
        range_header=DEFAULT_LOG_RANGE_FOLLOW,
        accept=LogFormat.JOURNAL,
    )
