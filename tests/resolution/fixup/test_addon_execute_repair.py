"""Test fixup addon execute repair."""

from unittest.mock import MagicMock, patch

from docker.errors import NotFound
import pytest

from supervisor.addons.addon import Addon
from supervisor.coresys import CoreSys
from supervisor.docker.addon import DockerAddon
from supervisor.docker.interface import DockerInterface
from supervisor.docker.manager import DockerAPI
from supervisor.exceptions import DockerError
from supervisor.resolution.const import ContextType, IssueType, SuggestionType
from supervisor.resolution.fixups.addon_execute_repair import FixupAddonExecuteRepair


async def test_fixup(docker: DockerAPI, coresys: CoreSys, install_addon_ssh: Addon):
    """Test fixup rebuilds addon's container."""
    docker.images.get.side_effect = NotFound("missing")
    install_addon_ssh.data["image"] = "test_image"

    addon_execute_repair = FixupAddonExecuteRepair(coresys)
    assert addon_execute_repair.auto is True

    coresys.resolution.create_issue(
        IssueType.MISSING_IMAGE,
        ContextType.ADDON,
        reference="local_ssh",
        suggestions=[SuggestionType.EXECUTE_REPAIR],
    )
    with patch.object(DockerInterface, "install") as install:
        await addon_execute_repair()
        install.assert_called_once()

    assert not coresys.resolution.issues
    assert not coresys.resolution.suggestions


async def test_fixup_max_auto_attempts(
    docker: DockerAPI, coresys: CoreSys, install_addon_ssh: Addon
):
    """Test fixup stops being auto-applied after 5 failures."""
    docker.images.get.side_effect = NotFound("missing")
    install_addon_ssh.data["image"] = "test_image"

    addon_execute_repair = FixupAddonExecuteRepair(coresys)

    coresys.resolution.create_issue(
        IssueType.MISSING_IMAGE,
        ContextType.ADDON,
        reference="local_ssh",
        suggestions=[SuggestionType.EXECUTE_REPAIR],
    )
    with patch.object(DockerInterface, "install", side_effect=DockerError):
        for _ in range(5):
            assert addon_execute_repair.auto is True
            with pytest.raises(DockerError):
                await addon_execute_repair()

    assert addon_execute_repair.auto is False


async def test_fixup_no_addon(coresys: CoreSys):
    """Test fixup dismisses if addon is missing."""
    addon_execute_repair = FixupAddonExecuteRepair(coresys)
    assert addon_execute_repair.auto is True

    coresys.resolution.create_issue(
        IssueType.MISSING_IMAGE,
        ContextType.ADDON,
        reference="local_ssh",
        suggestions=[SuggestionType.EXECUTE_REPAIR],
    )

    with patch.object(DockerAddon, "install") as install:
        await addon_execute_repair()
        install.assert_not_called()


async def test_fixup_image_exists(
    docker: DockerAPI, coresys: CoreSys, install_addon_ssh: Addon
):
    """Test fixup dismisses if image exists."""
    docker.images.get.return_value = MagicMock()

    addon_execute_repair = FixupAddonExecuteRepair(coresys)
    assert addon_execute_repair.auto is True

    coresys.resolution.create_issue(
        IssueType.MISSING_IMAGE,
        ContextType.ADDON,
        reference="local_ssh",
        suggestions=[SuggestionType.EXECUTE_REPAIR],
    )

    with patch.object(DockerAddon, "install") as install:
        await addon_execute_repair()
        install.assert_not_called()
