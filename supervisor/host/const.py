"""Const for host."""
from enum import Enum


class InterfaceMethod(str, Enum):
    """Configuration of an interface."""

    DISABLE = "disable"
    STATIC = "static"
    DHCP = "dhcp"


class InterfaceType(str, Enum):
    """Configuration of an interface."""

    ETHERNET = "ethernet"
    WIRELESS = "wireless"
    VLAN = "vlan"


class AuthMethod(str, Enum):
    """Authentication method."""

    NONE = "none"
    WEB = "web"
    WPA_PSK = "wpa-psk"


class WifiMode(str, Enum):
    """Wifi mode."""

    INFRASTRUCTURE = "infrastructure"
    MESH = "mesh"
    ADHOC = "adhoc"
    AP = "ap"
