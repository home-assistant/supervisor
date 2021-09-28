"""Test Home Assistant Add-ons."""

from supervisor.coresys import CoreSys

from ..const import TEST_ADDON_SLUG


def test_options_merge(coresys: CoreSys, install_addon_ssh) -> None:
    """Test options merge."""
    addon = coresys.addons.get(TEST_ADDON_SLUG)

    assert addon.options == {
        "apks": [],
        "authorized_keys": [],
        "password": "",
        "server": {"tcp_forwarding": False},
    }

    addon.options = {"password": "test"}

    assert addon.persist["options"] == {"password": "test"}
    assert addon.options == {
        "apks": [],
        "authorized_keys": [],
        "password": "test",
        "server": {"tcp_forwarding": False},
    }

    addon.options = {"password": "test", "server": {"tcp_forwarding": True}}
    assert addon.persist["options"] == {
        "password": "test",
        "server": {"tcp_forwarding": True},
    }
    assert addon.options == {
        "apks": [],
        "authorized_keys": [],
        "password": "test",
        "server": {"tcp_forwarding": True},
    }
