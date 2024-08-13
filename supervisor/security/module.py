"""Fetch last versions from webserver."""

from __future__ import annotations

import logging

from ..const import (
    ATTR_CONTENT_TRUST,
    ATTR_FORCE_SECURITY,
    ATTR_PWNED,
    FILE_HASSIO_SECURITY,
)
from ..coresys import CoreSys, CoreSysAttributes
from ..exceptions import (
    CodeNotaryError,
    CodeNotaryUntrusted,
    PwnedError,
    SecurityJobError,
)
from ..jobs.decorator import Job, JobCondition, JobExecutionLimit
from ..resolution.const import ContextType, IssueType, SuggestionType
from ..utils.codenotary import cas_validate
from ..utils.common import FileConfiguration
from ..utils.pwned import check_pwned_password
from ..validate import SCHEMA_SECURITY_CONFIG
from .const import ContentTrustResult, IntegrityResult

_LOGGER: logging.Logger = logging.getLogger(__name__)


class Security(FileConfiguration, CoreSysAttributes):
    """Handle Security properties."""

    def __init__(self, coresys: CoreSys):
        """Initialize updater."""
        super().__init__(FILE_HASSIO_SECURITY, SCHEMA_SECURITY_CONFIG)
        self.coresys = coresys

    @property
    def content_trust(self) -> bool:
        """Return if content trust is enabled/disabled."""
        return self._data[ATTR_CONTENT_TRUST]

    @content_trust.setter
    def content_trust(self, value: bool) -> None:
        """Set content trust is enabled/disabled."""
        self._data[ATTR_CONTENT_TRUST] = value

    @property
    def force(self) -> bool:
        """Return if force security is enabled/disabled."""
        return self._data[ATTR_FORCE_SECURITY]

    @force.setter
    def force(self, value: bool) -> None:
        """Set force security is enabled/disabled."""
        self._data[ATTR_FORCE_SECURITY] = value

    @property
    def pwned(self) -> bool:
        """Return if pwned is enabled/disabled."""
        return self._data[ATTR_PWNED]

    @pwned.setter
    def pwned(self, value: bool) -> None:
        """Set pwned is enabled/disabled."""
        self._data[ATTR_PWNED] = value

    async def verify_content(self, signer: str, checksum: str) -> None:
        """Verify content on CAS."""
        if not self.content_trust:
            _LOGGER.warning("Disabled content-trust, skip validation")
            return

        try:
            await cas_validate(signer, checksum)
        except CodeNotaryUntrusted:
            raise
        except CodeNotaryError:
            if self.force:
                raise
            self.sys_resolution.create_issue(
                IssueType.TRUST,
                ContextType.SYSTEM,
                suggestions=[SuggestionType.EXECUTE_INTEGRITY],
            )
            return

    async def verify_own_content(self, checksum: str) -> None:
        """Verify content from HA org."""
        return await self.verify_content("notary@home-assistant.io", checksum)

    async def verify_secret(self, pwned_hash: str) -> None:
        """Verify pwned state of a secret."""
        if not self.pwned:
            _LOGGER.warning("Disabled pwned, skip validation")
            return

        try:
            await check_pwned_password(self.sys_websession, pwned_hash)
        except PwnedError:
            if self.force:
                raise
            return

    @Job(
        name="security_manager_integrity_check",
        conditions=[JobCondition.INTERNET_SYSTEM],
        on_condition=SecurityJobError,
        limit=JobExecutionLimit.ONCE,
    )
    async def integrity_check(self) -> IntegrityResult:
        """Run a full system integrity check of the platform.

        We only allow to install trusted content.
        This is a out of the band manual check.
        """
        result: IntegrityResult = IntegrityResult()
        if not self.content_trust:
            _LOGGER.warning(
                "Skipping integrity check, content_trust is globally disabled"
            )
            return result

        # Supervisor
        try:
            await self.sys_supervisor.check_trust()
            result.supervisor = ContentTrustResult.PASS
        except CodeNotaryUntrusted:
            result.supervisor = ContentTrustResult.ERROR
            self.sys_resolution.create_issue(IssueType.TRUST, ContextType.SUPERVISOR)
        except CodeNotaryError:
            result.supervisor = ContentTrustResult.FAILED

        # Core
        try:
            await self.sys_homeassistant.core.check_trust()
            result.core = ContentTrustResult.PASS
        except CodeNotaryUntrusted:
            result.core = ContentTrustResult.ERROR
            self.sys_resolution.create_issue(IssueType.TRUST, ContextType.CORE)
        except CodeNotaryError:
            result.core = ContentTrustResult.FAILED

        # Plugins
        for plugin in self.sys_plugins.all_plugins:
            try:
                await plugin.check_trust()
                result.plugins[plugin.slug] = ContentTrustResult.PASS
            except CodeNotaryUntrusted:
                result.plugins[plugin.slug] = ContentTrustResult.ERROR
                self.sys_resolution.create_issue(
                    IssueType.TRUST, ContextType.PLUGIN, reference=plugin.slug
                )
            except CodeNotaryError:
                result.plugins[plugin.slug] = ContentTrustResult.FAILED

        # Add-ons
        for addon in self.sys_addons.installed:
            if not addon.signed:
                result.addons[addon.slug] = ContentTrustResult.UNTESTED
                continue
            try:
                await addon.check_trust()
                result.addons[addon.slug] = ContentTrustResult.PASS
            except CodeNotaryUntrusted:
                result.addons[addon.slug] = ContentTrustResult.ERROR
                self.sys_resolution.create_issue(
                    IssueType.TRUST, ContextType.ADDON, reference=addon.slug
                )
            except CodeNotaryError:
                result.addons[addon.slug] = ContentTrustResult.FAILED

        return result
