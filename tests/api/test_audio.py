"""Test audio api."""

from unittest.mock import AsyncMock, patch

from aiodocker.containers import DockerContainer
from aiohttp.test_utils import TestClient
import pytest

from supervisor.docker.manager import DockerAPI
from supervisor.host.const import LogFormatter

from tests.common import load_json_fixture


async def test_api_audio_logs(advanced_logs_tester) -> None:
    """Test audio logs."""
    await advanced_logs_tester("/audio", "hassio_audio", LogFormatter.VERBOSE)


async def test_api_audio_stats(
    api_client_with_prefix: tuple[TestClient, str], container: DockerContainer
):
    """Test audio stats."""
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
            resp = await api_client.get(f"{prefix}/audio/stats")
    else:
        container.stats = AsyncMock(
            return_value=[load_json_fixture("container_stats.json")]
        )
        resp = await api_client.get(f"{prefix}/audio/stats")

    assert resp.status == 200
    result = await resp.json()
    if prefix == "/v2":
        assert "cpu_percent" not in result["data"]
    else:
        assert result["data"]["cpu_percent"] == 90.0
    assert result["data"]["memory_usage"] == 59700000


@pytest.mark.parametrize(
    "url",
    [
        pytest.param("/audio/volume/bad", id="volume"),
        pytest.param("/audio/volume/bad/application", id="volume-application"),
        pytest.param("/audio/mute/bad", id="mute"),
        pytest.param("/audio/mute/bad/application", id="mute-application"),
        pytest.param("/audio/default/bad", id="default"),
    ],
)
async def test_api_audio_invalid_source(
    api_client_with_prefix: tuple[TestClient, str], url: str
):
    """Test audio endpoints reject an unknown source with a client error."""
    api_client, prefix = api_client_with_prefix
    resp = await api_client.post(f"{prefix}{url}", json={})
    assert resp.status == 400
    body = await resp.json()
    assert body["message"] == "Invalid audio source bad, must be one of: input, output"
