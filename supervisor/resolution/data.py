"""Data objects."""

from uuid import UUID, uuid4

import attr

from .const import (
    ContextType,
    IssueType,
    SuggestionType,
    UnhealthyReason,
    UnsupportedReason,
)


@attr.s(frozen=True, slots=True)
class Issue:
    """Represent an Issue."""

    type: IssueType = attr.ib()
    context: ContextType = attr.ib()
    reference: str | None = attr.ib(default=None)
    uuid: UUID = attr.ib(factory=lambda: uuid4().hex, eq=False, init=False)


@attr.s(frozen=True, slots=True)
class Suggestion:
    """Represent an Suggestion."""

    type: SuggestionType = attr.ib()
    context: ContextType = attr.ib()
    reference: str | None = attr.ib(default=None)
    uuid: UUID = attr.ib(factory=lambda: uuid4().hex, eq=False, init=False)


@attr.s(frozen=True, slots=True)
class HealthChanged:
    """Describe change in system health."""

    healthy: bool = attr.ib()
    unhealthy_reasons: list[UnhealthyReason] | None = attr.ib(default=None)


@attr.s(frozen=True, slots=True)
class SupportedChanged:
    """Describe change in system supported."""

    supported: bool = attr.ib()
    unsupported_reasons: list[UnsupportedReason] | None = attr.ib(default=None)
