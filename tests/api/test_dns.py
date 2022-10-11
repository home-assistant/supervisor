"""Test DNS API."""
from unittest.mock import MagicMock, PropertyMock, patch

from aiohttp.test_utils import TestClient

from supervisor.coresys import CoreSys
from supervisor.dbus.const import MulticastProtocolEnabled


async def test_llmnr_mdns_info(
    api_client: TestClient, coresys: CoreSys, dbus_is_connected: PropertyMock
):
    """Test llmnr and mdns in info api."""
    coresys.host.sys_dbus.resolved.is_connected = False

    resp = await api_client.get("/dns/info")
    result = await resp.json()
    assert result["data"]["llmnr"] is False
    assert result["data"]["mdns"] is False

    coresys.host.sys_dbus.resolved.is_connected = True
    with patch.object(
        type(coresys.host.sys_dbus.resolved),
        "llmnr",
        PropertyMock(return_value=MulticastProtocolEnabled.NO),
    ), patch.object(
        type(coresys.host.sys_dbus.resolved),
        "multicast_dns",
        PropertyMock(return_value=MulticastProtocolEnabled.NO),
    ):
        resp = await api_client.get("/dns/info")
        result = await resp.json()
        assert result["data"]["llmnr"] is False
        assert result["data"]["mdns"] is False

    await coresys.dbus.resolved.connect(coresys.dbus.bus)
    await coresys.dbus.resolved.update()

    resp = await api_client.get("/dns/info")
    result = await resp.json()
    assert result["data"]["llmnr"] is True
    assert result["data"]["mdns"] is True


async def test_options(api_client: TestClient, coresys: CoreSys):
    """Test options api."""
    assert coresys.plugins.dns.servers == []
    assert coresys.plugins.dns.fallback is True

    with patch.object(type(coresys.plugins.dns), "restart") as restart:
        await api_client.post(
            "/dns/options", json={"servers": ["dns://8.8.8.8"], "fallback": False}
        )

        assert coresys.plugins.dns.servers == ["dns://8.8.8.8"]
        assert coresys.plugins.dns.fallback is False
        restart.assert_called_once()

        restart.reset_mock()
        await api_client.post("/dns/options", json={"fallback": True})

        assert coresys.plugins.dns.servers == ["dns://8.8.8.8"]
        assert coresys.plugins.dns.fallback is True
        restart.assert_called_once()


async def test_api_dns_logs(api_client: TestClient, docker_logs: MagicMock):
    """Test dns logs."""
    resp = await api_client.get("/dns/logs")
    assert resp.status == 200
    assert resp.content_type == "application/octet-stream"
    content = await resp.text()
    assert content.split("\n")[0:2] == [
        "\x1b[36m22-10-11 14:04:23 DEBUG (MainThread) [supervisor.utils.dbus] D-Bus call - org.freedesktop.DBus.Properties.call_get_all on /io/hass/os\x1b[0m",
        "\x1b[36m22-10-11 14:04:23 DEBUG (MainThread) [supervisor.utils.dbus] D-Bus call - org.freedesktop.DBus.Properties.call_get_all on /io/hass/os/AppArmor\x1b[0m",
    ]
