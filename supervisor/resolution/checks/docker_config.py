"""Helper to check if docker config for container needs an update."""

from ...const import CoreState
from ...coresys import CoreSys
from ...docker.const import PropagationMode
from ...docker.interface import DockerInterface
from ..const import ContextType, IssueType, SuggestionType
from ..data import Issue
from .base import CheckBase


def _check_container(container: DockerInterface) -> bool:
    """Return true if container has a config issue."""
    return any(
        mount.get("Propagation") != PropagationMode.SLAVE.value
        for mount in container.meta_mounts
        if mount.get("Destination") == "/media"
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
            if _check_container(addon.instance):
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
