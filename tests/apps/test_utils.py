"""Test app utility functions."""

from pathlib import Path
import subprocess
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from supervisor.apps.model import AppModel
from supervisor.apps.utils import rating_security, remove_data
from supervisor.const import ATTR_PORTS, ROLE_DEFAULT, SECURITY_DEFAULT


@pytest.mark.parametrize(
    ("ports", "host_network", "with_ingress", "access_auth_api", "expected"),
    [
        (None, False, False, False, 7),
        ({"80/tcp": None}, False, False, False, 7),
        ({"80/tcp": 80}, False, False, False, 5),
        ({"80/tcp": 80}, False, False, True, 6),
        ({"80/tcp": 80}, False, True, False, 7),
        (None, True, False, False, 4),
    ],
)
def test_rating_security_network_exposure(
    ports: dict[str, int | None] | None,
    host_network: bool,
    with_ingress: bool,
    access_auth_api: bool,
    expected: int,
) -> None:
    """Test network exposure security rating."""
    app = MagicMock(spec=AppModel)
    app.apparmor = SECURITY_DEFAULT
    app.data = {ATTR_PORTS: ports}
    app.with_ingress = with_ingress
    app.access_auth_api = access_auth_api
    app.signed = False
    app.privileged = []
    app.with_kernel_modules = False
    app.hassio_role = ROLE_DEFAULT
    app.host_network = host_network
    app.host_pid = False
    app.host_uts = False
    app.access_docker_api = False
    app.with_full_access = False

    assert rating_security(app) == expected


def test_remove_data_process_error(
    caplog: pytest.LogCaptureFixture, tmp_path: Path
) -> None:
    """Test remove data logs the rm error output instead of raising."""

    def mock_run(args: list[str], **kwargs: Any) -> None:
        # Like subprocess.run, stderr is only captured when piped
        stderr = (
            "rm: cannot remove: Busy\n"
            if kwargs.get("stderr") == subprocess.PIPE
            else None
        )
        raise subprocess.CalledProcessError(1, args, stderr=stderr)

    with patch("supervisor.apps.utils.subprocess.run", side_effect=mock_run):
        remove_data(tmp_path)

    assert "Can't remove app data: rm: cannot remove: Busy" in caplog.text
