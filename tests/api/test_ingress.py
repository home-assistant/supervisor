"""Test ingress API."""
from unittest.mock import patch

import pytest


@pytest.fixture
def stub_auth():
    """Bypass auth check."""
    with patch("supervisor.api.ingress.APIIngress._check_ha_access") as mock_auth:
        yield mock_auth


@pytest.mark.asyncio
async def test_validate_session(stub_auth, api_client, coresys):
    """Test validating ingress session."""
    coresys.core.sys_homeassistant.supervisor_token = "ABCD"
    resp = await api_client.post(
        "/ingress/validate_session",
        json={"session": "non-existing"},
    )
    assert resp.status == 401
    assert len(stub_auth.mock_calls) == 1

    resp = await api_client.post("/ingress/session")
    result = await resp.json()
    assert len(stub_auth.mock_calls) == 2

    assert "session" in result["data"]
    session = result["data"]["session"]
    assert session in coresys.ingress.sessions

    valid_time = coresys.ingress.sessions[session]

    resp = await api_client.post(
        "/ingress/validate_session",
        json={"session": session},
    )
    assert resp.status == 200
    assert len(stub_auth.mock_calls) == 3
    assert await resp.json() == {"result": "ok", "data": {}}

    assert coresys.ingress.sessions[session] > valid_time
