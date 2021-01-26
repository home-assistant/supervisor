"""Data representation of Hardware."""
from pathlib import Path
from typing import Dict, List

import attr


@attr.s(slots=True, frozen=True)
class Device:
    """Represent a device."""

    name: str = attr.ib(eq=False)
    path: Path = attr.ib(eq=False)
    sysfs: Path = attr.ib(eq=True)
    subsystem: str = attr.ib(eq=False)
    links: List[Path] = attr.ib(eq=False)
    attributes: Dict[str, str] = attr.ib(eq=False)

    @property
    def cgroups_major(self) -> int:
        """Return Major cgroups."""
        return self.attributes.get("MAJOR", 0)

    @property
    def cgroups_minor(self) -> int:
        """Return Major cgroups."""
        return self.attributes.get("MINOR", 0)
