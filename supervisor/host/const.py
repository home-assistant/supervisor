"""Const for host."""

from enum import StrEnum

from awesomeversion import AwesomeVersion

PARAM_BOOT_ID = "_BOOT_ID"
PARAM_FOLLOW = "follow"
PARAM_SYSLOG_IDENTIFIER = "SYSLOG_IDENTIFIER"

# Writing NTP settings needs the timesyncd drop-in support of this OS Agent
# release. Older agents write /etc/systemd/timesyncd.conf and fail on the
# read-only /etc. HAOS 18.3.dev20260830 is the first build shipping it.
NTP_MIN_OS_AGENT_VERSION = AwesomeVersion("1.13.0")


class InterfaceMethod(StrEnum):
    """Configuration of an interface."""

    DISABLED = "disabled"
    STATIC = "static"
    AUTO = "auto"


class InterfaceAddrGenMode(StrEnum):
    """Configuration of an interface."""

    EUI64 = "eui64"
    STABLE_PRIVACY = "stable-privacy"
    DEFAULT_OR_EUI64 = "default-or-eui64"
    DEFAULT = "default"


class InterfaceIp6Privacy(StrEnum):
    """Configuration of an interface."""

    DEFAULT = "default"
    DISABLED = "disabled"
    ENABLED_PREFER_PUBLIC = "enabled-prefer-public"
    ENABLED = "enabled"


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
    NTP = "ntp"
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
    JSON_SEQ = "application/json-seq"
    TEXT = "text/plain"


class LogFormatter(StrEnum):
    """Log formatter."""

    PLAIN = "plain"
    VERBOSE = "verbose"


class MulticastDnsMode(StrEnum):
    """Multicast DNS (MDNS/LLMNR) mode."""

    DEFAULT = "default"
    OFF = "off"
    RESOLVE = "resolve"
    ANNOUNCE = "announce"
