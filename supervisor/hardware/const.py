"""Constants for hardware."""

from enum import StrEnum


class UdevSubsystem(StrEnum):
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
    CEC = "cec"
    DRM = "drm"
    HIDRAW = "hidraw"
    RPI_HEVCMEM = "rpivid-hevcmem"
    RPI_H264MEM = "rpivid-h264mem"


class PolicyGroup(StrEnum):
    """Policy groups backend."""

    UART = "uart"
    GPIO = "gpio"
    USB = "usb"
    VIDEO = "video"
    AUDIO = "audio"
    BLUETOOTH = "bluetooth"


class HardwareAction(StrEnum):
    """Hardware device action."""

    ADD = "add"
    REMOVE = "remove"


class UdevKernelAction(StrEnum):
    """Udev kernel device action."""

    ADD = "add"
    REMOVE = "remove"
    CHANGE = "change"
    BIND = "bind"
    UNBIND = "unbind"
