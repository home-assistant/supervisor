"""Connection object for Network Manager."""

import logging
from typing import Any

from dbus_fast import Variant
from dbus_fast.aio.message_bus import MessageBus

from ...const import DBUS_NAME_NM
from ...interface import DBusInterface
from ...utils import dbus_connected
from ..configuration import (
    ConnectionProperties,
    EthernetProperties,
    Ip6Properties,
    IpAddress,
    IpProperties,
    MatchProperties,
    VlanProperties,
    WirelessProperties,
    WirelessSecurityProperties,
)

CONF_ATTR_CONNECTION = "connection"
CONF_ATTR_MATCH = "match"
CONF_ATTR_802_ETHERNET = "802-3-ethernet"
CONF_ATTR_802_WIRELESS = "802-11-wireless"
CONF_ATTR_802_WIRELESS_SECURITY = "802-11-wireless-security"
CONF_ATTR_VLAN = "vlan"
CONF_ATTR_IPV4 = "ipv4"
CONF_ATTR_IPV6 = "ipv6"

CONF_ATTR_CONNECTION_ID = "id"
CONF_ATTR_CONNECTION_UUID = "uuid"
CONF_ATTR_CONNECTION_TYPE = "type"
CONF_ATTR_CONNECTION_LLMNR = "llmnr"
CONF_ATTR_CONNECTION_MDNS = "mdns"
CONF_ATTR_CONNECTION_AUTOCONNECT = "autoconnect"
CONF_ATTR_CONNECTION_INTERFACE_NAME = "interface-name"

CONF_ATTR_MATCH_PATH = "path"

CONF_ATTR_VLAN_ID = "id"
CONF_ATTR_VLAN_PARENT = "parent"

CONF_ATTR_802_ETHERNET_ASSIGNED_MAC = "assigned-mac-address"

CONF_ATTR_802_WIRELESS_MODE = "mode"
CONF_ATTR_802_WIRELESS_ASSIGNED_MAC = "assigned-mac-address"
CONF_ATTR_802_WIRELESS_SSID = "ssid"
CONF_ATTR_802_WIRELESS_POWERSAVE = "powersave"
CONF_ATTR_802_WIRELESS_SECURITY_AUTH_ALG = "auth-alg"
CONF_ATTR_802_WIRELESS_SECURITY_KEY_MGMT = "key-mgmt"
CONF_ATTR_802_WIRELESS_SECURITY_PSK = "psk"

CONF_ATTR_IPV4_METHOD = "method"
CONF_ATTR_IPV4_ADDRESS_DATA = "address-data"
CONF_ATTR_IPV4_GATEWAY = "gateway"
CONF_ATTR_IPV4_DNS = "dns"

CONF_ATTR_IPV6_METHOD = "method"
CONF_ATTR_IPV6_ADDR_GEN_MODE = "addr-gen-mode"
CONF_ATTR_IPV6_PRIVACY = "ip6-privacy"
CONF_ATTR_IPV6_ADDRESS_DATA = "address-data"
CONF_ATTR_IPV6_GATEWAY = "gateway"
CONF_ATTR_IPV6_DNS = "dns"

IPV4_6_IGNORE_FIELDS = [
    "addresses",
    "address-data",
    "dns",
    "dns-data",
    "gateway",
    "method",
    "addr-gen-mode",
    "ip6-privacy",
]

_LOGGER: logging.Logger = logging.getLogger(__name__)


def _merge_settings_attribute(
    base_settings: dict[str, dict[str, Variant]],
    new_settings: dict[str, dict[str, Variant]],
    attribute: str,
    *,
    ignore_current_value: list[str] | None = None,
) -> None:
    """Merge settings attribute if present."""
    if attribute in new_settings:
        if attribute in base_settings:
            if ignore_current_value:
                for field in ignore_current_value:
                    base_settings[attribute].pop(field, None)

            base_settings[attribute].update(new_settings[attribute])
        else:
            base_settings[attribute] = new_settings[attribute]


