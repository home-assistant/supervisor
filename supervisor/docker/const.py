"""Docker constants."""
from enum import Enum


class Capabilities(str, Enum):
    """Linux Capabilities."""

    DAC_READ_SEARCH = "DAC_READ_SEARCH"
    IPC_LOCK = "IPC_LOCK"
    NET_ADMIN = "NET_ADMIN"
    SYS_ADMIN = "SYS_ADMIN"
    SYS_MODULE = "SYS_MODULE"
    SYS_NICE = "SYS_NICE"
    SYS_PTRACE = "SYS_PTRACE"
    SYS_RAWIO = "SYS_RAWIO"
    SYS_RESOURCE = "SYS_RESOURCE"
    SYS_TIME = "SYS_TIME"
