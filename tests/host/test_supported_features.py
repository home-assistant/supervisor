"""Test supported features."""
# pylint: disable=protected-access


def test_supported_features(coresys, dbus_is_connected):
    """Test host features."""
    assert "network" in coresys.host.features

    coresys._dbus.network.is_connected = False

    assert "network" in coresys.host.features

    coresys.host.supported_features.cache_clear()
    assert "network" not in coresys.host.features
