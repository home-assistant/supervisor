"""Confgiuration Objects for Addon Config."""

from dataclasses import dataclass

from ..const import MappingType


@dataclass(slots=True)
class FolderMapping:
    """Represent folder mapping configuration."""

    path: str
    read_only: bool = True
    type: MappingType
