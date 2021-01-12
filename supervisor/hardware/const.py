"""Constants for hardware."""
from enum import Enum


class UdevSubsysteme(str, Enum):
    """Udev subsystem class."""

    SERIAL = "tty"
    USB = "usb"
    INPUT = "input"
    DISK = "block"
