"""Test DNS API."""

from unittest.mock import MagicMock, patch

from aiohttp.test_utils import TestClient

from supervisor.coresys import CoreSys
from supervisor.dbus.resolved import Resolved

from tests.api import common_test_api_advanced_logs
from tests.dbus_service_mocks.base import DBusServiceMock
from tests.dbus_service_mocks.resolved import Resolved as ResolvedService


async def test_llmnr_mdns_info(
    api_client: TestClient,
    coresys: CoreSys,
    all_dbus_services: dict[str, DBusServiceMock | dict[str, DBusServiceMock]],
):
    """Test llmnr and mdns in info api."""
    resolved_service: ResolvedService = all_dbus_services["resolved"]

    # pylint: disable=protected-access
    coresys.host.sys_dbus._resolved = Resolved()
    # pylint: enable=protected-access

    resp = await api_client.get("/dns/info")
    result = await resp.json()
    assert result["data"]["llmnr"] is False
    assert result["data"]["mdns"] is False

    await coresys.dbus.resolved.connect(coresys.dbus.bus)
    resp = await api_client.get("/dns/info")
    result = await resp.json()
    assert result["data"]["llmnr"] is True
    assert result["data"]["mdns"] is True

    resolved_service.emit_properties_changed({"LLMNR": "no", "MulticastDNS": "no"})
    await resolved_service.ping()

    resp = await api_client.get("/dns/info")
    result = await resp.json()
    assert result["data"]["llmnr"] is False
    assert result["data"]["mdns"] is False


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


async def test_api_dns_logs(api_client: TestClient, journald_logs: MagicMock):
    """Test dns logs."""
    await common_test_api_advanced_logs("/dns", "hassio_dns", api_client, journald_logs)
