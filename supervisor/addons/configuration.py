"""Confgiuration Objects for Addon Config."""

from dataclasses import dataclass


@dataclass(slots=True)
class FolderMapping:
    """Represent folder mapping configuration."""

    path: str
    read_only: bool
