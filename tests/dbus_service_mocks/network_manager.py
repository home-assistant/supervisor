"""Mock of Network Manager service."""

from dbus_fast import DBusError
from dbus_fast.service import PropertyAccess, dbus_property, signal

from .base import DBusServiceMock, dbus_method

BUS_NAME = "org.freedesktop.NetworkManager"


def setup(object_path: str | None = None) -> DBusServiceMock:
    """Create dbus mock object."""
    return NetworkManager()


class NetworkManager(DBusServiceMock):
    """Network Manager mock.

    gdbus introspect --system --dest org.freedesktop.NetworkManager --object-path /org/freedesktop/NetworkManager
    """

    interface = "org.freedesktop.NetworkManager"
    object_path = "/org/freedesktop/NetworkManager"
    version = "1.22.10"
    connectivity_check_enabled = True
    connectivity = 4
    devices = [
        "/org/freedesktop/NetworkManager/Devices/1",
        "/org/freedesktop/NetworkManager/Devices/3",
    ]

    @dbus_property(access=PropertyAccess.READ)
    def Devices(self) -> "ao":
        """Get Devices."""
        return self.devices

    @dbus_property(access=PropertyAccess.READ)
    def AllDevices(self) -> "ao":
        """Get AllDevices."""
        return [
            "/org/freedesktop/NetworkManager/Devices/1",
            "/org/freedesktop/NetworkManager/Devices/2",
            "/org/freedesktop/NetworkManager/Devices/3",
        ]

    @dbus_property(access=PropertyAccess.READ)
    def Checkpoints(self) -> "ao":
        """Get Checkpoints."""
        return []

    @dbus_property(access=PropertyAccess.READ)
    def NetworkingEnabled(self) -> "b":
        """Get NetworkingEnabled."""
        return True

    @dbus_property()
    def WirelessEnabled(self) -> "b":
        """Get WirelessEnabled."""
        return True

    @WirelessEnabled.setter
    def WirelessEnabled(self, value: "b"):
        """Set WirelessEnabled."""
        self.emit_properties_changed({"WirelessEnabled": value})

    @dbus_property(access=PropertyAccess.READ)
    def WirelessHardwareEnabled(self) -> "b":
        """Get WirelessHardwareEnabled."""
        return True

    @dbus_property()
    def WwanEnabled(self) -> "b":
        """Get WwanEnabled."""
        return True

    @WwanEnabled.setter
    def WwanEnabled(self, value: "b"):
        """Set WwanEnabled."""
        self.emit_properties_changed({"WwanEnabled": value})

    @dbus_property(access=PropertyAccess.READ)
    def WwanHardwareEnabled(self) -> "b":
        """Get WwanHardwareEnabled."""
        return True

    @dbus_property()
    def WimaxEnabled(self) -> "b":
        """Get WimaxEnabled."""
        return False

    @WimaxEnabled.setter
    def WimaxEnabled(self, value: "b"):
        """Set WimaxEnabled."""
        self.emit_properties_changed({"WimaxEnabled": value})

    @dbus_property(access=PropertyAccess.READ)
    def WimaxHardwareEnabled(self) -> "b":
        """Get WimaxHardwareEnabled."""
        return False

    @dbus_property(access=PropertyAccess.READ)
    def ActiveConnections(self) -> "ao":
        """Get ActiveConnections."""
        return ["/org/freedesktop/NetworkManager/ActiveConnection/1"]

    @dbus_property(access=PropertyAccess.READ)
    def PrimaryConnection(self) -> "o":
        """Get PrimaryConnection."""
        return "/org/freedesktop/NetworkManager/ActiveConnection/1"

    @dbus_property(access=PropertyAccess.READ)
    def PrimaryConnectionType(self) -> "s":
        """Get PrimaryConnectionType."""
        return "802-3-ethernet"

    @dbus_property(access=PropertyAccess.READ)
    def Metered(self) -> "u":
        """Get Metered."""
        return 4

    @dbus_property(access=PropertyAccess.READ)
    def ActivatingConnection(self) -> "o":
        """Get ActivatingConnection."""
        return "/"

    @dbus_property(access=PropertyAccess.READ)
    def Startup(self) -> "b":
        """Get Startup."""
        return False

    @dbus_property(access=PropertyAccess.READ)
    def Version(self) -> "s":
        """Get Version."""
        return self.version

    @dbus_property(access=PropertyAccess.READ)
    def Capabilities(self) -> "au":
        """Get Capabilities."""
        return [1]

    @dbus_property(access=PropertyAccess.READ)
    def State(self) -> "u":
        """Get State."""
        return 70

    @dbus_property(access=PropertyAccess.READ)
    def Connectivity(self) -> "u":
        """Get Connectivity."""
        return self.connectivity

    @dbus_property(access=PropertyAccess.READ)
    def ConnectivityCheckAvailable(self) -> "b":
        """Get ConnectivityCheckAvailable."""
        return True

    @dbus_property()
    def ConnectivityCheckEnabled(self) -> "b":
        """Get ConnectivityCheckEnabled."""
        return self.connectivity_check_enabled

    @ConnectivityCheckEnabled.setter
    def ConnectivityCheckEnabled(self, value: "b"):
        """Set ConnectivityCheckEnabled."""
        self.emit_properties_changed({"ConnectivityCheckEnabled": value})

    @dbus_property(access=PropertyAccess.READ)
    def ConnectivityCheckUri(self) -> "s":
        """Get ConnectivityCheckUri."""
        return "http://connectivity-check.ubuntu.com/"

    @dbus_property()
    def GlobalDnsConfiguration(self) -> "a{sv}":
        """Get GlobalDnsConfiguration."""
        return {}

    @GlobalDnsConfiguration.setter
    def GlobalDnsConfiguration(self, value: "a{sv}"):
        """Set GlobalDnsConfiguration."""
        self.emit_properties_changed({"GlobalDnsConfiguration": value})

    @signal()
    def CheckPermissions(self) -> None:
        """Signal CheckPermissions."""

    # These signals all seem redundant. Their respective properties fire PropertiesChanged signals
    @signal()
    def StateChanged(self) -> "u":
        """Signal StateChanged."""
        return 70

    @signal()
    def DeviceAdded(self) -> "o":
        """Signal DeviceAdded."""
        return "/org/freedesktop/NetworkManager/Devices/2"

    @signal()
    def DeviceRemoved(self) -> "o":
        """Signal DeviceRemoved."""
        return "/org/freedesktop/NetworkManager/Devices/2"

    @dbus_method()
    def Reload(self, flags: "u") -> None:
        """Do Reload method."""

    @dbus_method()
    def GetDevices(self) -> "ao":
        """Do GetDevices method."""
        return self.Devices

    @dbus_method()
    def GetAllDevices(self) -> "ao":
        """Do GetAllDevices method."""
        return self.AllDevices

    @dbus_method()
    def GetDeviceByIpIface(self, iface: "s") -> "o":
        """Do GetDeviceByIpIface method."""
        return "/org/freedesktop/NetworkManager/Devices/1"

    @dbus_method()
    def ActivateConnection(
        self, connection: "o", device: "o", specific_object: "o"
    ) -> "o":
        """Do ActivateConnection method."""
        return "/org/freedesktop/NetworkManager/ActiveConnection/1"

    @dbus_method()
    def AddAndActivateConnection(
        self, connection: "a{sa{sv}}", device: "o", speciic_object: "o"
    ) -> "oo":
        """Do AddAndActivateConnection method."""
        if connection["connection"]["type"].value == "802-11-wireless":
            if "802-11-wireless" not in connection:
                raise DBusError(
                    "org.freedesktop.NetworkManager.Device.InvalidConnection",
                    "A 'wireless' setting is required if no AP path was given.",
                )
            if "ssid" not in connection["802-11-wireless"]:
                raise DBusError(
                    "org.freedesktop.NetworkManager.Device.InvalidConnection",
                    "A 'wireless' setting with a valid SSID is required if no AP path was given.",
                )

        return [
            "/org/freedesktop/NetworkManager/Settings/1",
            "/org/freedesktop/NetworkManager/ActiveConnection/1",
        ]

    @dbus_method()
    def AddAndActivateConnection2(
        self,
        connection: "a{sa{sv}}",
        device: "o",
        speciic_object: "o",
        options: "a{sv}",
    ) -> "ooa{sv}":
        """Do AddAndActivateConnection2 method."""
        return [
            "/org/freedesktop/NetworkManager/Settings/1",
            "/org/freedesktop/NetworkManager/ActiveConnection/1",
            {},
        ]

    @dbus_method()
    def DeactivateConnection(self, active_connection: "o") -> None:
        """Do DeactivateConnection method."""

    @dbus_method()
    def Sleep(self, sleep: "b") -> None:
        """Do Sleep method."""

    @dbus_method()
    def Enable(self, enable: "b") -> None:
        """Do Enable method."""

    @dbus_method()
    def GetPermissions(self) -> "a{ss}":
        """Do GetPermissions method."""
        return {
            "org.freedesktop.NetworkManager.checkpoint-rollback": "yes",
            "org.freedesktop.NetworkManager.enable-disable-connectivity-check": "yes",
            "org.freedesktop.NetworkManager.enable-disable-network": "yes",
            "org.freedesktop.NetworkManager.enable-disable-statistics": "yes",
            "org.freedesktop.NetworkManager.enable-disable-wifi": "yes",
            "org.freedesktop.NetworkManager.enable-disable-wimax": "yes",
            "org.freedesktop.NetworkManager.enable-disable-wwan": "yes",
            "org.freedesktop.NetworkManager.network-control": "yes",
            "org.freedesktop.NetworkManager.reload": "yes",
            "org.freedesktop.NetworkManager.settings.modify.global-dns": "yes",
            "org.freedesktop.NetworkManager.settings.modify.hostname": "yes",
            "org.freedesktop.NetworkManager.settings.modify.own": "yes",
            "org.freedesktop.NetworkManager.settings.modify.system": "yes",
            "org.freedesktop.NetworkManager.sleep-wake": "yes",
            "org.freedesktop.NetworkManager.wifi.scan": "yes",
            "org.freedesktop.NetworkManager.wifi.share.open": "yes",
            "org.freedesktop.NetworkManager.wifi.share.protected": "yes",
        }

    @dbus_method()
    def SetLogging(self, level: "s", domains: "s") -> None:
        """Do SetLogging method."""

    @dbus_method()
    def GetLogging(self) -> "ss":
        """Do GetLogging method."""
        return [
            "INFO",
            "PLATFORM,RFKILL,ETHER,WIFI,BT,MB,DHCP4,DHCP6,PPP,IP4,IP6,AUTOIP4,DNS,VPN,"
            "SHARING,SUPPLICANT,AGENTS,SETTINGS,SUSPEND,CORE,DEVICE,OLPC,INFINIBAND,"
            "FIREWALL,ADSL,BOND,VLAN,BRIDGE,TEAM,CONCHECK,DCB,DISPATCH,AUDIT,SYSTEMD,PROXY",
        ]

    @dbus_method()
    def CheckConnectivity(self) -> "u":
        """Do CheckConnectivity method."""
        return self.Connectivity

    @dbus_method()
    def state(self) -> "u":
        """Do state method."""
        return self.State

    @dbus_method()
    def CheckpointCreate(self, devices: "ao", rollback_timeout: "u", flags: "u") -> "o":
        """Do CheckpointCreate method."""
        return "/org/freedesktop/NetworkManager/Checkpoint/1"

    @dbus_method()
    def CheckpointDestroy(self, checkpoint: "o") -> None:
        """Do CheckpointDestroy method."""

    @dbus_method()
    def CheckpointRollback(self, checkpoint: "o") -> "a{su}":
        """Do CheckpointRollback method."""
        return {}

    @dbus_method()
    def CheckpointAdjustRollbackTimeout(
        self, checkpoint: "o", add_timeout: "u"
    ) -> None:
        """Do CheckpointAdjustRollbackTimeout method."""
