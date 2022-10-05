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


async def test_load(coresys: CoreSys, journald_gateway: MagicMock):
    """Test load."""
    assert coresys.host.logs.boot_ids == []
    assert coresys.host.logs.identifiers == []
    assert coresys.host.logs.default_identifiers == []

    await coresys.host.logs.load()
    assert coresys.host.logs.boot_ids == TEST_BOOT_IDS

    # File is quite large so just check it loaded
    for identifier in ["kernel", "os-agent", "systemd"]:
        assert identifier in coresys.host.logs.default_identifiers

    # Mock is large so just look for a few different types of identifiers
    for identifier in [
        "addon_local_ssh",
        "hassio_dns",
        "hassio_supervisor",
        "kernel",
        "os-agent",
    ]:
        assert identifier in coresys.host.logs.identifiers

    # Boot ID query should not be run again, mock a failure for it to ensure
    journald_gateway.side_effect = [MagicMock(), TimeoutError()]
    await coresys.host.logs.update()
    assert coresys.host.logs.boot_ids == TEST_BOOT_IDS
