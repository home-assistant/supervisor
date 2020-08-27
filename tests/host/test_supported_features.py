"""Test supported features."""
# pylint: disable=protected-access


def test_supported_features(coresys):
    """Test host features."""
    assert "network" in coresys.host.supported_features

    coresys._dbus.network.is_connected = False

    assert "network" not in coresys.host.supported_features
