"""Const for host."""
from enum import Enum


class InterfaceMethod(str, Enum):
    """Configuration of an interface."""

    DISABLED = "disabled"
    STATIC = "static"
    AUTO = "auto"


class InterfaceType(str, Enum):
    """Configuration of an interface."""

    ETHERNET = "ethernet"
    WIRELESS = "wireless"
    VLAN = "vlan"


class AuthMethod(str, Enum):
    """Authentication method."""

    OPEN = "open"
    WEP = "wep"
    WPA_PSK = "wpa-psk"


class WifiMode(str, Enum):
    """Wifi mode."""

    INFRASTRUCTURE = "infrastructure"
    MESH = "mesh"
    ADHOC = "adhoc"
    AP = "ap"


class ConnectivityState(int, Enum):
    """Connectivity State."""

    UNKNOWN = 0
    NONE = 1
    PORTAL = 2
    LIMITED = 3
    FULL = 4
