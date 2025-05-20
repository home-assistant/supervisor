"""Constants for DBUS."""

from enum import IntEnum, StrEnum
from socket import AF_INET, AF_INET6

DBUS_NAME_HAOS = "io.hass.os"
DBUS_NAME_HOSTNAME = "org.freedesktop.hostname1"
DBUS_NAME_LOGIND = "org.freedesktop.login1"
DBUS_NAME_NM = "org.freedesktop.NetworkManager"
DBUS_NAME_RAUC = "de.pengutronix.rauc"
DBUS_NAME_RESOLVED = "org.freedesktop.resolve1"
DBUS_NAME_SYSTEMD = "org.freedesktop.systemd1"
DBUS_NAME_TIMEDATE = "org.freedesktop.timedate1"
DBUS_NAME_UDISKS2 = "org.freedesktop.UDisks2"

DBUS_IFACE_ACCESSPOINT = "org.freedesktop.NetworkManager.AccessPoint"
DBUS_IFACE_BLOCK = "org.freedesktop.UDisks2.Block"
DBUS_IFACE_CONNECTION_ACTIVE = "org.freedesktop.NetworkManager.Connection.Active"
DBUS_IFACE_DEVICE = "org.freedesktop.NetworkManager.Device"
DBUS_IFACE_DEVICE_WIRELESS = "org.freedesktop.NetworkManager.Device.Wireless"
DBUS_IFACE_DNS = "org.freedesktop.NetworkManager.DnsManager"
DBUS_IFACE_DRIVE = "org.freedesktop.UDisks2.Drive"
DBUS_IFACE_FILESYSTEM = "org.freedesktop.UDisks2.Filesystem"
DBUS_IFACE_HAOS = "io.hass.os"
DBUS_IFACE_HAOS_APPARMOR = "io.hass.os.AppArmor"
DBUS_IFACE_HAOS_BOARDS = "io.hass.os.Boards"
DBUS_IFACE_HAOS_CGROUP = "io.hass.os.CGroup"
DBUS_IFACE_HAOS_CONFIG_SWAP = "io.hass.os.Config.Swap"
DBUS_IFACE_HAOS_DATADISK = "io.hass.os.DataDisk"
DBUS_IFACE_HAOS_SYSTEM = "io.hass.os.System"
DBUS_IFACE_HOSTNAME = "org.freedesktop.hostname1"
DBUS_IFACE_IP4CONFIG = "org.freedesktop.NetworkManager.IP4Config"
DBUS_IFACE_IP6CONFIG = "org.freedesktop.NetworkManager.IP6Config"
DBUS_IFACE_NM = "org.freedesktop.NetworkManager"
DBUS_IFACE_PARTITION = "org.freedesktop.UDisks2.Partition"
DBUS_IFACE_PARTITION_TABLE = "org.freedesktop.UDisks2.PartitionTable"
DBUS_IFACE_RAUC_INSTALLER = "de.pengutronix.rauc.Installer"
DBUS_IFACE_RESOLVED_MANAGER = "org.freedesktop.resolve1.Manager"
DBUS_IFACE_SETTINGS_CONNECTION = "org.freedesktop.NetworkManager.Settings.Connection"
DBUS_IFACE_SYSTEMD_MANAGER = "org.freedesktop.systemd1.Manager"
DBUS_IFACE_SYSTEMD_UNIT = "org.freedesktop.systemd1.Unit"
DBUS_IFACE_TIMEDATE = "org.freedesktop.timedate1"
DBUS_IFACE_UDISKS2_MANAGER = "org.freedesktop.UDisks2.Manager"

DBUS_SIGNAL_NM_CONNECTION_ACTIVE_CHANGED = (
    "org.freedesktop.NetworkManager.Connection.Active.StateChanged"
)
DBUS_SIGNAL_PROPERTIES_CHANGED = "org.freedesktop.DBus.Properties.PropertiesChanged"
DBUS_SIGNAL_RAUC_INSTALLER_COMPLETED = "de.pengutronix.rauc.Installer.Completed"

