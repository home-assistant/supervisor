"""Test services API."""

from aiohttp.test_utils import TestClient
import pytest


@pytest.mark.parametrize(
    ("method", "url"),
    [("get", "/jobs/bad"), ("delete", "/jobs/bad")],
)
async def test_job_not_found(api_client: TestClient, method: str, url: str):
    """Test job not found error."""
    resp = await api_client.request(method, url)
    assert resp.status == 404
    resp = await resp.json()
    assert resp["message"] == "Job does not exist"
