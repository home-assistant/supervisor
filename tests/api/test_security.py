"""Test Supervisor API."""

from unittest.mock import AsyncMock

from aiohttp.test_utils import TestClient

from supervisor.coresys import CoreSys


async def test_api_security_options_force_security(
    api_client_with_prefix: tuple[TestClient, str], coresys: CoreSys
):
    """Test security options force security."""
    api_client, prefix = api_client_with_prefix
    assert not coresys.security.force

    await api_client.post(f"{prefix}/security/options", json={"force_security": True})

    assert coresys.security.force


async def test_api_security_options_pwned(
    api_client_with_prefix: tuple[TestClient, str], coresys: CoreSys
):
    """Test security options pwned."""
    api_client, prefix = api_client_with_prefix
    assert coresys.security.pwned

    await api_client.post(f"{prefix}/security/options", json={"pwned": False})

    assert not coresys.security.pwned


async def test_api_integrity_check(
    api_client_with_prefix: tuple[TestClient, str],
    coresys: CoreSys,
    supervisor_internet: AsyncMock,
):
    """Test security integrity check - now deprecated."""
    api_client, prefix = api_client_with_prefix
    resp = await api_client.post(f"{prefix}/security/integrity")

    # CodeNotary integrity check has been removed, should return 410 Gone
    assert resp.status == 410
