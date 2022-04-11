"""Test DNS API."""
from unittest.mock import PropertyMock, patch

from supervisor.coresys import CoreSys
from supervisor.dbus.const import MulticastProtocolEnabled


async def test_llmnr_mdns_info(api_client, coresys: CoreSys):
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

    await coresys.dbus.resolved.connect()
    await coresys.dbus.resolved.update()

    resp = await api_client.get("/dns/info")
    result = await resp.json()
    assert result["data"]["llmnr"] is True
    assert result["data"]["mdns"] is True
