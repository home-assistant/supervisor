"""Test supported features."""
# pylint: disable=protected-access
from unittest.mock import patch

from supervisor.coresys import CoreSys


async def test_connectivity_not_connected(coresys: CoreSys):
    """Test host unknown connectivity."""
    with patch("supervisor.utils.gdbus.DBus._send", return_value="[0]"):
        await coresys.host.network.check_connectivity()
        assert not coresys.host.network.connectivity


async def test_connectivity_connected(coresys: CoreSys):
    """Test host full connectivity."""
    with patch("supervisor.utils.gdbus.DBus._send", return_value="[4]"):
        await coresys.host.network.check_connectivity()
        assert coresys.host.network.connectivity
