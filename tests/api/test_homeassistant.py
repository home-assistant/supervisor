"""Test homeassistant api."""

from unittest.mock import MagicMock

from aiohttp.test_utils import TestClient

from .test_host import DEFAULT_RANGE


async def test_api_core_logs(api_client: TestClient, journald_logs: MagicMock):
    """Test core logs."""
    await api_client.get("/core/logs")
    journald_logs.assert_called_once_with(
        params={"SYSLOG_IDENTIFIER": "homeassistant"},
        range_header=DEFAULT_RANGE,
    )

    journald_logs.reset_mock()

    await api_client.get("/core/logs/follow")
    journald_logs.assert_called_once_with(
        params={"SYSLOG_IDENTIFIER": "homeassistant", "follow": ""},
        range_header=DEFAULT_RANGE,
    )


# Legacy routing path to logs. Does not support /follow
async def test_api_homeassistant_logs(api_client: TestClient, journald_logs: MagicMock):
    """Test legacy routing to logs."""
    await api_client.get("/homeassistant/logs")
    journald_logs.assert_called_once_with(
        params={"SYSLOG_IDENTIFIER": "homeassistant"},
        range_header=DEFAULT_RANGE,
    )
