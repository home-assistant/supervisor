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