DBUS_OBJECT_BASE = "/"
DBUS_OBJECT_DNS = "/org/freedesktop/NetworkManager/DnsManager"
DBUS_OBJECT_HAOS = "/io/hass/os"
DBUS_OBJECT_HAOS_APPARMOR = "/io/hass/os/AppArmor"
DBUS_OBJECT_HAOS_BOARDS = "/io/hass/os/Boards"
DBUS_OBJECT_HAOS_CGROUP = "/io/hass/os/CGroup"
DBUS_OBJECT_HAOS_CONFIG_SWAP = "/io/hass/os/Config/Swap"
DBUS_OBJECT_HAOS_DATADISK = "/io/hass/os/DataDisk"
DBUS_OBJECT_HAOS_SYSTEM = "/io/hass/os/System"
DBUS_OBJECT_HOSTNAME = "/org/freedesktop/hostname1"
DBUS_OBJECT_LOGIND = "/org/freedesktop/login1"
DBUS_OBJECT_NM = "/org/freedesktop/NetworkManager"
DBUS_OBJECT_RESOLVED = "/org/freedesktop/resolve1"
DBUS_OBJECT_SETTINGS = "/org/freedesktop/NetworkManager/Settings"
DBUS_OBJECT_SYSTEMD = "/org/freedesktop/systemd1"
DBUS_OBJECT_TIMEDATE = "/org/freedesktop/timedate1"
DBUS_OBJECT_UDISKS2 = "/org/freedesktop/UDisks2"
DBUS_OBJECT_UDISKS2_MANAGER = "/org/freedesktop/UDisks2/Manager"

