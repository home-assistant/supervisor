"""Data objects."""

from dataclasses import dataclass, field
import json
from typing import Any
from uuid import UUID, uuid5

from .const import (
    ContextType,
    IssueType,
    SuggestionType,
    UnhealthyReason,
    UnsupportedReason,
)

NAMESPACE_RESOLUTION = UUID("c822cec1-f675-44e3-a89d-55d7d46355fc")


def _identity_uuid(
    kind: str,
    type_: str,
    context: str,
    reference: str | None,
    reference_extra: dict[str, Any] | None,
) -> str:
    """Derive a uuid from the identity of an issue or suggestion.

    Home Assistant keys repairs (and their ignored state) on this uuid, so it
    has to stay the same when a check raises the same issue after a restart.
    """
    # JSON keeps field boundaries, e.g. None distinct from "None"
    name = json.dumps(
        [kind, type_, context, reference, reference_extra], sort_keys=True
    )
    return uuid5(NAMESPACE_RESOLUTION, name).hex


@dataclass(frozen=True, slots=True)
class Issue:
    """Represent an Issue."""

    type: IssueType
    context: ContextType
    reference: str | None = None
    reference_extra: dict[str, Any] | None = field(default=None, hash=False)
    uuid: str = field(init=False, compare=False)

    def __post_init__(self) -> None:
        """Derive uuid from identity."""
        object.__setattr__(
            self,
            "uuid",
            _identity_uuid(
                "issue", self.type, self.context, self.reference, self.reference_extra
            ),
        )


@dataclass(frozen=True, slots=True)
class Suggestion:
    """Represent an Suggestion."""

    type: SuggestionType
    context: ContextType
    reference: str | None = None
    reference_extra: dict[str, Any] | None = field(default=None, hash=False)
    uuid: str = field(init=False, compare=False)

    def __post_init__(self) -> None:
        """Derive uuid from identity."""
        object.__setattr__(
            self,
            "uuid",
            _identity_uuid(
                "suggestion",
                self.type,
                self.context,
                self.reference,
                self.reference_extra,
            ),
        )


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
