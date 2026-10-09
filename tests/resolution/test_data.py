"""Tests for resolution data objects."""

from typing import Any

import pytest

from supervisor.resolution.const import ContextType, IssueType, SuggestionType
from supervisor.resolution.data import Issue, Suggestion


def test_issue_uuid_pinned() -> None:
    """Test issue uuid derivation does not change between versions.

    Home Assistant persists the ignored state of a repair under this uuid.
    """
    assert (
        Issue(IssueType.PWNED, ContextType.ADDON, reference="core_samba").uuid
        == "57fb6e6881fc51a4807636f323bcad99"
    )
    assert (
        Issue(
            IssueType.APP_PORT_CONFLICT,
            ContextType.ADDON,
            reference="a",
            reference_extra={"port": 80},
        ).uuid
        == "78c6842ed13451ad905e0addf53548a6"
    )


@pytest.mark.parametrize(
    ("cls", "type_"),
    [
        pytest.param(Issue, IssueType.APP_PORT_CONFLICT, id="issue"),
        pytest.param(Suggestion, SuggestionType.CLEAR_PORT_CONFIG, id="suggestion"),
    ],
)
def test_uuid_stable_for_same_identity(
    cls: type[Issue | Suggestion], type_: IssueType | SuggestionType
) -> None:
    """Test equal identities get the same uuid, regardless of extra key order."""
    first = cls(
        type_, ContextType.ADDON, reference="a", reference_extra={"x": 1, "port": 80}
    )
    second = cls(
        type_, ContextType.ADDON, reference="a", reference_extra={"port": 80, "x": 1}
    )

    assert first == second
    assert first.uuid == second.uuid


@pytest.mark.parametrize(
    ("changes"),
    [
        pytest.param({"type": IssueType.BOOT_FAIL}, id="type"),
        pytest.param({"context": ContextType.CORE}, id="context"),
        pytest.param({"reference": "b"}, id="reference"),
        pytest.param({"reference": None}, id="no_reference"),
        pytest.param({"reference_extra": {"port": 81}}, id="reference_extra"),
        pytest.param({"reference_extra": None}, id="no_reference_extra"),
    ],
)
def test_issue_uuid_differs_for_other_identity(changes: dict[str, Any]) -> None:
    """Test issues with a different identity get a different uuid."""
    base: dict[str, Any] = {
        "type": IssueType.APP_PORT_CONFLICT,
        "context": ContextType.ADDON,
        "reference": "a",
        "reference_extra": {"port": 80},
    }

    assert Issue(**base).uuid != Issue(**(base | changes)).uuid
