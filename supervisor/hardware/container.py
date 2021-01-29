"""Handle udev for container."""

from ..coresys import CoreSys, CoreSysAttributes


class HwContainer(CoreSysAttributes):
    """Representation of an interface to udev / container."""

    def __init__(self, coresys: CoreSys):
        """Init hardware object."""
        self.coresys = coresys
