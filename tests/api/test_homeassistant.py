"""Test homeassistant api."""

from unittest.mock import MagicMock, patch

from aiohttp.test_utils import TestClient
import pytest

from supervisor.coresys import CoreSys
from supervisor.homeassistant.module import HomeAssistant
from supervisor.host.const import LogFormat

from tests.common import load_json_fixture

DEFAULT_LOG_RANGE = "entries=:-100:"


@pytest.mark.parametrize("legacy_route", [True, False])
async def test_api_core_logs(
    api_client: TestClient, journald_logs: MagicMock, legacy_route: bool
):
    """Test core logs."""
    resp = await api_client.get(f"/{'homeassistant' if legacy_route else 'core'}/logs")
    assert resp.status == 200
    assert resp.content_type == "text/plain"

    journald_logs.assert_called_once_with(
        params={"SYSLOG_IDENTIFIER": "homeassistant"},
        range_header=DEFAULT_LOG_RANGE,
        accept=LogFormat.JOURNAL,
    )

    journald_logs.reset_mock()

    resp = await api_client.get(
        f"/{'homeassistant' if legacy_route else 'core'}/logs/follow"
    )
    assert resp.status == 200
    assert resp.content_type == "text/plain"

    journald_logs.assert_called_once_with(
        params={"SYSLOG_IDENTIFIER": "homeassistant", "follow": ""},
        range_header=DEFAULT_LOG_RANGE,
        accept=LogFormat.JOURNAL,
    )

    journald_logs.reset_mock()

    resp = await api_client.get(
        f"/{'homeassistant' if legacy_route else 'core'}/logs/boots/0"
    )
    assert resp.status == 200
    assert resp.content_type == "text/plain"

    journald_logs.assert_called_once_with(
        params={"SYSLOG_IDENTIFIER": "homeassistant", "_BOOT_ID": "ccc"},
        range_header=DEFAULT_LOG_RANGE,
        accept=LogFormat.JOURNAL,
    )

    journald_logs.reset_mock()

    resp = await api_client.get(
        f"/{'homeassistant' if legacy_route else 'core'}/logs/boots/0/follow"
    )
    assert resp.status == 200
    assert resp.content_type == "text/plain"

    journald_logs.assert_called_once_with(
        params={"SYSLOG_IDENTIFIER": "homeassistant", "_BOOT_ID": "ccc", "follow": ""},
        range_header=DEFAULT_LOG_RANGE,
        accept=LogFormat.JOURNAL,
    )


async def test_api_stats(api_client: TestClient, coresys: CoreSys):
    """Test stats."""
    coresys.docker.containers.get.return_value.status = "running"
    coresys.docker.containers.get.return_value.stats.return_value = load_json_fixture(
        "container_stats.json"
    )

    resp = await api_client.get("/homeassistant/stats")
    assert resp.status == 200
    result = await resp.json()
    assert result["data"]["cpu_percent"] == 90.0
    assert result["data"]["memory_usage"] == 59700000
    assert result["data"]["memory_limit"] == 4000000000
    assert result["data"]["memory_percent"] == 1.49


async def test_api_set_options(api_client: TestClient, coresys: CoreSys):
    """Test setting options for homeassistant."""
    resp = await api_client.get("/homeassistant/info")
    assert resp.status == 200
    result = await resp.json()
    assert result["data"]["watchdog"] is True
    assert result["data"]["backups_exclude_database"] is False

    with patch.object(HomeAssistant, "save_data") as save_data:
        resp = await api_client.post(
            "/homeassistant/options",
            json={"backups_exclude_database": True, "watchdog": False},
        )
        assert resp.status == 200
        save_data.assert_called_once()

    resp = await api_client.get("/homeassistant/info")
    assert resp.status == 200
    result = await resp.json()
    assert result["data"]["watchdog"] is False
    assert result["data"]["backups_exclude_database"] is True
