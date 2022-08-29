"""Constants for DBUS."""
from enum import Enum, IntEnum
from socket import AF_INET, AF_INET6

DBUS_NAME_HAOS = "io.hass.os"
DBUS_NAME_HOSTNAME = "org.freedesktop.hostname1"
DBUS_NAME_LOGIND = "org.freedesktop.login1"
DBUS_NAME_NM = "org.freedesktop.NetworkManager"
DBUS_NAME_RAUC = "de.pengutronix.rauc"
DBUS_NAME_RESOLVED = "org.freedesktop.resolve1"
DBUS_NAME_SYSTEMD = "org.freedesktop.systemd1"
DBUS_NAME_TIMEDATE = "org.freedesktop.timedate1"

DBUS_IFACE_ACCESSPOINT = "org.freedesktop.NetworkManager.AccessPoint"
DBUS_IFACE_CONNECTION_ACTIVE = "org.freedesktop.NetworkManager.Connection.Active"
DBUS_IFACE_DEVICE = "org.freedesktop.NetworkManager.Device"
DBUS_IFACE_DEVICE_WIRELESS = "org.freedesktop.NetworkManager.Device.Wireless"
DBUS_IFACE_DNS = "org.freedesktop.NetworkManager.DnsManager"
DBUS_IFACE_HAOS = "io.hass.os"
DBUS_IFACE_HAOS_APPARMOR = "io.hass.os.AppArmor"
DBUS_IFACE_HAOS_CGROUP = "io.hass.os.CGroup"
DBUS_IFACE_HAOS_DATADISK = "io.hass.os.DataDisk"
DBUS_IFACE_HAOS_SYSTEM = "io.hass.os.System"
DBUS_IFACE_HOSTNAME = "org.freedesktop.hostname1"
DBUS_IFACE_IP4CONFIG = "org.freedesktop.NetworkManager.IP4Config"
DBUS_IFACE_IP6CONFIG = "org.freedesktop.NetworkManager.IP6Config"
DBUS_IFACE_NM = "org.freedesktop.NetworkManager"
DBUS_IFACE_RAUC_INSTALLER = "de.pengutronix.rauc.Installer"
DBUS_IFACE_RESOLVED_MANAGER = "org.freedesktop.resolve1.Manager"
DBUS_IFACE_SETTINGS_CONNECTION = "org.freedesktop.NetworkManager.Settings.Connection"
DBUS_IFACE_SYSTEMD_MANAGER = "org.freedesktop.systemd1.Manager"
DBUS_IFACE_TIMEDATE = "org.freedesktop.timedate1"

DBUS_SIGNAL_NM_CONNECTION_ACTIVE_CHANGED = (
    "org.freedesktop.NetworkManager.Connection.Active.StateChanged"
)
DBUS_SIGNAL_RAUC_INSTALLER_COMPLETED = "de.pengutronix.rauc.Installer.Completed"

DBUS_OBJECT_BASE = "/"
DBUS_OBJECT_DNS = "/org/freedesktop/NetworkManager/DnsManager"
DBUS_OBJECT_HAOS = "/io/hass/os"
DBUS_OBJECT_HAOS_APPARMOR = "/io/hass/os/AppArmor"
DBUS_OBJECT_HAOS_CGROUP = "/io/hass/os/CGroup"
DBUS_OBJECT_HAOS_DATADISK = "/io/hass/os/DataDisk"
DBUS_OBJECT_HAOS_SYSTEM = "/io/hass/os/System"
DBUS_OBJECT_HOSTNAME = "/org/freedesktop/hostname1"
DBUS_OBJECT_LOGIND = "/org/freedesktop/login1"
DBUS_OBJECT_NM = "/org/freedesktop/NetworkManager"
DBUS_OBJECT_RESOLVED = "/org/freedesktop/resolve1"
DBUS_OBJECT_SETTINGS = "/org/freedesktop/NetworkManager/Settings"
DBUS_OBJECT_SYSTEMD = "/org/freedesktop/systemd1"
DBUS_OBJECT_TIMEDATE = "/org/freedesktop/timedate1"

