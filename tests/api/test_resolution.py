"""Test Resolution API."""
import pytest

from supervisor.const import ATTR_UNSUPPORTED, UnsupportedReason


@pytest.mark.asyncio
async def test_api_resolution_base(coresys, api_client):
    """Test resolution manager api."""
    coresys.resolution.unsupported = UnsupportedReason.OS
    resp = await api_client.get("/resolution")
    result = await resp.json()
    assert UnsupportedReason.OS in result["data"][ATTR_UNSUPPORTED]
