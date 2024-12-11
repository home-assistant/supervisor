"""Test Docker API."""

from aiohttp.test_utils import TestClient
import pytest


@pytest.mark.asyncio
async def test_api_docker_info(api_client: TestClient):
    """Test docker info api."""
    resp = await api_client.get("/docker/info")
    result = await resp.json()

    assert result["data"]["logging"] == "journald"
    assert result["data"]["storage"] == "overlay2"
    assert result["data"]["version"] == "1.0.0"


async def test_registry_not_found(api_client: TestClient):
    """Test registry not found error."""
    resp = await api_client.delete("/docker/registries/bad")
    assert resp.status == 404
    body = await resp.json()
    assert body["message"] == "Hostname bad does not exist in registries"
