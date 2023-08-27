"""Const for host."""
from enum import Enum

PARAM_BOOT_ID = "_BOOT_ID"
PARAM_FOLLOW = "follow"
PARAM_SYSLOG_IDENTIFIER = "SYSLOG_IDENTIFIER"


class InterfaceMethod(str, Enum):
    """Configuration of an interface."""

    DISABLED = "disabled"
    STATIC = "static"
    AUTO = "auto"


class InterfaceAddrGenMode(str, Enum):
    """Configuration of an interface."""

    EUI64 = "eui64"
    STABLE_PRIVACY = "stable-privacy"


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

    DISK = "disk"
    HAOS = "haos"
    HOSTNAME = "hostname"
    JOURNAL = "journal"
    MOUNT = "mount"
    NETWORK = "network"
    OS_AGENT = "os_agent"
    REBOOT = "reboot"
    RESOLVED = "resolved"
    SERVICES = "services"
    SHUTDOWN = "shutdown"
    TIMEDATE = "timedate"


class LogFormat(str, Enum):
    """Log format."""

    JOURNAL = "application/vnd.fdo.journal"
    JSON = "application/json"
    TEXT = "text/plain"
