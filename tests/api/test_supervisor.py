"""Test Supervisor API."""

import pytest

from supervisor.coresys import CoreSys


@pytest.mark.asyncio
async def test_api_supervisor_options_debug(api_client, coresys: CoreSys):
    """Test security options force security."""
    assert not coresys.config.debug

    await api_client.post("/supervisor/options", json={"debug": True})

    assert coresys.config.debug
