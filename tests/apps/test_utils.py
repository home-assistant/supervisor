"""Test app utility functions."""

from unittest.mock import MagicMock

import pytest

from supervisor.apps.model import AppModel
from supervisor.apps.utils import rating_security
from supervisor.const import ROLE_DEFAULT, SECURITY_DEFAULT


@pytest.mark.parametrize(
    ("webui", "with_ingress", "access_auth_api", "expected"),
    [
        (None, False, False, 7),
        ("http://[HOST]:[PORT:80]", False, False, 5),
        ("http://[HOST]:[PORT:80]", False, True, 6),
        (None, True, False, 7),
    ],
)
def test_rating_security_web_interface(
    webui: str | None,
    with_ingress: bool,
    access_auth_api: bool,
    expected: int,
) -> None:
    """Test web interface security rating."""
    app = MagicMock(spec=AppModel)
    app.apparmor = SECURITY_DEFAULT
    app.webui = webui
    app.with_ingress = with_ingress
    app.access_auth_api = access_auth_api
    app.signed = False
    app.privileged = []
    app.with_kernel_modules = False
    app.hassio_role = ROLE_DEFAULT
    app.host_network = False
    app.host_pid = False
    app.host_uts = False
    app.access_docker_api = False
    app.with_full_access = False

    assert rating_security(app) == expected
