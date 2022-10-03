"""Test multicast api."""

from unittest.mock import MagicMock

from aiohttp.test_utils import TestClient

from tests.api.test_host import DEFAULT_RANGE


async def test_api_multicast_logs(api_client: TestClient, journald_logs: MagicMock):
    """Test multicast logs."""
    await api_client.get("/multicast/logs")
    journald_logs.assert_called_once_with(
        params={"SYSLOG_IDENTIFIER": "hassio_multicast"},
        range_header=DEFAULT_RANGE,
    )

    journald_logs.reset_mock()

    await api_client.get("/multicast/logs/follow")
    journald_logs.assert_called_once_with(
        params={"SYSLOG_IDENTIFIER": "hassio_multicast", "follow": ""},
        range_header=DEFAULT_RANGE,
    )
