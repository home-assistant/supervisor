"""Test for API calls."""

from unittest.mock import AsyncMock, MagicMock

from aiohttp.test_utils import TestClient

from supervisor.coresys import CoreSys
from supervisor.host.const import LogFormat

DEFAULT_LOG_RANGE = "entries=:-99:100"
DEFAULT_LOG_RANGE_FOLLOW = "entries=:-99:18446744073709551615"


async def common_test_api_advanced_logs(
    path_prefix: str,
    syslog_identifier: str,
    api_client: TestClient,
    journald_logs: MagicMock,
    coresys: CoreSys,
    os_available: None,
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

    mock_response = MagicMock()
    mock_response.text = AsyncMock(
        return_value='{"CONTAINER_LOG_EPOCH": "12345"}\n{"CONTAINER_LOG_EPOCH": "12345"}\n'
    )
    journald_logs.return_value.__aenter__.return_value = mock_response

    resp = await api_client.get(f"{path_prefix}/logs/latest")
    assert resp.status == 200

    assert journald_logs.call_count == 2

    # Check the first call for getting epoch
    epoch_call = journald_logs.call_args_list[0]
    assert epoch_call[1]["params"] == {"CONTAINER_NAME": syslog_identifier}
    assert epoch_call[1]["range_header"] == "entries=:-1:2"

    # Check the second call for getting logs with the epoch
    logs_call = journald_logs.call_args_list[1]
    assert logs_call[1]["params"]["SYSLOG_IDENTIFIER"] == syslog_identifier
    assert logs_call[1]["params"]["CONTAINER_LOG_EPOCH"] == "12345"
    assert logs_call[1]["range_header"] == "entries=:0:18446744073709551615"

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
