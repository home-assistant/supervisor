"""Test multicast api."""

from unittest.mock import AsyncMock, PropertyMock, patch

from aiodocker.containers import DockerContainer
from aiohttp.test_utils import TestClient
from awesomeversion import AwesomeVersion

from supervisor.coresys import CoreSys
from supervisor.docker.manager import DockerAPI
from supervisor.host.const import LogFormatter
from supervisor.plugins.multicast import PluginMulticast

from tests.common import load_json_fixture


async def test_api_multicast_logs(advanced_logs_tester):
    """Test multicast logs."""
    await advanced_logs_tester("/multicast", "hassio_multicast", LogFormatter.VERBOSE)


async def test_api_multicast_stats(
    api_client_with_prefix: tuple[TestClient, str], container: DockerContainer
):
    """Test multicast stats."""
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
            resp = await api_client.get(f"{prefix}/multicast/stats")
    else:
        container.stats = AsyncMock(
            return_value=[load_json_fixture("container_stats.json")]
        )
        resp = await api_client.get(f"{prefix}/multicast/stats")

    assert resp.status == 200
    result = await resp.json()
    if prefix == "/v2":
        assert "cpu_percent" not in result["data"]
    else:
        assert result["data"]["cpu_percent"] == 90.0
    assert result["data"]["memory_usage"] == 59700000


async def test_api_multicast_info(
    api_client_with_prefix: tuple[TestClient, str], coresys: CoreSys
):
    """Test multicast info reports the enabled state."""
    api_client, prefix = api_client_with_prefix

    resp = await api_client.get(f"{prefix}/multicast/info")
    assert resp.status == 200
    result = await resp.json()
    assert result["data"]["enabled"] is True

    coresys.plugins.multicast._data["enabled"] = False  # pylint: disable=protected-access
    resp = await api_client.get(f"{prefix}/multicast/info")
    result = await resp.json()
    assert result["data"]["enabled"] is False
    assert result["data"]["update_available"] is False


async def test_api_multicast_options(
    api_client_with_prefix: tuple[TestClient, str], coresys: CoreSys
):
    """Test multicast options enable and disable the plugin."""
    api_client, prefix = api_client_with_prefix

    with (
        patch.object(PluginMulticast, "disable") as disable,
        patch.object(PluginMulticast, "enable") as enable,
    ):
        resp = await api_client.post(
            f"{prefix}/multicast/options", json={"enabled": False}
        )
        assert resp.status == 200
        disable.assert_called_once()
        enable.assert_not_called()

        disable.reset_mock()
        resp = await api_client.post(
            f"{prefix}/multicast/options", json={"enabled": True}
        )
        assert resp.status == 200
        enable.assert_called_once()
        disable.assert_not_called()


async def test_api_multicast_disabled_actions(
    api_client_with_prefix: tuple[TestClient, str], coresys: CoreSys
):
    """Test restart and update are rejected while the plugin is disabled."""
    api_client, prefix = api_client_with_prefix
    coresys.plugins.multicast._data["enabled"] = False  # pylint: disable=protected-access

    resp = await api_client.post(f"{prefix}/multicast/restart")
    assert resp.status == 400
    result = await resp.json()
    assert result["message"] == "Multicast plugin is disabled"

    with patch.object(
        PluginMulticast,
        "latest_version",
        new=PropertyMock(return_value=AwesomeVersion("2024.01.0")),
    ):
        resp = await api_client.post(f"{prefix}/multicast/update")
    assert resp.status == 400
