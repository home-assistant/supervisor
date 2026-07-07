"""Data objects."""

from dataclasses import dataclass, field
from typing import Any
from uuid import uuid4

from .const import (
    ContextType,
    IssueType,
    SuggestionType,
    UnhealthyReason,
    UnsupportedReason,
)


@dataclass(frozen=True, slots=True)
class Issue:
    """Represent an Issue."""

    type: IssueType
    context: ContextType
    reference: str | None = None
    reference_extra: dict[str, Any] | None = field(default=None, hash=False)
    uuid: str = field(default_factory=lambda: uuid4().hex, compare=False, init=False)


@dataclass(frozen=True, slots=True)
class Suggestion:
    """Represent an Suggestion."""

    type: SuggestionType
    context: ContextType
    reference: str | None = None
    reference_extra: dict[str, Any] | None = field(default=None, hash=False)
    uuid: str = field(default_factory=lambda: uuid4().hex, compare=False, init=False)


@dataclass(frozen=True, slots=True)
class HealthChanged:
    """Describe change in system health."""

    healthy: bool
    unhealthy_reasons: list[UnhealthyReason] | None = None


@dataclass(frozen=True, slots=True)
class SupportedChanged:
    """Describe change in system supported."""

    supported: bool
    unsupported_reasons: list[UnsupportedReason] | None = None
