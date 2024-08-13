"""Security constants."""

from enum import StrEnum

import attr


class ContentTrustResult(StrEnum):
    """Content trust result enum."""

    PASS = "pass"
    ERROR = "error"
    FAILED = "failed"
    UNTESTED = "untested"


@attr.s
class IntegrityResult:
    """Result of a full integrity check."""

    supervisor: ContentTrustResult = attr.ib(default=ContentTrustResult.UNTESTED)
    core: ContentTrustResult = attr.ib(default=ContentTrustResult.UNTESTED)
    plugins: dict[str, ContentTrustResult] = attr.ib(default={})
    addons: dict[str, ContentTrustResult] = attr.ib(default={})
