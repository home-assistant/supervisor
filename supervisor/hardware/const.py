"""Constants for hardware."""
from enum import Enum

ATTR_BY_ID = "by_id"
ATTR_SUBSYSTEM = "subsystem"
ATTR_SYSFS = "sysfs"
ATTR_DEV_PATH = "dev_path"
ATTR_ATTRIBUTES = "attributes"


class UdevSubsystem(str, Enum):
    """Udev subsystem class."""

    SERIAL = "tty"
    USB = "usb"
    INPUT = "input"
    DISK = "block"
    PCI = "pci"
    AUDIO = "sound"
    VIDEO = "video4linux"
    MEDIA = "media"
    GPIO = "gpio"
    GPIOMEM = "gpiomem"
    VCHIQ = "vchiq"
    GRAPHICS = "graphics"
    CEC = "CEC"
    DRM = "drm"


class PolicyGroup(str, Enum):
    """Policy groups backend."""

    UART = "uart"
    GPIO = "gpio"
    USB = "usb"
    VIDEO = "video"
    AUDIO = "audio"


class HardwareAction(str, Enum):
    """Hardware device action."""

    ADD = "add"
    REMOVE = "remove"


class UdevKernelAction(str, Enum):
    """Udev kernel device action."""

    ADD = "add"
    REMOVE = "remove"
    CHANGE = "change"
    BIND = "bind"
    UNBIND = "unbind"