DBUS_ATTR_ACTIVE_ACCESSPOINT = "ActiveAccessPoint"
DBUS_ATTR_ACTIVE_CONNECTION = "ActiveConnection"
DBUS_ATTR_ACTIVE_CONNECTIONS = "ActiveConnections"
DBUS_ATTR_ADDRESS_DATA = "AddressData"
DBUS_ATTR_BOOT_SLOT = "BootSlot"
DBUS_ATTR_CACHE_STATISTICS = "CacheStatistics"
DBUS_ATTR_CHASSIS = "Chassis"
DBUS_ATTR_COMPATIBLE = "Compatible"
DBUS_ATTR_CONFIGURATION = "Configuration"
DBUS_ATTR_CONNECTION = "Connection"
DBUS_ATTR_CONNECTION_ENABLED = "ConnectivityCheckEnabled"
DBUS_ATTR_CURRENT_DEVICE = "CurrentDevice"
DBUS_ATTR_CURRENT_DNS_SERVER = "CurrentDNSServer"
DBUS_ATTR_CURRENT_DNS_SERVER_EX = "CurrentDNSServerEx"
DBUS_ATTR_DEFAULT = "Default"
DBUS_ATTR_DEPLOYMENT = "Deployment"
DBUS_ATTR_DEVICE_INTERFACE = "Interface"
DBUS_ATTR_DEVICE_TYPE = "DeviceType"
DBUS_ATTR_DEVICES = "Devices"
DBUS_ATTR_DIAGNOSTICS = "Diagnostics"
DBUS_ATTR_DNS = "DNS"
DBUS_ATTR_DNS_EX = "DNSEx"
DBUS_ATTR_DNS_OVER_TLS = "DNSOverTLS"
DBUS_ATTR_DNS_STUB_LISTENER = "DNSStubListener"
DBUS_ATTR_DNSSEC = "DNSSEC"
DBUS_ATTR_DNSSEC_NEGATIVE_TRUST_ANCHORS = "DNSSECNegativeTrustAnchors"
DBUS_ATTR_DNSSEC_STATISTICS = "DNSSECStatistics"
DBUS_ATTR_DNSSEC_SUPPORTED = "DNSSECSupported"
DBUS_ATTR_DOMAINS = "Domains"
DBUS_ATTR_DRIVER = "Driver"
DBUS_ATTR_FALLBACK_DNS = "FallbackDNS"
DBUS_ATTR_FALLBACK_DNS_EX = "FallbackDNSEx"
DBUS_ATTR_FINISH_TIMESTAMP = "FinishTimestamp"
DBUS_ATTR_FIRMWARE_TIMESTAMP_MONOTONIC = "FirmwareTimestampMonotonic"
DBUS_ATTR_FREQUENCY = "Frequency"
DBUS_ATTR_GATEWAY = "Gateway"
DBUS_ATTR_HWADDRESS = "HwAddress"
DBUS_ATTR_ID = "Id"
DBUS_ATTR_IP4CONFIG = "Ip4Config"
DBUS_ATTR_IP6CONFIG = "Ip6Config"
DBUS_ATTR_KERNEL_RELEASE = "KernelRelease"
DBUS_ATTR_KERNEL_TIMESTAMP_MONOTONIC = "KernelTimestampMonotonic"
DBUS_ATTR_LAST_ERROR = "LastError"
DBUS_ATTR_LLMNR = "LLMNR"
DBUS_ATTR_LLMNR_HOSTNAME = "LLMNRHostname"
DBUS_ATTR_LOADER_TIMESTAMP_MONOTONIC = "LoaderTimestampMonotonic"
DBUS_ATTR_MANAGED = "Managed"
DBUS_ATTR_MODE = "Mode"
DBUS_ATTR_MULTICAST_DNS = "MulticastDNS"
DBUS_ATTR_NAMESERVER_DATA = "NameserverData"
DBUS_ATTR_NAMESERVERS = "Nameservers"
DBUS_ATTR_NTP = "NTP"
DBUS_ATTR_NTPSYNCHRONIZED = "NTPSynchronized"
DBUS_ATTR_OPERATING_SYSTEM_PRETTY_NAME = "OperatingSystemPrettyName"
DBUS_ATTR_OPERATION = "Operation"
DBUS_ATTR_PARSER_VERSION = "ParserVersion"
DBUS_ATTR_PRIMARY_CONNECTION = "PrimaryConnection"
DBUS_ATTR_RESOLV_CONF_MODE = "ResolvConfMode"
DBUS_ATTR_RCMANAGER = "RcManager"
DBUS_ATTR_SSID = "Ssid"
DBUS_ATTR_STATE = "State"
DBUS_ATTR_STATE_FLAGS = "StateFlags"
DBUS_ATTR_STATIC_HOSTNAME = "StaticHostname"
DBUS_ATTR_STATIC_OPERATING_SYSTEM_CPE_NAME = "OperatingSystemCPEName"
DBUS_ATTR_STRENGTH = "Strength"
DBUS_ATTR_TIMEUSEC = "TimeUSec"
DBUS_ATTR_TIMEZONE = "Timezone"
DBUS_ATTR_TRANSACTION_STATISTICS = "TransactionStatistics"
DBUS_ATTR_TYPE = "Type"
DBUS_ATTR_USERSPACE_TIMESTAMP_MONOTONIC = "UserspaceTimestampMonotonic"
DBUS_ATTR_UUID = "Uuid"
DBUS_ATTR_VARIANT = "Variant"
DBUS_ATTR_VERSION = "Version"


