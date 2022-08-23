"""Test Network Manager Connection object."""
from typing import Any
from unittest.mock import patch

from dbus_next.signature import Variant

from supervisor.coresys import CoreSys
from supervisor.dbus.network.setting.generate import get_connection_from_interface
from supervisor.host.network import Interface

from tests.const import TEST_INTERFACE


async def mock_call_dbus_get_settings_signature(
    method: str, *args: list[Any], remove_signature: bool = True
) -> list[dict[str, Any]]:
    """Call dbus method mock for get settings that keeps signature."""
    if (
        method == "org.freedesktop.NetworkManager.Settings.Connection.GetSettings"
        and not remove_signature
    ):
        return [
            {
                "connection": {
                    "id": Variant("s", "Wired connection 1"),
                    "interface-name": Variant("s", "eth0"),
                    "permissions": Variant("as", []),
                    "timestamp": Variant("t", 1598125548),
                    "type": Variant("s", "802-3-ethernet"),
                    "uuid": Variant("s", "0c23631e-2118-355c-bbb0-8943229cb0d6"),
                },
                "ipv4": {
                    "address-data": Variant(
                        "aa{sv}",
                        [
                            {
                                "address": Variant("s", "192.168.2.148"),
                                "prefix": Variant("u", 24),
                            }
                        ],
                    ),
                    "addresses": Variant("aau", [[2483202240, 24, 16951488]]),
                    "dns": Variant("au", [16951488]),
                    "dns-search": Variant("as", []),
                    "gateway": Variant("s", "192.168.2.1"),
                    "method": Variant("s", "auto"),
                    "route-data": Variant(
                        "aa{sv}",
                        [
                            {
                                "dest": Variant("s", "192.168.122.0"),
                                "prefix": Variant("u", 24),
                                "next-hop": Variant("s", "10.10.10.1"),
                            }
                        ],
                    ),
                    "routes": Variant("aau", [[8038592, 24, 17435146, 0]]),
                },
                "ipv6": {
                    "address-data": Variant("aa{sv}", []),
                    "addresses": Variant("a(ayuay)", []),
                    "dns": Variant("au", []),
                    "dns-search": Variant("as", []),
                    "method": Variant("s", "auto"),
                    "route-data": Variant("aa{sv}", []),
                    "routes": Variant("aau", []),
                    "addr-gen-mode": Variant("i", 0),
                },
                "proxy": {},
                "802-3-ethernet": {
                    "auto-negotiate": Variant("b", False),
                    "mac-address-blacklist": Variant("as", []),
                    "s390-options": Variant("a{ss}", {}),
                },
                "802-11-wireless": {"ssid": Variant("ay", bytes([78, 69, 84, 84]))},
            }
        ]
    else:
        assert method == "org.freedesktop.NetworkManager.Settings.Connection.Update"
        assert len(args[0]) == 2
        assert args[0][0] == "a{sa{sv}}"
        settings = args[0][1]

        assert "connection" in settings
        assert settings["connection"]["id"] == Variant("s", "Supervisor eth0")
        assert settings["connection"]["interface-name"] == Variant("s", "eth0")
        assert settings["connection"]["uuid"] == Variant(
            "s", "0c23631e-2118-355c-bbb0-8943229cb0d6"
        )
        assert settings["connection"]["autoconnect"] == Variant("b", True)

        assert "ipv4" in settings
        assert settings["ipv4"]["method"] == Variant("s", "auto")
        assert "gateway" not in settings["ipv4"]
        assert "dns" not in settings["ipv4"]
        assert "address-data" not in settings["ipv4"]
        assert "addresses" not in settings["ipv4"]
        assert len(settings["ipv4"]["route-data"].value) == 1
        assert settings["ipv4"]["route-data"].value[0]["dest"] == Variant(
            "s", "192.168.122.0"
        )
        assert settings["ipv4"]["route-data"].value[0]["prefix"] == Variant("u", 24)
        assert settings["ipv4"]["route-data"].value[0]["next-hop"] == Variant(
            "s", "10.10.10.1"
        )
        assert settings["ipv4"]["routes"] == Variant(
            "aau", [[8038592, 24, 17435146, 0]]
        )

        assert "ipv6" in settings
        assert settings["ipv6"]["method"] == Variant("s", "auto")
        assert "gateway" not in settings["ipv6"]
        assert "dns" not in settings["ipv6"]
        assert "address-data" not in settings["ipv6"]
        assert "addresses" not in settings["ipv6"]
        assert settings["ipv6"]["addr-gen-mode"] == Variant("i", 0)

        assert "proxy" in settings

        assert "802-3-ethernet" in settings
        assert settings["802-3-ethernet"]["auto-negotiate"] == Variant("b", False)

        assert "802-11-wireless" in settings
        assert settings["802-11-wireless"]["ssid"] == Variant(
            "ay", bytes([78, 69, 84, 84])
        )
        assert "mode" not in settings["802-11-wireless"]
        assert "powersave" not in settings["802-11-wireless"]

        assert "802-11-wireless-security" not in settings
        assert "vlan" not in settings


async def test_update(coresys: CoreSys):
    """Test network manager update."""
    await coresys.dbus.network.interfaces[TEST_INTERFACE].connect()
    interface = Interface.from_dbus_interface(
        coresys.dbus.network.interfaces[TEST_INTERFACE]
    )
    conn = get_connection_from_interface(
        interface,
        name=coresys.dbus.network.interfaces[TEST_INTERFACE].settings.connection.id,
        uuid=coresys.dbus.network.interfaces[TEST_INTERFACE].settings.connection.uuid,
    )

    with patch.object(
        coresys.dbus.network.interfaces[TEST_INTERFACE].settings.dbus,
        "call_dbus",
        new=mock_call_dbus_get_settings_signature,
    ):
        await coresys.dbus.network.interfaces[TEST_INTERFACE].settings.update(conn)