class NetworkSetting(DBusInterface):
    """Network connection setting object for Network Manager.

    https://networkmanager.dev/docs/api/1.48.0/gdbus-org.freedesktop.NetworkManager.Settings.Connection.html
    """

    bus_name: str = DBUS_NAME_NM

    def __init__(self, object_path: str) -> None:
        """Initialize NetworkConnection object."""
        self._object_path: str = object_path

        self._connection: ConnectionProperties | None = None
        self._wireless: WirelessProperties | None = None
        self._wireless_security: WirelessSecurityProperties | None = None
        self._ethernet: EthernetProperties | None = None
        self._vlan: VlanProperties | None = None
        self._ipv4: IpProperties | None = None
        self._ipv6: Ip6Properties | None = None
        self._match: MatchProperties | None = None
        super().__init__()

    @property
    def object_path(self) -> str:
        """Object path for dbus object."""
        return self._object_path

    @property
    def connection(self) -> ConnectionProperties | None:
        """Return connection properties if any."""
        return self._connection

    @property
    def wireless(self) -> WirelessProperties | None:
        """Return wireless properties if any."""
        return self._wireless

    @property
    def wireless_security(self) -> WirelessSecurityProperties | None:
        """Return wireless security properties if any."""
        return self._wireless_security

    @property
    def ethernet(self) -> EthernetProperties | None:
        """Return Ethernet properties if any."""
        return self._ethernet

    @property
    def vlan(self) -> VlanProperties | None:
        """Return Vlan properties if any."""
        return self._vlan

    @property
    def ipv4(self) -> IpProperties | None:
        """Return ipv4 properties if any."""
        return self._ipv4

    @property
    def ipv6(self) -> Ip6Properties | None:
        """Return ipv6 properties if any."""
        return self._ipv6

    @property
    def match(self) -> MatchProperties | None:
        """Return match properties if any."""
        return self._match

    @dbus_connected
    async def get_settings(self) -> dict[str, Any]:
        """Return connection settings."""
        return await self.connected_dbus.Settings.Connection.call("get_settings")

    @dbus_connected
    async def update(self, settings: dict[str, dict[str, Variant]]) -> None:
        """Update connection settings."""
        new_settings: dict[
            str, dict[str, Variant]
        ] = await self.connected_dbus.Settings.Connection.call(
            "get_settings", unpack_variants=False
        )

        _merge_settings_attribute(
            new_settings,
            settings,
            CONF_ATTR_CONNECTION,
            ignore_current_value=[CONF_ATTR_CONNECTION_INTERFACE_NAME],
        )
        _merge_settings_attribute(new_settings, settings, CONF_ATTR_802_ETHERNET)
        _merge_settings_attribute(new_settings, settings, CONF_ATTR_802_WIRELESS)
        _merge_settings_attribute(
            new_settings, settings, CONF_ATTR_802_WIRELESS_SECURITY
        )
        _merge_settings_attribute(new_settings, settings, CONF_ATTR_VLAN)
        _merge_settings_attribute(
            new_settings,
            settings,
            CONF_ATTR_IPV4,
            ignore_current_value=IPV4_6_IGNORE_FIELDS,
        )
        _merge_settings_attribute(
            new_settings,
            settings,
            CONF_ATTR_IPV6,
            ignore_current_value=IPV4_6_IGNORE_FIELDS,
        )
        _merge_settings_attribute(new_settings, settings, CONF_ATTR_MATCH)

        await self.connected_dbus.Settings.Connection.call("update", new_settings)

    @dbus_connected
    async def delete(self) -> None:
        """Delete connection settings."""
        await self.connected_dbus.Settings.Connection.call("delete")

    async def connect(self, bus: MessageBus) -> None:
        """Get connection information."""
        await super().connect(bus)
        await self.reload()

        self.connected_dbus.Settings.Connection.on("updated", self.reload)

    @dbus_connected
    async def reload(self):
        """Get current settings for connection."""
        data = await self.get_settings()

        # Get configuration settings we care about
        # See: https://developer-old.gnome.org/NetworkManager/stable/ch01.html
        if CONF_ATTR_CONNECTION in data:
            self._connection = ConnectionProperties(
                id=data[CONF_ATTR_CONNECTION].get(CONF_ATTR_CONNECTION_ID),
                uuid=data[CONF_ATTR_CONNECTION].get(CONF_ATTR_CONNECTION_UUID),
                type=data[CONF_ATTR_CONNECTION].get(CONF_ATTR_CONNECTION_TYPE),
                interface_name=data[CONF_ATTR_CONNECTION].get(
                    CONF_ATTR_CONNECTION_INTERFACE_NAME
                ),
            )

        if CONF_ATTR_802_ETHERNET in data:
            self._ethernet = EthernetProperties(
                assigned_mac=data[CONF_ATTR_802_ETHERNET].get(
                    CONF_ATTR_802_ETHERNET_ASSIGNED_MAC
                ),
            )

        if CONF_ATTR_802_WIRELESS in data:
            self._wireless = WirelessProperties(
                ssid=bytes(
                    data[CONF_ATTR_802_WIRELESS].get(CONF_ATTR_802_WIRELESS_SSID, [])
                ).decode(),
                assigned_mac=data[CONF_ATTR_802_WIRELESS].get(
                    CONF_ATTR_802_WIRELESS_ASSIGNED_MAC
                ),
                mode=data[CONF_ATTR_802_WIRELESS].get(CONF_ATTR_802_WIRELESS_MODE),
                powersave=data[CONF_ATTR_802_WIRELESS].get(
                    CONF_ATTR_802_WIRELESS_POWERSAVE
                ),
            )

        if CONF_ATTR_802_WIRELESS_SECURITY in data:
            self._wireless_security = WirelessSecurityProperties(
                auth_alg=data[CONF_ATTR_802_WIRELESS_SECURITY].get(
                    CONF_ATTR_802_WIRELESS_SECURITY_AUTH_ALG
                ),
                key_mgmt=data[CONF_ATTR_802_WIRELESS_SECURITY].get(
                    CONF_ATTR_802_WIRELESS_SECURITY_KEY_MGMT
                ),
                psk=data[CONF_ATTR_802_WIRELESS_SECURITY].get(
                    CONF_ATTR_802_WIRELESS_SECURITY_PSK
                ),
            )

        if CONF_ATTR_VLAN in data:
            self._vlan = VlanProperties(
                id=data[CONF_ATTR_VLAN].get(CONF_ATTR_VLAN_ID),
                parent=data[CONF_ATTR_VLAN].get(CONF_ATTR_VLAN_PARENT),
            )

        if CONF_ATTR_IPV4 in data:
            address_data = None
            if ips := data[CONF_ATTR_IPV4].get(CONF_ATTR_IPV4_ADDRESS_DATA):
                address_data = [IpAddress(ip["address"], ip["prefix"]) for ip in ips]
            self._ipv4 = IpProperties(
                method=data[CONF_ATTR_IPV4].get(CONF_ATTR_IPV4_METHOD),
                address_data=address_data,
                gateway=data[CONF_ATTR_IPV4].get(CONF_ATTR_IPV4_GATEWAY),
                dns=data[CONF_ATTR_IPV4].get(CONF_ATTR_IPV4_DNS),
            )

        if CONF_ATTR_IPV6 in data:
            address_data = None
            if ips := data[CONF_ATTR_IPV6].get(CONF_ATTR_IPV6_ADDRESS_DATA):
                address_data = [IpAddress(ip["address"], ip["prefix"]) for ip in ips]
            self._ipv6 = Ip6Properties(
                method=data[CONF_ATTR_IPV6].get(CONF_ATTR_IPV6_METHOD),
                addr_gen_mode=data[CONF_ATTR_IPV6].get(CONF_ATTR_IPV6_ADDR_GEN_MODE),
                ip6_privacy=data[CONF_ATTR_IPV6].get(CONF_ATTR_IPV6_PRIVACY),
                address_data=address_data,
                gateway=data[CONF_ATTR_IPV6].get(CONF_ATTR_IPV6_GATEWAY),
                dns=data[CONF_ATTR_IPV6].get(CONF_ATTR_IPV6_DNS),
            )

        if CONF_ATTR_MATCH in data:
            self._match = MatchProperties(
                data[CONF_ATTR_MATCH].get(CONF_ATTR_MATCH_PATH)
            )
