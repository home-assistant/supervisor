"""Test Supervisor API."""

import pytest

from supervisor.coresys import CoreSys


@pytest.mark.asyncio
async def test_api_security_options_force_security(api_client, coresys: CoreSys):
    """Test security options force security."""
    assert not coresys.security.force

    await api_client.post("/security/options", json={"force_security": True})

    assert coresys.security.force


@pytest.mark.asyncio
async def test_api_security_options_content_trust(api_client, coresys: CoreSys):
    """Test security options content trust."""
    assert coresys.security.content_trust

    await api_client.post("/security/options", json={"content_trust": False})

    assert not coresys.security.content_trust


@pytest.mark.asyncio
async def test_api_security_options_pwned(api_client, coresys: CoreSys):
    """Test security options pwned."""
    assert coresys.security.pwned

    await api_client.post("/security/options", json={"pwned": False})

    assert not coresys.security.pwned
