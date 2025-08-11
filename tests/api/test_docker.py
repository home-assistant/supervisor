"""Test Docker API."""

from aiohttp.test_utils import TestClient
import pytest

from supervisor.coresys import CoreSys


@pytest.mark.asyncio
async def test_api_docker_info(api_client: TestClient):
    """Test docker info api."""
    resp = await api_client.get("/docker/info")
    result = await resp.json()

    assert result["data"]["logging"] == "journald"
    assert result["data"]["storage"] == "overlay2"
    assert result["data"]["version"] == "1.0.0"


async def test_api_network_enable_ipv6(coresys: CoreSys, api_client: TestClient):
    """Test setting docker network for enabled IPv6."""
    assert coresys.docker.config.enable_ipv6 is None

    resp = await api_client.post("/docker/options", json={"enable_ipv6": True})
    assert resp.status == 200

    assert coresys.docker.config.enable_ipv6 is True

    resp = await api_client.get("/docker/info")
    assert resp.status == 200
    body = await resp.json()
    assert body["data"]["enable_ipv6"] is True


async def test_api_network_mtu(coresys: CoreSys, api_client: TestClient):
    """Test setting docker network MTU."""
    assert coresys.docker.config.mtu is None

    resp = await api_client.post("/docker/options", json={"mtu": 1450})
    assert resp.status == 200

    assert coresys.docker.config.mtu == 1450

    resp = await api_client.get("/docker/info")
    assert resp.status == 200
    body = await resp.json()
    assert body["data"]["mtu"] == 1450

    # Test setting MTU to None
    resp = await api_client.post("/docker/options", json={"mtu": None})
    assert resp.status == 200

    assert coresys.docker.config.mtu is None

    resp = await api_client.get("/docker/info")
    assert resp.status == 200
    body = await resp.json()
    assert body["data"]["mtu"] is None


async def test_api_network_combined_options(coresys: CoreSys, api_client: TestClient):
    """Test setting both IPv6 and MTU together."""
    assert coresys.docker.config.enable_ipv6 is None
    assert coresys.docker.config.mtu is None

    resp = await api_client.post(
        "/docker/options", json={"enable_ipv6": True, "mtu": 1400}
    )
    assert resp.status == 200

    assert coresys.docker.config.enable_ipv6 is True
    assert coresys.docker.config.mtu == 1400

    resp = await api_client.get("/docker/info")
    assert resp.status == 200
    body = await resp.json()
    assert body["data"]["enable_ipv6"] is True
    assert body["data"]["mtu"] == 1400


async def test_registry_not_found(api_client: TestClient):
    """Test registry not found error."""
    resp = await api_client.delete("/docker/registries/bad")
    assert resp.status == 404
    body = await resp.json()
    assert body["message"] == "Hostname bad does not exist in registries"
