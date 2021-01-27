"""Test Docker API."""
import pytest


@pytest.mark.asyncio
async def test_api_hardware_info(api_client):
    """Test docker info api."""
    resp = await api_client.get("/hardware/info")
    result = await resp.json()

    assert result["result"] == "ok"
