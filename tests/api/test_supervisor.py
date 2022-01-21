"""Test Supervisor API."""
# pylint: disable=protected-access
import pytest

from supervisor.api.const import ATTR_AVAILABLE_UPDATES
from supervisor.coresys import CoreSys

from tests.const import TEST_ADDON_SLUG


@pytest.mark.asyncio
async def test_api_supervisor_options_debug(api_client, coresys: CoreSys):
    """Test security options force security."""
    assert not coresys.config.debug

    await api_client.post("/supervisor/options", json={"debug": True})

    assert coresys.config.debug
