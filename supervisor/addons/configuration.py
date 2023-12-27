"""Confgiuration Objects for Addon Config."""

from dataclasses import dataclass


@dataclass(slots=True)
class FolderMapping:
    """Represent folder mapping configuration."""

    path: str | None
    read_only: bool
