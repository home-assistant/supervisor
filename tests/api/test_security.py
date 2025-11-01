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
async def test_api_security_options_pwned(api_client, coresys: CoreSys):
    """Test security options pwned."""
    assert coresys.security.pwned

    await api_client.post("/security/options", json={"pwned": False})

    assert not coresys.security.pwned


@pytest.mark.asyncio
async def test_api_integrity_check(
    api_client, coresys: CoreSys, supervisor_internet: AsyncMock
):
    """Test security integrity check - now deprecated."""
    resp = await api_client.post("/security/integrity")

    # CodeNotary integrity check has been removed, should return 410 Gone
    assert resp.status == 410
