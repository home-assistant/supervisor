"""Test DNS API."""

from unittest.mock import patch

from aiohttp.test_utils import TestClient

from supervisor.coresys import CoreSys
from supervisor.dbus.resolved import Resolved
from supervisor.host.const import LogFormatter

from tests.dbus_service_mocks.base import DBusServiceMock
from tests.dbus_service_mocks.resolved import Resolved as ResolvedService


async def test_llmnr_mdns_info(
    api_client_with_prefix: tuple[TestClient, str],
    coresys: CoreSys,
    all_dbus_services: dict[str, DBusServiceMock | dict[str, DBusServiceMock]],
):
    """Test llmnr and mdns in info api."""
    api_client, prefix = api_client_with_prefix
    resolved_service: ResolvedService = all_dbus_services["resolved"]

    # pylint: disable=protected-access
    coresys.host.sys_dbus._resolved = Resolved()
    # pylint: enable=protected-access

    resp = await api_client.get(f"{prefix}/dns/info")
    result = await resp.json()
    assert result["data"]["llmnr"] is False
    assert result["data"]["mdns"] is False

    await coresys.dbus.resolved.connect(coresys.dbus.bus)
    resp = await api_client.get(f"{prefix}/dns/info")
    result = await resp.json()
    assert result["data"]["llmnr"] is True
    assert result["data"]["mdns"] is True

    resolved_service.emit_properties_changed({"LLMNR": "no", "MulticastDNS": "no"})
    await resolved_service.ping()

    resp = await api_client.get(f"{prefix}/dns/info")
    result = await resp.json()
    assert result["data"]["llmnr"] is False
    assert result["data"]["mdns"] is False


async def test_info_includes_search_domains(api_client: TestClient, coresys: CoreSys):
    """Test search_domains is present in DNS info response."""
    assert coresys.plugins.dns.search_domains == []

    resp = await api_client.get("/dns/info")
    result = await resp.json()
    assert "search_domains" in result["data"]
    assert result["data"]["search_domains"] == []

    coresys.plugins.dns.search_domains = ["example.com", "local.hass.io"]

    resp = await api_client.get("/dns/info")
    result = await resp.json()
    assert result["data"]["search_domains"] == ["example.com", "local.hass.io"]


async def test_options(
    api_client_with_prefix: tuple[TestClient, str], coresys: CoreSys
):
    """Test options api."""
    api_client, prefix = api_client_with_prefix
    assert coresys.plugins.dns.servers == []
    assert coresys.plugins.dns.fallback is True
    assert coresys.plugins.dns.search_domains == []

    with patch.object(type(coresys.plugins.dns), "restart") as restart:
        await api_client.post(
            f"{prefix}/dns/options",
            json={"servers": ["dns://8.8.8.8"], "fallback": False},
        )

        assert coresys.plugins.dns.servers == ["dns://8.8.8.8"]
        assert coresys.plugins.dns.fallback is False
        restart.assert_called_once()

        restart.reset_mock()
        await api_client.post(f"{prefix}/dns/options", json={"fallback": True})

        assert coresys.plugins.dns.servers == ["dns://8.8.8.8"]
        assert coresys.plugins.dns.fallback is True
        restart.assert_called_once()


async def test_options_search_domains(api_client: TestClient, coresys: CoreSys):
    """Test setting search_domains via options api."""
    assert coresys.plugins.dns.search_domains == []

    with patch.object(type(coresys.plugins.dns), "restart") as restart:
        resp = await api_client.post(
            "/dns/options",
            json={"search_domains": ["example.com", "local.hass.io"]},
        )
        assert resp.status == 200
        assert coresys.plugins.dns.search_domains == ["example.com", "local.hass.io"]
        # search_domains alone does not trigger a CoreDNS restart
        restart.assert_not_called()

        await api_client.post("/dns/options", json={"search_domains": []})
        assert coresys.plugins.dns.search_domains == []

        await api_client.post(
            "/dns/options",
            json={"servers": ["dns://1.1.1.1"], "search_domains": ["corp.example.com"]},
        )
        assert coresys.plugins.dns.servers == ["dns://1.1.1.1"]
        assert coresys.plugins.dns.search_domains == ["corp.example.com"]
        restart.assert_called_once()


async def test_api_dns_logs(advanced_logs_tester):
    """Test dns logs."""
    await advanced_logs_tester("/dns", "hassio_dns", LogFormatter.VERBOSE)
