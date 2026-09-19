"""Test DNS API."""

from unittest.mock import AsyncMock, patch

from aiodocker.containers import DockerContainer
from aiohttp.test_utils import TestClient

from supervisor.coresys import CoreSys
from supervisor.dbus.resolved import Resolved
from supervisor.docker.manager import DockerAPI
from supervisor.host.const import LogFormatter

from tests.common import load_json_fixture
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


async def test_api_dns_stats(
    api_client_with_prefix: tuple[TestClient, str], container: DockerContainer
):
    """Test DNS stats."""
    api_client, prefix = api_client_with_prefix
    container.show.return_value["State"]["Status"] = "running"
    container.show.return_value["State"]["Running"] = True

    if prefix == "/v2":
        stats_fixture = load_json_fixture("container_stats.json")
        del stats_fixture["precpu_stats"]
        with patch.object(
            DockerAPI,
            "_query_one_shot_stats",
            AsyncMock(return_value=stats_fixture),
        ):
            resp = await api_client.get(f"{prefix}/dns/stats")
    else:
        container.stats = AsyncMock(
            return_value=[load_json_fixture("container_stats.json")]
        )
        resp = await api_client.get(f"{prefix}/dns/stats")

    assert resp.status == 200
    result = await resp.json()
    if prefix == "/v2":
        assert "cpu_percent" not in result["data"]
    else:
        assert result["data"]["cpu_percent"] == 90.0
    assert result["data"]["memory_usage"] == 59700000


async def test_options(
    api_client_with_prefix: tuple[TestClient, str], coresys: CoreSys
):
    """Test options api."""
    api_client, prefix = api_client_with_prefix
    assert coresys.plugins.dns.servers == []
    assert coresys.plugins.dns.fallback is True

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


async def test_api_dns_logs(advanced_logs_tester):
    """Test dns logs."""
    await advanced_logs_tester("/dns", "hassio_dns", LogFormatter.VERBOSE)
