"""Constants for DBUS."""
from enum import Enum

DBUS_NAME_CONNECTION_ACTIVE = "org.freedesktop.NetworkManager.Connection.Active"
DBUS_NAME_DEVICE = "org.freedesktop.NetworkManager.Device"
DBUS_NAME_DNS = "org.freedesktop.NetworkManager.DnsManager"
DBUS_NAME_HOSTNAME = "org.freedesktop.hostname1"
DBUS_NAME_IP4CONFIG = "org.freedesktop.NetworkManager.IP4Config"
DBUS_NAME_NM = "org.freedesktop.NetworkManager"
DBUS_NAME_RAUC = "de.pengutronix.rauc"
DBUS_NAME_RAUC_INSTALLER = "de.pengutronix.rauc.Installer"
DBUS_NAME_RAUC_INSTALLER_COMPLETED = "de.pengutronix.rauc.Installer.Completed"
DBUS_NAME_SETTINGS_CONNECTION = "org.freedesktop.NetworkManager.Settings.Connection"
DBUS_NAME_SYSTEMD = "org.freedesktop.systemd1"

DBUS_OBJECT_BASE = "/"
DBUS_OBJECT_DNS = "/org/freedesktop/NetworkManager/DnsManager"
DBUS_OBJECT_HOSTNAME = "/org/freedesktop/hostname1"
DBUS_OBJECT_NM = "/org/freedesktop/NetworkManager"
DBUS_OBJECT_SYSTEMD = "/org/freedesktop/systemd1"

DBUS_ATTR_802_WIRELESS = "802-11-wireless"
DBUS_ATTR_802_WIRELESS_SECURITY = "802-11-wireless-security"
DBUS_ATTR_ACTIVE_CONNECTIONS = "ActiveConnections"
DBUS_ATTR_ADDRESS_DATA = "AddressData"
DBUS_ATTR_BOOT_SLOT = "BootSlot"
DBUS_ATTR_CHASSIS = "Chassis"
DBUS_ATTR_COMPATIBLE = "Compatible"
DBUS_ATTR_CONFIGURATION = "Configuration"
DBUS_ATTR_CONNECTION = "Connection"
DBUS_ATTR_DEFAULT = "Default"
DBUS_ATTR_DEPLOYMENT = "Deployment"
DBUS_ATTR_DEVICE_INTERFACE = "Interface"
DBUS_ATTR_DEVICE_TYPE = "DeviceType"
DBUS_ATTR_DEVICES = "Devices"
DBUS_ATTR_GATEWAY = "Gateway"
DBUS_ATTR_ID = "Id"
DBUS_ATTR_IP4ADDRESS = "Ip4Address"
DBUS_ATTR_IP4CONFIG = "Ip4Config"
DBUS_ATTR_KERNEL_RELEASE = "KernelRelease"
DBUS_ATTR_LAST_ERROR = "LastError"
DBUS_ATTR_MODE = "Mode"
DBUS_ATTR_NAMESERVERS = "Nameservers"
DBUS_ATTR_OPERATING_SYSTEM_PRETTY_NAME = "OperatingSystemPrettyName"
DBUS_ATTR_OPERATION = "Operation"
DBUS_ATTR_PRIMARY_CONNECTION = "PrimaryConnection"
DBUS_ATTR_RCMANAGER = "RcManager"
DBUS_ATTR_REAL = "Real"
DBUS_ATTR_STATE = "State"
DBUS_ATTR_STATIC_HOSTNAME = "StaticHostname"
DBUS_ATTR_STATIC_OPERATING_SYSTEM_CPE_NAME = "OperatingSystemCPEName"
DBUS_ATTR_TYPE = "Type"
DBUS_ATTR_UUID = "Uuid"
DBUS_ATTR_VARIANT = "Variant"


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


class InterfaceMethodSimple(str, Enum):
    """Interface method."""

    DHCP = "dhcp"
    STATIC = "static"


class ConnectionType(str, Enum):
    """Connection type."""

    ETHERNET = "802-3-ethernet"
    WIRELESS = "802-11-wireless"
