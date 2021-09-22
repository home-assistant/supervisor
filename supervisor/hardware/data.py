"""Data representation of Hardware."""
from __future__ import annotations

from pathlib import Path

import attr
import pyudev


@attr.s(slots=True, frozen=True)
class Device:
    """Represent a device."""

    name: str = attr.ib(eq=False)
    path: Path = attr.ib(eq=False)
    sysfs: Path = attr.ib(eq=True)
    subsystem: str = attr.ib(eq=False)
    parent: Path | None = attr.ib(eq=False)
    links: list[Path] = attr.ib(eq=False)
    attributes: dict[str, str] = attr.ib(eq=False)
    children: list[Path] = attr.ib(eq=False)

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
            None if not udevice.parent else Path(udevice.parent.sys_path),
            [Path(node) for node in udevice.device_links],
            {attr: udevice.properties[attr] for attr in udevice.properties},
            [Path(node.sys_path) for node in udevice.children],
        )
