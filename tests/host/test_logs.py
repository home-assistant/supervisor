"""Test host logs control."""

from unittest.mock import MagicMock

import pytest

from supervisor.coresys import CoreSys
from supervisor.exceptions import HostLogError

TEST_BOOT_IDS = [
    "b2aca10d5ca54fb1b6fb35c85a0efca9",
    "b1c386a144fd44db8f855d7e907256f8",
]


async def test_available(coresys: CoreSys, journald_gateway: MagicMock):
    """Test available as long as socket is regardless of boot IDs."""
    journald_gateway.side_effect = TimeoutError()
    with pytest.raises(HostLogError):
        await coresys.host.logs.update()

    assert coresys.host.logs.boot_ids == []
    assert coresys.host.logs.available is True


async def test_get_boot_ids(coresys: CoreSys, journald_gateway: MagicMock):
    """Test getting boot IDs."""
    assert coresys.host.logs.boot_ids == []

    await coresys.host.logs.update()
    assert coresys.host.logs.boot_ids == TEST_BOOT_IDS

    # Calls would fail at this point but update should not try to query again
    journald_gateway.side_effect = TimeoutError()
    await coresys.host.logs.update()
    assert coresys.host.logs.boot_ids == TEST_BOOT_IDS
