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


class HostFeature(str, Enum):
    """Host feature."""

    HAOS = "haos"
    HOSTNAME = "hostname"
    NETWORK = "network"
    REBOOT = "reboot"
    SERVICES = "services"
    SHUTDOWN = "shutdown"
    AGENT = "agent"
