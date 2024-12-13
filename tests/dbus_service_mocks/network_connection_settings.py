"""Mock of Network Manager Connection Settings service."""

from copy import deepcopy
from ipaddress import IPv4Address, IPv6Address
import socket

from dbus_fast import DBusError, Variant
from dbus_fast.service import PropertyAccess, dbus_property, signal

from .base import DBusServiceMock, dbus_method

BUS_NAME = "org.freedesktop.NetworkManager"
DEFAULT_OBJECT_PATH = "/org/freedesktop/NetworkManager/Settings/1"

# NetworkManager Connection settings skeleton which gets generated automatically
# Created with 1.42.4, using:
# nmcli con add type ethernet con-name "Test"
# busctl call org.freedesktop.NetworkManager /org/freedesktop/NetworkManager/Settings/5 org.freedesktop.NetworkManager.Settings.Connection GetSettings --json=pretty
# Note that "id" and "type" seem to be the bare minimum an update call, so they can be
# ommitted here.
MINIMAL_SETTINGS_FIXTURE = {
    "ipv4": {
        "address-data": Variant("aa{sv}", []),
        "addresses": Variant("aau", []),
        "dns-search": Variant("as", []),
        "method": Variant("s", "auto"),
        "route-data": Variant("aa{sv}", []),
        "routes": Variant("aau", []),
    },
    "ipv6": {
        "address-data": Variant("aa{sv}", []),
        "addresses": Variant("a(ayuay)", []),
        "dns-search": Variant("as", []),
        "method": Variant("s", "auto"),
        "route-data": Variant("aa{sv}", []),
        "routes": Variant("a(ayuayu)", []),
    },
    "proxy": {},
}

MINIMAL_ETHERNET_SETTINGS_FIXTURE = MINIMAL_SETTINGS_FIXTURE | {
    "connection": {
        "permissions": Variant("as", []),
        "uuid": Variant("s", "ee736ea0-e2cc-4cc5-9c35-d6df94a56b47"),
    },
    "802-3-ethernet": {
        "auto-negotiate": Variant("b", False),
        "mac-address-blacklist": Variant("as", []),
        "s390-options": Variant("a{ss}", {}),
    },
}

MINIMAL_WIRELESS_SETTINGS_FIXTURE = MINIMAL_SETTINGS_FIXTURE | {
    "connection": {
        "permissions": Variant("as", []),
        "uuid": Variant("s", "bf9f098a-23f5-41b0-873b-b449c58df499"),
    },
    "802-11-wireless": {
        "mac-address-blacklist": Variant("as", []),
        "seen-bssids": Variant("as", []),
        "ssid": Variant("ay", b"TestSSID"),
    },
}


def settings_update(minimal_setting, new_settings):
    """Update Connection settings with minimal skeleton in mind."""
    settings = deepcopy(minimal_setting)
    for k, v in new_settings.items():
        if k in settings:
            settings[k].update(v)
        else:
            settings[k] = v
    return settings


SETTINGS_1_FIXTURE: dict[str, dict[str, Variant]] = settings_update(
    MINIMAL_ETHERNET_SETTINGS_FIXTURE,
    {
        "connection": {
            "id": Variant("s", "Wired connection 1"),
            "interface-name": Variant("s", "eth0"),
            "llmnr": Variant("i", 2),
            "mdns": Variant("i", 2),
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
            "addresses": Variant("aau", [[2483202240, 24, 0]]),
            "dns": Variant("au", [16951488]),
            "dns-data": Variant("as", ["192.168.2.1"]),
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
            "method": Variant("s", "auto"),
            "dns": Variant("aay", [IPv6Address("2001:4860:4860::8888").packed]),
            "dns-data": Variant("as", ["2001:4860:4860::8888"]),
            "addr-gen-mode": Variant("i", 0),
        },
        "802-3-ethernet": {
            "assigned-mac-address": Variant("s", "preserve"),
        },
    },
)

SETTINGS_2_FIXTURE = settings_update(
    MINIMAL_ETHERNET_SETTINGS_FIXTURE,
    {
        "connection": {
            k: v
            for k, v in SETTINGS_1_FIXTURE["connection"].items()
            if k != "interface-name"
        },
        "ipv4": SETTINGS_1_FIXTURE["ipv4"],
        "ipv6": SETTINGS_1_FIXTURE["ipv6"],
        "802-3-ethernet": SETTINGS_1_FIXTURE["802-3-ethernet"],
        "match": {"path": Variant("as", ["platform-ff3f0000.ethernet"])},
    },
)

SETTINGS_3_FIXTURE = deepcopy(MINIMAL_WIRELESS_SETTINGS_FIXTURE)

SETINGS_FIXTURES: dict[str, dict[str, dict[str, Variant]]] = {
    "/org/freedesktop/NetworkManager/Settings/1": SETTINGS_1_FIXTURE,
    "/org/freedesktop/NetworkManager/Settings/2": SETTINGS_2_FIXTURE,
    "/org/freedesktop/NetworkManager/Settings/3": SETTINGS_3_FIXTURE,
}


