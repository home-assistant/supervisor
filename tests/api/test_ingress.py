"""Test ingress API."""
from unittest.mock import patch

import pytest

# pylint: disable=redefined-outer-name


@pytest.mark.asyncio
async def test_validate_session(api_client, coresys):
    """Test validating ingress session."""
    with patch("aiohttp.web_request.BaseRequest.__getitem__", return_value=None):
        resp = await api_client.post(
            "/ingress/validate_session",
            json={"session": "non-existing"},
        )
        assert resp.status == 401

    with patch(
        "aiohttp.web_request.BaseRequest.__getitem__",
        return_value=coresys.homeassistant,
    ):

        resp = await api_client.post("/ingress/session")
        result = await resp.json()

        assert "session" in result["data"]
        session = result["data"]["session"]
        assert session in coresys.ingress.sessions

        valid_time = coresys.ingress.sessions[session]

        resp = await api_client.post(
            "/ingress/validate_session",
            json={"session": session},
        )
        assert resp.status == 200
        assert await resp.json() == {"result": "ok", "data": {}}

        assert coresys.ingress.sessions[session] > valid_time
