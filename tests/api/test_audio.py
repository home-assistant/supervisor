"""Test audio api."""

from aiohttp.test_utils import TestClient
import pytest


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
) -> None:
    """Test audio endpoints reject an unknown source with a client error."""
    api_client, prefix = api_client_with_prefix
    resp = await api_client.post(f"{prefix}{url}", json={})
    assert resp.status == 400
    body = await resp.json()
    assert body["message"] == "Invalid audio source bad, must be one of: input, output"
