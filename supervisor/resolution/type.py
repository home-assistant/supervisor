"""Data objects."""
from typing import Optional
from uuid import UUID, uuid4

import attr

from .const import ContextType, IssueType, SuggestionType


@attr.s(slots=True)
class Issue:
    """Represent an Issue."""

    type: IssueType = attr.ib()
    context: ContextType = attr.ib()
    reference: Optional[str] = attr.ib(default=None)
    uuid: UUID = attr.ib(factory=lambda: uuid4().hex, eq=False, init=False)


@attr.s(slots=True)
class Suggestion:
    """Represent an Suggestion."""

    type: SuggestionType = attr.ib()
    context: ContextType = attr.ib()
    reference: Optional[str] = attr.ib(default=None)
    uuid: UUID = attr.ib(factory=lambda: uuid4().hex, eq=False, init=False)