DBUS_ATTR_ACTIVE_ACCESSPOINT = "ActiveAccessPoint"
DBUS_ATTR_ACTIVE_CONNECTION = "ActiveConnection"
DBUS_ATTR_ACTIVE_CONNECTIONS = "ActiveConnections"
DBUS_ATTR_ACTIVE_STATE = "ActiveState"
DBUS_ATTR_ACTIVITY_LED = "ActivityLED"
DBUS_ATTR_ADDRESS_DATA = "AddressData"
DBUS_ATTR_BITRATE = "Bitrate"
DBUS_ATTR_BOARD = "Board"
DBUS_ATTR_BOOT_SLOT = "BootSlot"
DBUS_ATTR_CACHE_STATISTICS = "CacheStatistics"
DBUS_ATTR_CHASSIS = "Chassis"
DBUS_ATTR_COMPATIBLE = "Compatible"
DBUS_ATTR_CONFIGURATION = "Configuration"
DBUS_ATTR_CONNECTION = "Connection"
DBUS_ATTR_CONNECTION_BUS = "ConnectionBus"
DBUS_ATTR_CONNECTION_ENABLED = "ConnectivityCheckEnabled"
DBUS_ATTR_CONNECTIVITY = "Connectivity"
DBUS_ATTR_CURRENT_DEVICE = "CurrentDevice"
DBUS_ATTR_CURRENT_DNS_SERVER = "CurrentDNSServer"
DBUS_ATTR_CURRENT_DNS_SERVER_EX = "CurrentDNSServerEx"
DBUS_ATTR_DEFAULT = "Default"
DBUS_ATTR_DEPLOYMENT = "Deployment"
DBUS_ATTR_DESCRIPTION = "Description"
DBUS_ATTR_DEVICE = "Device"
DBUS_ATTR_DEVICE_INTERFACE = "Interface"
DBUS_ATTR_DEVICE_NUMBER = "DeviceNumber"
DBUS_ATTR_DEVICE_TYPE = "DeviceType"
DBUS_ATTR_DEVICES = "Devices"
DBUS_ATTR_DIAGNOSTICS = "Diagnostics"
DBUS_ATTR_DISK_LED = "DiskLED"
DBUS_ATTR_DNS = "DNS"
DBUS_ATTR_DNS_EX = "DNSEx"
DBUS_ATTR_DNS_OVER_TLS = "DNSOverTLS"
DBUS_ATTR_DNS_STUB_LISTENER = "DNSStubListener"
DBUS_ATTR_DNSSEC = "DNSSEC"
DBUS_ATTR_DNSSEC_NEGATIVE_TRUST_ANCHORS = "DNSSECNegativeTrustAnchors"
DBUS_ATTR_DNSSEC_STATISTICS = "DNSSECStatistics"
DBUS_ATTR_DNSSEC_SUPPORTED = "DNSSECSupported"
DBUS_ATTR_DOMAINS = "Domains"
DBUS_ATTR_DRIVE = "Drive"
DBUS_ATTR_DRIVER = "Driver"
DBUS_ATTR_EJECTABLE = "Ejectable"
DBUS_ATTR_FALLBACK_DNS = "FallbackDNS"
DBUS_ATTR_FALLBACK_DNS_EX = "FallbackDNSEx"
DBUS_ATTR_FINISH_TIMESTAMP = "FinishTimestamp"
DBUS_ATTR_FIRMWARE_TIMESTAMP_MONOTONIC = "FirmwareTimestampMonotonic"
DBUS_ATTR_FREQUENCY = "Frequency"
DBUS_ATTR_GATEWAY = "Gateway"
DBUS_ATTR_HEARTBEAT_LED = "HeartbeatLED"
DBUS_ATTR_HINT_AUTO = "HintAuto"
DBUS_ATTR_HINT_IGNORE = "HintIgnore"
DBUS_ATTR_HINT_NAME = "HintName"
DBUS_ATTR_HINT_SYSTEM = "HintSystem"
DBUS_ATTR_HWADDRESS = "HwAddress"
DBUS_ATTR_ID = "Id"
DBUS_ATTR_ID_LABEL = "IdLabel"
DBUS_ATTR_ID_ID_TYPE = "IdType"
DBUS_ATTR_ID_USAGE = "IdUsage"
DBUS_ATTR_ID_UUID = "IdUUID"
DBUS_ATTR_ID_VERSION = "IdVersion"
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
DBUS_ATTR_MODEL = "Model"
DBUS_ATTR_MOUNT_POINTS = "MountPoints"
DBUS_ATTR_MULTICAST_DNS = "MulticastDNS"
DBUS_ATTR_NAME = "Name"
DBUS_ATTR_NAMESERVER_DATA = "NameserverData"
DBUS_ATTR_NAMESERVERS = "Nameservers"
DBUS_ATTR_NTP = "NTP"
DBUS_ATTR_NTPSYNCHRONIZED = "NTPSynchronized"
DBUS_ATTR_NUMBER = "Number"
DBUS_ATTR_OFFSET = "Offset"
DBUS_ATTR_OPERATING_SYSTEM_PRETTY_NAME = "OperatingSystemPrettyName"
DBUS_ATTR_OPERATION = "Operation"
DBUS_ATTR_OPTIONS = "Options"
DBUS_ATTR_PARSER_VERSION = "ParserVersion"
DBUS_ATTR_PARTITIONS = "Partitions"
DBUS_ATTR_PATH = "Path"
DBUS_ATTR_POWER_LED = "PowerLED"
DBUS_ATTR_PRIMARY_CONNECTION = "PrimaryConnection"
DBUS_ATTR_READ_ONLY = "ReadOnly"
DBUS_ATTR_REMOVABLE = "Removable"
DBUS_ATTR_RESOLV_CONF_MODE = "ResolvConfMode"
DBUS_ATTR_REVISION = "Revision"
DBUS_ATTR_RCMANAGER = "RcManager"
DBUS_ATTR_SEAT = "Seat"
DBUS_ATTR_SERIAL = "Serial"
DBUS_ATTR_SIZE = "Size"
DBUS_ATTR_SSID = "Ssid"
DBUS_ATTR_STATE = "State"
DBUS_ATTR_STATE_FLAGS = "StateFlags"
DBUS_ATTR_STATIC_HOSTNAME = "StaticHostname"
DBUS_ATTR_STATIC_OPERATING_SYSTEM_CPE_NAME = "OperatingSystemCPEName"
DBUS_ATTR_STRENGTH = "Strength"
DBUS_ATTR_SUPPORTED_FILESYSTEMS = "SupportedFilesystems"
DBUS_ATTR_SYMLINKS = "Symlinks"
DBUS_ATTR_SWAP_SIZE = "SwapSize"
DBUS_ATTR_SWAPPINESS = "Swappiness"
DBUS_ATTR_TABLE = "Table"
DBUS_ATTR_TIME_DETECTED = "TimeDetected"
DBUS_ATTR_TIMEUSEC = "TimeUSec"
DBUS_ATTR_TIMEZONE = "Timezone"
DBUS_ATTR_TRANSACTION_STATISTICS = "TransactionStatistics"
DBUS_ATTR_TYPE = "Type"
DBUS_ATTR_USER_LED = "UserLED"
DBUS_ATTR_USERSPACE_TIMESTAMP_MONOTONIC = "UserspaceTimestampMonotonic"
DBUS_ATTR_UUID_UPPERCASE = "UUID"
DBUS_ATTR_UUID = "Uuid"
DBUS_ATTR_VARIANT = "Variant"
DBUS_ATTR_VENDOR = "Vendor"
DBUS_ATTR_VERSION = "Version"
DBUS_ATTR_VIRTUALIZATION = "Virtualization"
DBUS_ATTR_WHAT = "What"
DBUS_ATTR_WWN = "WWN"

