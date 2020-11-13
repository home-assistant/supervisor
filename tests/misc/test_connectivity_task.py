"""Test periodic connectivity task."""
# pylint: disable=protected-access,import-error
from unittest.mock import AsyncMock

from supervisor.coresys import CoreSys


async def test_no_connectivity(coresys: CoreSys):
    """Test periodic connectivity task."""
    coresys.host.network.check_connectivity = AsyncMock()
    coresys.supervisor.check_connectivity = AsyncMock()

    coresys.tasks._cache["connectivity"] = 0
    coresys.host.network._connectivity = False
    coresys.supervisor._connectivity = False

    await coresys.tasks._check_connectivity()

    coresys.host.network.check_connectivity.assert_called_once()
    coresys.supervisor.check_connectivity.assert_called_once()
    assert coresys.tasks._cache["connectivity"] == 0
    coresys.host.network.check_connectivity.reset_mock()
    coresys.supervisor.check_connectivity.reset_mock()

    await coresys.tasks._check_connectivity()

    coresys.host.network.check_connectivity.assert_called_once()
    coresys.supervisor.check_connectivity.assert_called_once()
    assert coresys.tasks._cache["connectivity"] == 0


async def test_connectivity(coresys: CoreSys):
    """Test periodic connectivity task."""
    coresys.host.network.check_connectivity = AsyncMock()
    coresys.supervisor.check_connectivity = AsyncMock()

    coresys.tasks._cache["connectivity"] = 0
    coresys.host.network._connectivity = True
    coresys.supervisor._connectivity = True

    await coresys.tasks._check_connectivity()

    coresys.host.network.check_connectivity.assert_not_called()
    coresys.supervisor.check_connectivity.assert_not_called()
    assert coresys.tasks._cache["connectivity"] == 30


async def test_connectivity_cache_reached(coresys: CoreSys):
    """Test periodic connectivity task."""
    coresys.host.network.check_connectivity = AsyncMock()
    coresys.supervisor.check_connectivity = AsyncMock()

    coresys.tasks._cache["connectivity"] = 600
    coresys.host.network._connectivity = True
    coresys.supervisor._connectivity = True

    await coresys.tasks._check_connectivity()

    coresys.host.network.check_connectivity.assert_called_once()
    coresys.supervisor.check_connectivity.assert_called_once()
    assert coresys.tasks._cache["connectivity"] == 0
