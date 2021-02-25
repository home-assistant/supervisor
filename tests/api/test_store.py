"""Test Store API."""
from aiohttp.test_utils import TestClient
import pytest

from supervisor.store.addon import AddonStore
from supervisor.store.repository import Repository


@pytest.mark.asyncio
async def test_api_store(
    api_client: TestClient, store_addon: AddonStore, repository: Repository
):
    """Test /store REST API."""
    resp = await api_client.get("/store")
    result = await resp.json()

    assert result["data"]["addons"][0]["slug"] == store_addon.slug
    assert result["data"]["repositories"][0]["slug"] == repository.slug


@pytest.mark.asyncio
async def test_api_store_addons(api_client: TestClient, store_addon: AddonStore):
    """Test /store/addons REST API."""
    print("test")
    resp = await api_client.get("/store/addons")
    result = await resp.json()
    print(result)

    assert result["data"][0]["slug"] == store_addon.slug


@pytest.mark.asyncio
async def test_api_store_addons_addon(api_client: TestClient, store_addon: AddonStore):
    """Test /store/addons/{addon} REST API."""
    resp = await api_client.get(f"/store/addons/{store_addon.slug}")
    result = await resp.json()
    assert result["data"]["slug"] == store_addon.slug


@pytest.mark.asyncio
async def test_api_store_addons_addon_version(
    api_client: TestClient, store_addon: AddonStore
):
    """Test /store/addons/{addon}/{version} REST API."""
    resp = await api_client.get(f"/store/addons/{store_addon.slug}/1.0.0")
    result = await resp.json()
    assert result["data"]["slug"] == store_addon.slug


@pytest.mark.asyncio
async def test_api_store_repositories(api_client: TestClient, repository: Repository):
    """Test /store/repositories REST API."""
    resp = await api_client.get("/store/repositories")
    result = await resp.json()

    assert result["data"][0]["slug"] == repository.slug


@pytest.mark.asyncio
async def test_api_store_repositories_repository(
    api_client: TestClient, repository: Repository
):
    """Test /store/repositories/{repository} REST API."""
    resp = await api_client.get(f"/store/repositories/{repository.slug}")
    result = await resp.json()

    assert result["data"]["slug"] == repository.slug