def setup(object_path: str | None = None) -> DBusServiceMock:
    """Create dbus mock object."""
    return ConnectionSettings(object_path if object_path else DEFAULT_OBJECT_PATH)


class ConnectionSettings(DBusServiceMock):
    """Connection Settings mock.

    gdbus introspect --system --dest org.freedesktop.NetworkManager --object-path /org/freedesktop/NetworkManager/Settings/1
    """

    interface = "org.freedesktop.NetworkManager.Settings.Connection"

    def __init__(self, object_path: str):
        """Initialize object."""
        super().__init__()
        self.object_path = object_path
        self.settings = deepcopy(SETINGS_FIXTURES[object_path])

    @dbus_property(access=PropertyAccess.READ)
    def Unsaved(self) -> "b":
        """Get Unsaved."""
        return False

    @dbus_property(access=PropertyAccess.READ)
    def Flags(self) -> "u":
        """Get Flags."""
        return 0

    @dbus_property(access=PropertyAccess.READ)
    def Filename(self) -> "s":
        """Get Unsaved."""
        return "/etc/NetworkManager/system-connections/Supervisor eth0.nmconnection"

    @signal()
    def Updated(self) -> None:
        """Signal Updated."""

    @signal()
    def Removed(self) -> None:
        """Signal Removed."""

    @dbus_method()
    def Update(self, properties: "a{sa{sv}}") -> None:
        """Do Update method."""
        if "connection" not in properties:
            raise DBusError(
                "org.freedesktop.NetworkManager.Settings.Connection.MissingProperty",
                "connection.type: property is missing",
            )
        for required_prop in ("type", "id"):
            if required_prop not in properties["connection"]:
                raise DBusError(
                    "org.freedesktop.NetworkManager.Settings.Connection.MissingProperty",
                    f"connection.{required_prop}: property is missing",
                )
        if properties["connection"]["type"] == "802-11-wireless":
            self.settings = settings_update(
                MINIMAL_WIRELESS_SETTINGS_FIXTURE, properties
            )
        elif properties["connection"]["type"] == "802-3-ethernet":
            self.settings = settings_update(
                MINIMAL_ETHERNET_SETTINGS_FIXTURE, properties
            )
        else:
            self.settings = settings_update(MINIMAL_SETTINGS_FIXTURE, properties)
        # Post process addresses/address-data and dns/dns-data
        # If both "address" and "address-data" are provided the former wins
        # If both "dns" and "dns-data" are provided the former wins
        if "ipv4" in properties:
            ipv4 = properties["ipv4"]
            if "address-data" in ipv4:
                addresses = Variant("aau", [])
                for entry in ipv4["address-data"].value:
                    addresses.value.append(
                        [
                            socket.htonl(int(IPv4Address(entry["address"].value))),
                            entry["prefix"].value,
                            0,
                        ]
                    )
                self.settings["ipv4"]["addresses"] = addresses
            if "addresses" in ipv4:
                address_data = Variant("aa{sv}", [])
                for entry in ipv4["addresses"].value:
                    ipv4address = IPv4Address(socket.ntohl(entry[0]))
                    address_data.value.append(
                        {
                            "address": Variant("s", str(ipv4address)),
                            "prefix": Variant("u", int(entry[1])),
                        }
                    )
                self.settings["ipv4"]["address-data"] = address_data
            if "dns-data" in ipv4:
                dns = Variant("au", [])
                for entry in ipv4["dns-data"].value:
                    dns.value.append(socket.htonl(int(IPv4Address(entry))))
                self.settings["ipv4"]["dns"] = dns
            if "dns" in ipv4:
                dns_data = Variant("as", [])
                for entry in ipv4["dns"].value:
                    dns_data.value.append(str(IPv4Address(socket.ntohl(entry))))
                self.settings["ipv4"]["dns-data"] = dns_data
        self.Updated()

    @dbus_method()
    def UpdateUnsaved(self, properties: "a{sa{sv}}") -> None:
        """Do UpdateUnsaved method."""

    @dbus_method()
    def Delete(self) -> None:
        """Do Delete method."""
        self.Removed()

    @dbus_method()
    def GetSettings(self) -> "a{sa{sv}}":
        """Do GetSettings method."""
        return self.settings

    @dbus_method()
    def GetSecrets(self, setting_name: "s") -> "a{sa{sv}}":
        """Do GetSecrets method."""
        return self.GetSettings()

    @dbus_method()
    def ClearSecrets(self) -> None:
        """Do ClearSecrets method."""

    @dbus_method()
    def Save(self) -> None:
        """Do Save method."""
        self.Updated()

    @dbus_method()
    def Update2(self, settings: "a{sa{sv}}", flags: "u", args: "a{sv}") -> "a{sv}":
        """Do Update2 method."""
        self.Update(settings)
        return {}
