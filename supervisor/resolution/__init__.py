"""Supervisor resolution center."""
from typing import List

from ..const import UnsupportedReason
from ..coresys import CoreSys, CoreSysAttributes


class ResolutionManager(CoreSysAttributes):
    """Resolution manager for supervisor."""

    def __init__(self, coresys: CoreSys):
        """Initialize Resolution manager."""
        self.coresys: CoreSys = coresys
        self._unsupported: List[UnsupportedReason] = []

    @property
    def unsupported(self) -> List[UnsupportedReason]:
        """Return a list of unsupported reasons."""
        return self._unsupported

    @unsupported.setter
    def unsupported(self, reason: UnsupportedReason) -> None:
        """Add a reason for unsupported."""
        self._unsupported.append(reason)
