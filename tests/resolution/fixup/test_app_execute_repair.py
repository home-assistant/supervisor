"""Test fixup app execute repair."""

from http import HTTPStatus
from unittest.mock import patch

import aiodocker
import pytest

from supervisor.apps.app import App
from supervisor.coresys import CoreSys
from supervisor.docker.app import DockerApp
from supervisor.docker.interface import DockerInterface
from supervisor.docker.manager import DockerAPI
from supervisor.exceptions import DockerError
from supervisor.resolution.const import ContextType, IssueType, SuggestionType
from supervisor.resolution.fixups.app_execute_repair import FixupAppExecuteRepair


async def test_fixup(docker: DockerAPI, coresys: CoreSys, install_app_ssh: App):
    """Test fixup rebuilds app's container."""
    docker.images.inspect.side_effect = aiodocker.DockerError(
        HTTPStatus.NOT_FOUND, {"message": "missing"}
    )
    install_app_ssh.data["image"] = "test_image"

    app_execute_repair = FixupAppExecuteRepair(coresys)
    assert app_execute_repair.auto is True

    coresys.resolution.create_issue(
        IssueType.MISSING_IMAGE,
        ContextType.ADDON,
        reference="local_ssh",
        suggestions=[SuggestionType.EXECUTE_REPAIR],
    )
    with patch.object(DockerInterface, "install") as install:
        await app_execute_repair()
        install.assert_called_once()

    assert not coresys.resolution.issues
    assert not coresys.resolution.suggestions


async def test_fixup_max_auto_attempts(
    docker: DockerAPI, coresys: CoreSys, install_app_ssh: App
):
    """Test fixup stops being auto-applied after 5 failures."""
    docker.images.inspect.side_effect = aiodocker.DockerError(
        HTTPStatus.NOT_FOUND, {"message": "missing"}
    )
    install_app_ssh.data["image"] = "test_image"

    app_execute_repair = FixupAppExecuteRepair(coresys)

    coresys.resolution.create_issue(
        IssueType.MISSING_IMAGE,
        ContextType.ADDON,
        reference="local_ssh",
        suggestions=[SuggestionType.EXECUTE_REPAIR],
    )
    with patch.object(DockerInterface, "install", side_effect=DockerError):
        for _ in range(5):
            assert app_execute_repair.auto is True
            with pytest.raises(DockerError):
                await app_execute_repair()

    assert app_execute_repair.auto is False


async def test_fixup_no_app(coresys: CoreSys):
    """Test fixup dismisses if app is missing."""
    app_execute_repair = FixupAppExecuteRepair(coresys)
    assert app_execute_repair.auto is True

    coresys.resolution.create_issue(
        IssueType.MISSING_IMAGE,
        ContextType.ADDON,
        reference="local_ssh",
        suggestions=[SuggestionType.EXECUTE_REPAIR],
    )

    with patch.object(DockerApp, "install") as install:
        await app_execute_repair()
        install.assert_not_called()


async def test_fixup_image_exists(
    docker: DockerAPI, coresys: CoreSys, install_app_ssh: App
):
    """Test fixup dismisses if image exists."""
    app_execute_repair = FixupAppExecuteRepair(coresys)
    assert app_execute_repair.auto is True

    coresys.resolution.create_issue(
        IssueType.MISSING_IMAGE,
        ContextType.ADDON,
        reference="local_ssh",
        suggestions=[SuggestionType.EXECUTE_REPAIR],
    )

    with patch.object(DockerApp, "install") as install:
        await app_execute_repair()
        install.assert_not_called()
