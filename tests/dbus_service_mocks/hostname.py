"""Mock of hostname dbus service."""

from json import dumps

from dbus_fast.service import PropertyAccess, dbus_property

from .base import DBusServiceMock, dbus_method

BUS_NAME = "org.freedesktop.hostname1"


def setup(object_path: str | None = None) -> DBusServiceMock:
    """Create dbus mock object."""
    return Hostname()


class Hostname(DBusServiceMock):
    """Hostname mock.

    gdbus introspect --system --dest org.freedesktop.hostname1 --object-path /org/freedesktop/hostname1
    """

    object_path = "/org/freedesktop/hostname1"
    interface = "org.freedesktop.hostname1"

    @dbus_property(access=PropertyAccess.READ)
    def Hostname(self) -> "s":
        """Get Hostname."""
        return "homeassistant-n2"

    @dbus_property(access=PropertyAccess.READ)
    def StaticHostname(self) -> "s":
        """Get StaticHostname."""
        return "homeassistant-n2"

    @dbus_property(access=PropertyAccess.READ)
    def PrettyHostname(self) -> "s":
        """Get PrettyHostname."""
        return ""

    @dbus_property(access=PropertyAccess.READ)
    def IconName(self) -> "s":
        """Get IconName."""
        return "computer-embedded"

    @dbus_property(access=PropertyAccess.READ)
    def Chassis(self) -> "s":
        """Get Chassis."""
        return "embedded"

    @dbus_property(access=PropertyAccess.READ)
    def Deployment(self) -> "s":
        """Get Deployment."""
        return "development"

    @dbus_property(access=PropertyAccess.READ)
    def Location(self) -> "s":
        """Get Location."""
        return ""

    @dbus_property(access=PropertyAccess.READ)
    def KernelName(self) -> "s":
        """Get KernelName."""
        return "Linux"

    @dbus_property(access=PropertyAccess.READ)
    def KernelRelease(self) -> "s":
        """Get KernelRelease."""
        return "5.10.33"

    @dbus_property(access=PropertyAccess.READ)
    def KernelVersion(self) -> "s":
        """Get KernelVersion."""
        return "#1 SMP PREEMPT Wed May 5 00:55:38 UTC 2021"

    @dbus_property(access=PropertyAccess.READ)
    def OperatingSystemPrettyName(self) -> "s":
        """Get OperatingSystemPrettyName."""
        return "Home Assistant OS 6.0.dev20210504"

    @dbus_property(access=PropertyAccess.READ)
    def OperatingSystemCPEName(self) -> "s":
        """Get OperatingSystemCPEName."""
        return "cpe:2.3:o:home-assistant:haos:6.0.dev20210504:*:development:*:*:*:odroid-n2:*"

    @dbus_property(access=PropertyAccess.READ)
    def HomeURL(self) -> "s":
        """Get HomeURL."""
        return "https://hass.io/"

    @dbus_method()
    def SetHostname(self, hostname: "s", interactive: "b") -> None:
        """Set hostname."""
        self.emit_properties_changed({"Hostname": hostname})

    @dbus_method()
    def SetStaticHostname(self, hostname: "s", interactive: "b") -> None:
        """Set static hostname."""
        self.emit_properties_changed({"StaticHostname": hostname})

    @dbus_method()
    def SetPrettyHostname(self, hostname: "s", interactive: "b") -> None:
        """Set pretty hostname."""
        self.emit_properties_changed({"PrettyHostname": hostname})

    @dbus_method()
    def SetIconName(self, icon: "s", interactive: "b") -> None:
        """Set icon name."""
        self.emit_properties_changed({"IconName": icon})

    @dbus_method()
    def SetChassis(self, chassis: "s", interactive: "b") -> None:
        """Set chassis."""
        self.emit_properties_changed({"Chassis": chassis})

    @dbus_method()
    def SetDeployment(self, deployment: "s", interactive: "b") -> None:
        """Set deployment."""
        self.emit_properties_changed({"Deployment": deployment})

    @dbus_method()
    def SetLocation(self, location: "s", interactive: "b") -> None:
        """Set location."""
        self.emit_properties_changed({"Location": location})

    @dbus_method()
    def GetProductUUID(self, interactive: "b") -> "ay":
        """Get product UUID."""
        return b"d153e353-2a32-4763-b930-b27fbc980da5"

    @dbus_method()
    def Describe(self) -> "s":
        """Describe."""
        return dumps(
            {
                "Hostname": "odroid-dev",
                "StaticHostname": "odroid-dev",
                "PrettyHostname": None,
                "DefaultHostname": "homeassistant",
                "HostnameSource": "static",
                "IconName": "computer-embedded",
                "Chassis": "embedded",
                "Deployment": "development",
                "Location": None,
                "KernelName": "Linux",
                "KernelRelease": "5.15.88",
                "KernelVersion": "#1 SMP PREEMPT Mon Jan 16 23:45:23 UTC 2023",
                "OperatingSystemPrettyName": "Home Assistant OS 10.0.dev20230116",
                "OperatingSystemCPEName": "cpe:2.3:o:home-assistant:haos:10.0.dev20230116:*:development:*:*:*:odroid-n2:*",
                "OperatingSystemHomeURL": "https://hass.io/",
                "HardwareVendor": None,
                "HardwareModel": None,
                "ProductUUID": None,
            }
        )
