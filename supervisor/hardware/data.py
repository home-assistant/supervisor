"""Data representation of Hardware."""
from pathlib import Path
from typing import Dict, List

import attr


@attr.s(slots=True, frozen=True)
class Device:
    """Represent a device."""

    name: str = attr.ib()
    path: Path = attr.ib()
    subsystem: str = attr.ib()
    links: List[Path] = attr.ib()
    attributes: Dict[str, str] = attr.ib()

    @property
    def cgroups_major(self) -> int:
        """Return Major cgroups."""
        return self.attributes.get("MAJOR", 0)

    @property
    def cgroups_minor(self) -> int:
        """Return Major cgroups."""
        return self.attributes.get("MINOR", 0)
