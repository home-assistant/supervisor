"""Test services API."""

from aiohttp.test_utils import TestClient
import pytest


@pytest.mark.parametrize(
    ("method", "url"),
    [("get", "/services/bad"), ("post", "/services/bad"), ("delete", "/services/bad")],
)
async def test_service_not_found(api_client: TestClient, method: str, url: str):
    """Test service not found error."""
    resp = await api_client.request(method, url)
    assert resp.status == 404
    body = await resp.json()
    assert body["message"] == "Service does not exist"
