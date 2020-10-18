"""Test Docker API."""
import pytest


@pytest.mark.asyncio
async def test_api_docker_info(api_client):
    """Test docker info api."""
    resp = await api_client.get("/docker/info")
    result = await resp.json()

    assert result["data"]["logging"] == "journald"
    assert result["data"]["storage"] == "overlay2"
    assert result["data"]["version"] == "1.0.0"
