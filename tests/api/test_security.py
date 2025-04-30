"""Test Supervisor API."""

from unittest.mock import AsyncMock

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


@pytest.mark.asyncio
async def test_api_integrity_check(
    api_client, coresys: CoreSys, supervisor_internet: AsyncMock
):
    """Test security integrity check."""
    coresys.security.content_trust = False

    resp = await api_client.post("/security/integrity")
    result = await resp.json()

    assert result["data"]["core"] == "untested"
    assert result["data"]["supervisor"] == "untested"
