"""Testing handling with Security."""
from unittest.mock import AsyncMock, patch

import pytest

from supervisor.coresys import CoreSys
from supervisor.exceptions import CodeNotaryError


async def test_content_trust(coresys: CoreSys):
    """Test Content-Trust."""

    with patch("supervisor.security.cas_validate", AsyncMock()) as cas_validate:
        await coresys.security.verify_content("ffffffffffffff", "test@mail.com")
        assert cas_validate.called
        cas_validate.assert_called_once_with("test@mail.com", "ffffffffffffff")

    with patch("supervisor.security.cas_validate", AsyncMock()) as cas_validate:
        await coresys.security.verify_own_content("ffffffffffffff")
        assert cas_validate.called
        cas_validate.assert_called_once_with(
            "notary@home-assistant.io", "ffffffffffffff"
        )


async def test_disabled_content_trust(coresys: CoreSys):
    """Test Content-Trust."""
    coresys.security.content_trust = False

    with patch("supervisor.security.cas_validate", AsyncMock()) as cas_validate:
        await coresys.security.verify_content("ffffffffffffff", "test@mail.com")
        assert not cas_validate.called

    with patch("supervisor.security.cas_validate", AsyncMock()) as cas_validate:
        await coresys.security.verify_own_content("ffffffffffffff")
        assert not cas_validate.called


async def test_foce_content_trust(coresys: CoreSys):
    """Force Content-Trust tests."""

    with patch(
        "supervisor.security.cas_validate", AsyncMock(side_effect=CodeNotaryError)
    ) as cas_validate:
        await coresys.security.verify_content("ffffffffffffff", "test@mail.com")
        assert cas_validate.called
        cas_validate.assert_called_once_with("test@mail.com", "ffffffffffffff")

    coresys.security.force = True

    with patch(
        "supervisor.security.cas_validate", AsyncMock(side_effect=CodeNotaryError)
    ) as cas_validate:
        with pytest.raises(CodeNotaryError):
            await coresys.security.verify_content("ffffffffffffff", "test@mail.com")
