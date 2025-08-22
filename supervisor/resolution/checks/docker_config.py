"""Helper to check if docker config for container needs an update."""

from ...addons.const import MappingType
from ...const import CoreState
from ...coresys import CoreSys
from ...docker.const import PATH_MEDIA, PATH_SHARE, PropagationMode
from ...docker.interface import DockerInterface
from ..const import ContextType, IssueType, SuggestionType
from ..data import Issue
from .base import CheckBase


def _check_container(container: DockerInterface, addon=None) -> bool:
    """Check if container has mount propagation issues requiring recreate.

    For add-ons, only validates mounts explicitly configured (not Docker VOLUMEs).
    For Core/plugins, validates all /media and /share mounts.
    """
    # For add-ons, check mounts against their actual configured targets
    if addon is not None:
        addon_mapping = addon.map_volumes
        configured_targets = set()

        # Get actual target paths from add-on configuration
        if MappingType.MEDIA in addon_mapping:
            target = addon_mapping[MappingType.MEDIA].path or PATH_MEDIA.as_posix()
            configured_targets.add(target)

        if MappingType.SHARE in addon_mapping:
            target = addon_mapping[MappingType.SHARE].path or PATH_SHARE.as_posix()
            configured_targets.add(target)

        if not configured_targets:
            return False

        # Check if any configured targets have propagation issues
        for mount in container.meta_mounts:
            if (
                mount.get("Destination") in configured_targets
                and mount.get("Propagation") != PropagationMode.RSLAVE
            ):
                return True

        return False

    # For Home Assistant Core and plugins, check default /media and /share paths
    return any(
        mount.get("Propagation") != PropagationMode.RSLAVE
        for mount in container.meta_mounts
        if mount.get("Destination") in [PATH_MEDIA.as_posix(), PATH_SHARE.as_posix()]
    )


def setup(coresys: CoreSys) -> CheckBase:
    """Check setup function."""
    return CheckDockerConfig(coresys)


class CheckDockerConfig(CheckBase):
    """CheckDockerConfig class for check."""

    async def run_check(self) -> None:
        """Run check if not affected by issue."""
        self._check_docker_config()

        if self.current_issues:
            self.sys_resolution.create_issue(
                IssueType.DOCKER_CONFIG,
                ContextType.SYSTEM,
                suggestions=[SuggestionType.EXECUTE_REBUILD],
            )

    async def approve_check(self, reference: str | None = None) -> bool:
        """Approve check if it is affected by issue."""
        self._check_docker_config()
        return bool(self.current_issues)

    def _check_docker_config(self) -> None:
        """Check docker config and make issues."""
        new_issues: set[Issue] = set()

        if _check_container(self.sys_homeassistant.core.instance):
            new_issues.add(Issue(IssueType.DOCKER_CONFIG, ContextType.CORE))

        for addon in self.sys_addons.installed:
            if _check_container(addon.instance, addon):
                new_issues.add(
                    Issue(
                        IssueType.DOCKER_CONFIG, ContextType.ADDON, reference=addon.slug
                    )
                )

        for plugin in self.sys_plugins.all_plugins:
            if _check_container(plugin.instance):
                new_issues.add(
                    Issue(
                        IssueType.DOCKER_CONFIG,
                        ContextType.PLUGIN,
                        reference=plugin.slug,
                    )
                )

        # Make an issue for each container with a bad config
        for issue in new_issues - self.current_issues:
            self.sys_resolution.add_issue(
                issue, suggestions=[SuggestionType.EXECUTE_REBUILD]
            )

        # Dismiss issues when container config has been fixed
        for issue in self.current_issues - new_issues:
            self.sys_resolution.dismiss_issue(issue)

    @property
    def current_issues(self) -> set[Issue]:
        """List of current docker config issues, excluding the system one."""
        return {
            issue
            for issue in self.sys_resolution.issues
            if issue.type == IssueType.DOCKER_CONFIG and issue.context != self.context
        }

    @property
    def issue(self) -> IssueType:
        """Return a IssueType enum."""
        return IssueType.DOCKER_CONFIG

    @property
    def context(self) -> ContextType:
        """Return a ContextType enum."""
        return ContextType.SYSTEM

    @property
    def states(self) -> list[CoreState]:
        """Return a list of valid states when this check can run."""
        return [CoreState.RUNNING]
