"""Test Supervisor API."""

import pytest

from supervisor.coresys import CoreSys


@pytest.mark.asyncio
async def test_api_supervisor_options_force_security(api_client, coresys: CoreSys):
    """Test supervisor options force security."""
    assert not coresys.config.force_security

    await api_client.post("/supervisor/options", json={"force_security": True})

    assert coresys.config.force_security


@pytest.mark.asyncio
async def test_api_supervisor_options_content_trust(api_client, coresys: CoreSys):
    """Test supervisor options content trust."""
    assert coresys.config.content_trust

    await api_client.post("/supervisor/options", json={"content_trust": False})

    assert not coresys.config.content_trust
