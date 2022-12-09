"""Test multicast api."""

from unittest.mock import MagicMock

from aiohttp.test_utils import TestClient


async def test_api_multicast_logs(api_client: TestClient, docker_logs: MagicMock):
    """Test multicast logs."""
    resp = await api_client.get("/multicast/logs")
    assert resp.status == 200
    assert resp.content_type == "application/octet-stream"
    content = await resp.text()
    assert content.split("\n")[0:2] == [
        "\x1b[36m22-10-11 14:04:23 DEBUG (MainThread) [supervisor.utils.dbus] D-Bus call - org.freedesktop.DBus.Properties.call_get_all on /io/hass/os\x1b[0m",
        "\x1b[36m22-10-11 14:04:23 DEBUG (MainThread) [supervisor.utils.dbus] D-Bus call - org.freedesktop.DBus.Properties.call_get_all on /io/hass/os/AppArmor\x1b[0m",
    ]
