"""Const for host."""
from enum import Enum


class InterfaceMode(str, Enum):
    """Configuration of an interface."""

    DISABLE = "disable"
    STATIC = "static"
    DHCP = "dhcp"
