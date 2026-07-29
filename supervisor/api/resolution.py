"""Handle REST API for resolution."""

import asyncio
from collections.abc import Awaitable
from dataclasses import asdict
from typing import Any

from aiohttp import web
import voluptuous as vol

from ..const import (
    ATTR_AUTO,
    ATTR_CHECKS,
    ATTR_ENABLED,
    ATTR_ISSUES,
    ATTR_SLUG,
    ATTR_SUGGESTIONS,
    ATTR_UNHEALTHY,
    ATTR_UNSUPPORTED,
)
from ..coresys import CoreSysAttributes
from ..resolution.checks.base import CheckBase
from ..resolution.const import LEGACY_CHECK_SLUG_MAP
from ..resolution.data import Issue, Suggestion
from ..resolution.module import (
    process_check_dict_for_legacy_compatibility,
    process_issue_dict_for_legacy_compatibility,
)
from .utils import api_process, api_validate

SCHEMA_CHECK_OPTIONS = vol.Schema({vol.Optional(ATTR_ENABLED): bool})


class APIResolution(CoreSysAttributes):
    """Handle REST API for resolution."""

    def _extract_issue(self, request: web.Request) -> Issue:
        """Extract issue from request or raise."""
        return self.sys_resolution.get_issue_by_id(request.match_info["issue"])

    def _extract_suggestion(self, request: web.Request) -> Suggestion:
        """Extract suggestion from request or raise."""
        return self.sys_resolution.get_suggestion_by_id(
            request.match_info["suggestion"]
        )

    def _extract_check(self, request: web.Request) -> CheckBase:
        """Extract check from request or raise."""
        return self.sys_resolution.check.get(request.match_info["check"])

    def _extract_check_v1(self, request: web.Request) -> CheckBase:
        """Extract check from request using legacy slug mapping or raise (v1)."""
        slug = request.match_info["check"]
        # Translate legacy (old) slug to new slug if needed
        new_slug = LEGACY_CHECK_SLUG_MAP.get(slug, slug)
        return self.sys_resolution.check.get(new_slug)

    def _generate_suggestion_information(self, suggestion: Suggestion):
        """Generate suggestion information for response."""
        resp = asdict(suggestion)
        resp[ATTR_AUTO] = bool(
            [
                fix
                for fix in self.sys_resolution.fixup.fixes_for_suggestion(suggestion)
                if fix.auto
            ]
        )
        return resp

    def _build_info_response(self) -> dict[str, Any]:
        """Build the resolution info response with current (v2) names."""
        return {
            ATTR_UNSUPPORTED: sorted(self.sys_resolution.unsupported),
            ATTR_UNHEALTHY: sorted(self.sys_resolution.unhealthy),
            ATTR_SUGGESTIONS: [
                self._generate_suggestion_information(suggestion)
                for suggestion in self.sys_resolution.suggestions
            ],
            ATTR_ISSUES: [asdict(issue) for issue in self.sys_resolution.issues],
            ATTR_CHECKS: [
                {ATTR_ENABLED: check.enabled, ATTR_SLUG: check.slug}
                for check in self.sys_resolution.check.all_checks
            ],
        }

    @api_process
    async def info(self, request: web.Request) -> dict[str, Any]:
        """Return resolution information."""
        return self._build_info_response()

    @api_process
    async def info_v1(self, request: web.Request) -> dict[str, Any]:
        """Return resolution info (v1: uses legacy issue types and check slugs)."""
        data = self._build_info_response()
        return data | {
            ATTR_ISSUES: [
                process_issue_dict_for_legacy_compatibility(issue)
                for issue in data[ATTR_ISSUES]
            ],
            ATTR_CHECKS: [
                process_check_dict_for_legacy_compatibility(check)
                for check in data[ATTR_CHECKS]
            ],
        }

    @api_process
    async def apply_suggestion(self, request: web.Request) -> None:
        """Apply suggestion."""
        suggestion = self._extract_suggestion(request)
        await self.sys_resolution.apply_suggestion(suggestion)

    @api_process
    async def dismiss_suggestion(self, request: web.Request) -> None:
        """Dismiss suggestion."""
        suggestion = self._extract_suggestion(request)
        self.sys_resolution.dismiss_suggestion(suggestion)

    @api_process
    async def suggestions_for_issue(self, request: web.Request) -> dict[str, Any]:
        """Return suggestions that fix an issue."""
        issue = self._extract_issue(request)
        return {
            ATTR_SUGGESTIONS: [
                self._generate_suggestion_information(suggestion)
                for suggestion in self.sys_resolution.suggestions_for_issue(issue)
            ]
        }

    @api_process
    async def dismiss_issue(self, request: web.Request) -> None:
        """Dismiss issue."""
        issue = self._extract_issue(request)
        self.sys_resolution.dismiss_issue(issue)

    @api_process
    def healthcheck(self, request: web.Request) -> Awaitable[None]:
        """Run backend healthcheck."""
        return asyncio.shield(self.sys_resolution.healthcheck())

    @api_process
    async def options_check(self, request: web.Request) -> None:
        """Set options for check."""
        body = await api_validate(SCHEMA_CHECK_OPTIONS, request)
        check = self._extract_check(request)

        # Apply options
        if ATTR_ENABLED in body:
            check.enabled = body[ATTR_ENABLED]

        await self.sys_resolution.save_data()

    @api_process
    async def options_check_v1(self, request: web.Request) -> None:
        """Set options for check (v1: accepts legacy check slug in URL)."""
        body = await api_validate(SCHEMA_CHECK_OPTIONS, request)
        check = self._extract_check_v1(request)

        # Apply options
        if ATTR_ENABLED in body:
            check.enabled = body[ATTR_ENABLED]

        await self.sys_resolution.save_data()

    @api_process
    async def run_check(self, request: web.Request) -> None:
        """Execute a backend check."""
        check = self._extract_check(request)
        await check()

    @api_process
    async def run_check_v1(self, request: web.Request) -> None:
        """Execute a backend check (v1: accepts legacy check slug in URL)."""
        check = self._extract_check_v1(request)
        await check()
