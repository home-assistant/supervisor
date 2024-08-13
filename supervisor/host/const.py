"""Const for host."""

from enum import StrEnum

PARAM_BOOT_ID = "_BOOT_ID"
PARAM_FOLLOW = "follow"
PARAM_SYSLOG_IDENTIFIER = "SYSLOG_IDENTIFIER"


class InterfaceMethod(StrEnum):
    """Configuration of an interface."""

    DISABLED = "disabled"
    STATIC = "static"
    AUTO = "auto"


class InterfaceType(StrEnum):
    """Configuration of an interface."""

    ETHERNET = "ethernet"
    WIRELESS = "wireless"
    VLAN = "vlan"


class AuthMethod(StrEnum):
    """Authentication method."""

    OPEN = "open"
    WEP = "wep"
    WPA_PSK = "wpa-psk"


class WifiMode(StrEnum):
    """Wifi mode."""

    INFRASTRUCTURE = "infrastructure"
    MESH = "mesh"
    ADHOC = "adhoc"
    AP = "ap"


class HostFeature(StrEnum):
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


class LogFormat(StrEnum):
    """Log format."""

    JOURNAL = "application/vnd.fdo.journal"
    JSON = "application/json"
    TEXT = "text/plain"


class LogFormatter(StrEnum):
    """Log formatter."""

    PLAIN = "plain"
    VERBOSE = "verbose"
