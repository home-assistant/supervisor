"""Test multicast api."""

from unittest.mock import AsyncMock, patch

from aiodocker.containers import DockerContainer
from aiohttp.test_utils import TestClient

from supervisor.docker.manager import DockerAPI
from supervisor.host.const import LogFormatter

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
