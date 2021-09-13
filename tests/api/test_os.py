"""Test OS API."""
import pytest


@pytest.mark.asyncio
async def test_api_os_info(api_client):
    """Test docker info api."""
    resp = await api_client.get("/os/info")
    result = await resp.json()

    for attr in (
        "version",
        "version_latest",
        "update_available",
        "board",
        "boot",
        "disk_data",
    ):
        assert attr in result["data"]
