"""Data representation of Hardware."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import pyudev


@dataclass(slots=True, frozen=True)
class Device:
    """Represent a device."""

    name: str = field(compare=False)
    path: Path = field(compare=False)
    sysfs: Path
    subsystem: str = field(compare=False)
    parent: Path | None = field(compare=False)
    links: list[Path] = field(compare=False)
    attributes: dict[str, str] = field(compare=False)
    children: list[Path] = field(compare=False)

    @property
    def major(self) -> int:
        """Return Major cgroups."""
        return int(self.attributes.get("MAJOR", 0))

    @property
    def minor(self) -> int:
        """Return Major cgroups."""
        return int(self.attributes.get("MINOR", 0))

    @property
    def by_id(self) -> Path | None:
        """Return path by-id."""
        for link in self.links:
            if not link.match("/dev/*/by-id/*"):
                continue
            return link
        return None

    @staticmethod
    def import_udev(udevice: pyudev.Device) -> Device:
        """Remap a pyudev object into a Device."""
        return Device(
            udevice.sys_name,
            Path(udevice.device_node),
            Path(udevice.sys_path),
            udevice.subsystem,
            None if udevice.parent is None else Path(udevice.parent.sys_path),
            [Path(node) for node in udevice.device_links],
            {attr: udevice.properties[attr] for attr in udevice.properties},
            [Path(node.sys_path) for node in udevice.children],
        )
