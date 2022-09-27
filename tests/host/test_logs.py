"""Test host logs control."""

from unittest.mock import AsyncMock, patch

import pytest

from supervisor.coresys import CoreSys
from supervisor.exceptions import HostLogError

from tests.common import load_fixture

TEST_BOOT_IDS = [
    "b2aca10d5ca54fb1b6fb35c85a0efca9",
    "b1c386a144fd44db8f855d7e907256f8",
]


async def test_available(coresys: CoreSys):
    """Test available as long as socket is regardless of boot IDs."""
    assert coresys.host.logs.available is False

    with patch("supervisor.host.logs.Path.is_socket", return_value=True), patch(
        "supervisor.host.logs.ClientSession.get", side_effect=TimeoutError()
    ):
        with pytest.raises(HostLogError):
            await coresys.host.logs.update()

        assert coresys.host.logs.boot_ids == []
        assert coresys.host.logs.available is True


async def test_get_boot_ids(coresys: CoreSys):
    """Test getting boot IDs."""
    assert coresys.host.logs.boot_ids == []

    with patch("supervisor.host.logs.Path.is_socket", return_value=True), patch(
        "supervisor.host.logs.ClientSession.get"
    ) as get:
        get.return_value.__aenter__.return_value.text = AsyncMock(
            side_effect=[load_fixture("boot_ids_logs.txt")]
        )
        await coresys.host.logs.update()

        assert coresys.host.logs.boot_ids == TEST_BOOT_IDS

    # Calls would fail at this point but update should not try to query again
    await coresys.host.logs.update()
    assert coresys.host.logs.boot_ids == TEST_BOOT_IDS
