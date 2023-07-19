"""Test homeassistant api."""

from unittest.mock import MagicMock

from aiohttp.test_utils import TestClient
import pytest

from supervisor.coresys import CoreSys

from tests.common import load_json_fixture


@pytest.mark.parametrize("legacy_route", [True, False])
async def test_api_core_logs(
    api_client: TestClient, docker_logs: MagicMock, legacy_route: bool
):
    """Test core logs."""
    resp = await api_client.get(f"/{'homeassistant' if legacy_route else 'core'}/logs")
    assert resp.status == 200
    assert resp.content_type == "application/octet-stream"
    content = await resp.text()
    assert content.split("\n")[0:2] == [
        "\x1b[36m22-10-11 14:04:23 DEBUG (MainThread) [supervisor.utils.dbus] D-Bus call - org.freedesktop.DBus.Properties.call_get_all on /io/hass/os\x1b[0m",
        "\x1b[36m22-10-11 14:04:23 DEBUG (MainThread) [supervisor.utils.dbus] D-Bus call - org.freedesktop.DBus.Properties.call_get_all on /io/hass/os/AppArmor\x1b[0m",
    ]


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
