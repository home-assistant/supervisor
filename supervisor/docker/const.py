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


DBUS_PATH = "/run/dbus"
DBUS_VOLUME = {"bind": DBUS_PATH, "mode": "ro"}

ENV_TIME = "TZ"
ENV_TOKEN = "SUPERVISOR_TOKEN"
ENV_TOKEN_OLD = "HASSIO_TOKEN"
