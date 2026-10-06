"""Test security module."""

from contextlib import AbstractContextManager, nullcontext as does_not_raise
from unittest.mock import AsyncMock, patch

import pytest

from supervisor.coresys import CoreSys
from supervisor.exceptions import PwnedConnectivityError, PwnedError, PwnedSecret


@pytest.mark.parametrize(
    ("error", "force", "expectation"),
    [
        pytest.param(
            PwnedSecret,
            False,
            pytest.raises(PwnedSecret),
            id="secret-no-force",
        ),
        pytest.param(
            PwnedSecret,
            True,
            pytest.raises(PwnedSecret),
            id="secret-force",
        ),
        pytest.param(
            PwnedConnectivityError,
            False,
            does_not_raise(),
            id="connectivity-no-force",
        ),
        pytest.param(
            PwnedConnectivityError,
            True,
            pytest.raises(PwnedConnectivityError),
            id="connectivity-force",
        ),
        pytest.param(
            PwnedError,
            False,
            does_not_raise(),
            id="service-error-no-force",
        ),
        pytest.param(
            PwnedError,
            True,
            pytest.raises(PwnedError),
            id="service-error-force",
        ),
    ],
)
@pytest.mark.usefixtures("websession")
async def test_verify_secret(
    coresys: CoreSys,
    error: type[PwnedError],
    force: bool,
    expectation: AbstractContextManager,
) -> None:
    """Test verify_secret propagates pwned secrets and only swallows errors without force."""
    coresys.security.pwned = True
    coresys.security.force = force

    check = AsyncMock(side_effect=error)
    with patch("supervisor.security.module.check_pwned_password", check), expectation:
        await coresys.security.verify_secret("1234567890abcdef")

    check.assert_awaited_once()


async def test_verify_secret_disabled(coresys: CoreSys) -> None:
    """Test verify_secret skips the check when pwned is disabled."""
    coresys.security.pwned = False

    with patch(
        "supervisor.security.module.check_pwned_password",
        AsyncMock(side_effect=PwnedSecret),
    ) as check:
        await coresys.security.verify_secret("1234567890abcdef")

    check.assert_not_awaited()
