"""Constants for hardware."""
from enum import Enum


class UdevSubsystem(str, Enum):
    """Udev subsystem class."""

    SERIAL = "tty"
    USB = "usb"
    INPUT = "input"
    DISK = "block"
    PCI = "pci"
    AUDIO = "sound"


class PolicyGroup(str, Enum):
    """Policy groups backend."""

    UART = "uart"
    GPIO = "gpio"
    USB = "usb"
    VIDEO = "video"
    AUDIO = "audio"