class RaucState(str, Enum):
    """Rauc slot states."""

    GOOD = "good"
    BAD = "bad"
    ACTIVE = "active"


class InterfaceMethod(str, Enum):
    """Interface method simple."""

    AUTO = "auto"
    MANUAL = "manual"
    DISABLED = "disabled"
    LINK_LOCAL = "link-local"


class ConnectionType(str, Enum):
    """Connection type."""

    ETHERNET = "802-3-ethernet"
    WIRELESS = "802-11-wireless"


class ConnectionStateType(int, Enum):
    """Connection states.

    https://developer.gnome.org/NetworkManager/stable/nm-dbus-types.html#NMActiveConnectionState
    """

    UNKNOWN = 0
    ACTIVATING = 1
    ACTIVATED = 2
    DEACTIVATING = 3
    DEACTIVATED = 4


class ConnectionStateFlags(int, Enum):
    """Connection state flags.

    https://developer-old.gnome.org/NetworkManager/stable/nm-dbus-types.html#NMActivationStateFlags
    """

    NONE = 0
    IS_MASTER = 0x1
    IS_SLAVE = 0x2
    LAYER2_READY = 0x4
    IP4_READY = 0x8
    IP6_READY = 0x10
    MASTER_HAS_SLAVES = 0x20
    LIFETIME_BOUND_TO_PROFILE_VISIBILITY = 0x40
    EXTERNAL = 0x80


class ConnectivityState(int, Enum):
    """Network connectvity.

    https://developer.gnome.org/NetworkManager/unstable/nm-dbus-types.html#NMConnectivityState
    """

    CONNECTIVITY_UNKNOWN = 0
    CONNECTIVITY_NONE = 1
    CONNECTIVITY_PORTAL = 2
    CONNECTIVITY_LIMITED = 3
    CONNECTIVITY_FULL = 4


class DeviceType(int, Enum):
    """Device types.

    https://developer.gnome.org/NetworkManager/stable/nm-dbus-types.html#NMDeviceType
    """

    UNKNOWN = 0
    ETHERNET = 1
    WIRELESS = 2
    BLUETOOTH = 5
    VLAN = 11
    TUN = 16
    VETH = 20


class WirelessMethodType(int, Enum):
    """Device Type."""

    UNKNOWN = 0
    ADHOC = 1
    INFRASTRUCTURE = 2
    ACCESSPOINT = 3
    MESH = 4


class DNSAddressFamily(IntEnum):
    """Address family for DNS server."""

    INET = AF_INET
    INET6 = AF_INET6


class MulticastProtocolEnabled(str, Enum):
    """Multicast protocol enabled or resolve."""

    YES = "yes"
    NO = "no"
    RESOLVE = "resolve"


class DNSOverTLSEnabled(str, Enum):
    """DNS over TLS enabled."""

    YES = "yes"
    NO = "no"
    OPPORTUNISTIC = "opportunistic"


class DNSSECValidation(str, Enum):
    """DNSSEC validation enforced."""

    YES = "yes"
    NO = "no"
    ALLOW_DOWNGRADE = "allow-downgrade"


class DNSStubListenerEnabled(str, Enum):
    """DNS stub listener enabled."""

    YES = "yes"
    NO = "no"
    TCP_ONLY = "tcp"
    UDP_ONLY = "udp"


class ResolvConfMode(str, Enum):
    """Resolv.conf management mode."""

    FOREIGN = "foreign"
    MISSING = "missing"
    STATIC = "static"
    STUB = "stub"
    UPLINK = "uplink"
