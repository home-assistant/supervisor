"""Test supported features."""

# pylint: disable=protected-access
from unittest.mock import patch

import pytest

from supervisor.coresys import CoreSys

from tests.common import load_binary_fixture


@pytest.mark.usefixtures("dbus_is_connected")
def test_supported_features(coresys: CoreSys):
    """Test host features."""
    assert "network" in coresys.host.features

    coresys._dbus.network.is_connected = False

    assert "network" in coresys.host.features

    coresys.host.supported_features.cache_clear()
    assert "network" not in coresys.host.features


async def test_supported_features_nvme(coresys: CoreSys):
    """Test nvme supported feature."""
    with patch(
        "supervisor.host.nvme.manager.asyncio.create_subprocess_shell"
    ) as shell_mock:
        shell_mock.return_value.returncode = 0
        shell_mock.return_value.communicate.return_value = (b'{"Devices":[]}', b"")
        await coresys.host.nvme.load()

        assert "nvme" not in coresys.host.features

        shell_mock.return_value.communicate.return_value = (
            load_binary_fixture("nvme-list.json"),
            b"",
        )
        await coresys.host.nvme.update()
        coresys.host.supported_features.cache_clear()

        assert "nvme" in coresys.host.features
