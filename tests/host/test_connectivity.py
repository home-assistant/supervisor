"""Test supported features."""
# pylint: disable=protected-access
from unittest.mock import patch

from supervisor.coresys import CoreSys
from supervisor.host.const import ConnectivityState


async def test_connectivity_unknown(coresys: CoreSys):
    """Test host unknown connectivity."""
    with patch("supervisor.utils.gdbus.DBus._send", return_value="[0]"):
        await coresys.host.network.check_connectivity()
        assert coresys.host.network.connectivity == ConnectivityState.UNKNOWN


async def test_connectivity_none(coresys: CoreSys):
    """Test host none connectivity."""
    with patch("supervisor.utils.gdbus.DBus._send", return_value="[1]"):
        await coresys.host.network.check_connectivity()
        assert coresys.host.network.connectivity == ConnectivityState.NONE


async def test_connectivity_portal(coresys: CoreSys):
    """Test host portal connectivity."""
    with patch("supervisor.utils.gdbus.DBus._send", return_value="[2]"):
        await coresys.host.network.check_connectivity()
        assert coresys.host.network.connectivity == ConnectivityState.PORTAL


async def test_connectivity_limited(coresys: CoreSys):
    """Test host limited connectivity."""
    with patch("supervisor.utils.gdbus.DBus._send", return_value="[3]"):
        await coresys.host.network.check_connectivity()
        assert coresys.host.network.connectivity == ConnectivityState.LIMITED


async def test_connectivity_full(coresys: CoreSys):
    """Test host full connectivity."""
    with patch("supervisor.utils.gdbus.DBus._send", return_value="[4]"):
        await coresys.host.network.check_connectivity()
        assert coresys.host.network.connectivity == ConnectivityState.FULL