DBUS_ERR_SYSTEMD_NO_SUCH_UNIT = "org.freedesktop.systemd1.NoSuchUnit"


class RaucState(StrEnum):
    """Rauc slot states."""

    GOOD = "good"
    BAD = "bad"
    ACTIVE = "active"


class InterfaceMethod(StrEnum):
    """Interface method simple."""

    AUTO = "auto"
    MANUAL = "manual"
    DISABLED = "disabled"
    LINK_LOCAL = "link-local"


class InterfaceAddrGenMode(IntEnum):
    """Interface addr_gen_mode."""

    EUI64 = 0
    STABLE_PRIVACY = 1
    DEFAULT_OR_EUI64 = 2
    DEFAULT = 3


class InterfaceIp6Privacy(IntEnum):
    """Interface ip6_privacy."""

    DEFAULT = -1
    DISABLED = 0
    ENABLED_PREFER_PUBLIC = 1
    ENABLED = 2


class ConnectionType(StrEnum):
    """Connection type."""

    ETHERNET = "802-3-ethernet"
    WIRELESS = "802-11-wireless"


class ConnectionStateType(IntEnum):
    """Connection states.

    https://developer.gnome.org/NetworkManager/stable/nm-dbus-types.html#NMActiveConnectionState
    """

    UNKNOWN = 0
    ACTIVATING = 1
    ACTIVATED = 2
    DEACTIVATING = 3
    DEACTIVATED = 4


class ConnectionStateFlags(IntEnum):
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


class ConnectivityState(IntEnum):
    """Network connectvity.

    https://developer.gnome.org/NetworkManager/unstable/nm-dbus-types.html#NMConnectivityState
    """

    CONNECTIVITY_UNKNOWN = 0
    CONNECTIVITY_NONE = 1
    CONNECTIVITY_PORTAL = 2
    CONNECTIVITY_LIMITED = 3
    CONNECTIVITY_FULL = 4


class DeviceType(IntEnum):
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


class WirelessMethodType(IntEnum):
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


class MulticastProtocolEnabled(StrEnum):
    """Multicast protocol enabled or resolve."""

    YES = "yes"
    NO = "no"
    RESOLVE = "resolve"


class DNSOverTLSEnabled(StrEnum):
    """DNS over TLS enabled."""

    YES = "yes"
    NO = "no"
    OPPORTUNISTIC = "opportunistic"


class DNSSECValidation(StrEnum):
    """DNSSEC validation enforced."""

    YES = "yes"
    NO = "no"
    ALLOW_DOWNGRADE = "allow-downgrade"


class DNSStubListenerEnabled(StrEnum):
    """DNS stub listener enabled."""

    YES = "yes"
    NO = "no"
    TCP_ONLY = "tcp"
    UDP_ONLY = "udp"


class ResolvConfMode(StrEnum):
    """Resolv.conf management mode."""

    FOREIGN = "foreign"
    MISSING = "missing"
    STATIC = "static"
    STUB = "stub"
    UPLINK = "uplink"


class StopUnitMode(StrEnum):
    """Mode for stopping the unit."""

    REPLACE = "replace"
    FAIL = "fail"
    IGNORE_DEPENDENCIES = "ignore-dependencies"
    IGNORE_REQUIREMENTS = "ignore-requirements"


class StartUnitMode(StrEnum):
    """Mode for starting the unit."""

    REPLACE = "replace"
    FAIL = "fail"
    IGNORE_DEPENDENCIES = "ignore-dependencies"
    IGNORE_REQUIREMENTS = "ignore-requirements"
    ISOLATE = "isolate"


class UnitActiveState(StrEnum):
    """Active state of a systemd unit."""

    ACTIVE = "active"
    ACTIVATING = "activating"
    DEACTIVATING = "deactivating"
    FAILED = "failed"
    INACTIVE = "inactive"
    MAINTENANCE = "maintenance"
    RELOADING = "reloading"
