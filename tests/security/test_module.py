"""Testing handling with Security."""

from unittest.mock import AsyncMock, patch

import pytest

from supervisor.coresys import CoreSys
from supervisor.exceptions import CodeNotaryError, CodeNotaryUntrusted
from supervisor.security.const import ContentTrustResult


async def test_content_trust(coresys: CoreSys):
    """Test Content-Trust."""

    with patch("supervisor.security.module.cas_validate", AsyncMock()) as cas_validate:
        await coresys.security.verify_content("test@mail.com", "ffffffffffffff")
        assert cas_validate.called
        cas_validate.assert_called_once_with("test@mail.com", "ffffffffffffff")

        with patch(
            "supervisor.security.module.cas_validate", AsyncMock()
        ) as cas_validate:
            await coresys.security.verify_own_content("ffffffffffffff")
            assert cas_validate.called
            cas_validate.assert_called_once_with(
                "notary@home-assistant.io", "ffffffffffffff"
            )


async def test_disabled_content_trust(coresys: CoreSys):
    """Test Content-Trust."""
    coresys.security.content_trust = False

    with patch("supervisor.security.module.cas_validate", AsyncMock()) as cas_validate:
        await coresys.security.verify_content("test@mail.com", "ffffffffffffff")
        assert not cas_validate.called

    with patch("supervisor.security.module.cas_validate", AsyncMock()) as cas_validate:
        await coresys.security.verify_own_content("ffffffffffffff")
        assert not cas_validate.called


async def test_force_content_trust(coresys: CoreSys):
    """Force Content-Trust tests."""

    with patch(
        "supervisor.security.module.cas_validate",
        AsyncMock(side_effect=CodeNotaryError),
    ) as cas_validate:
        await coresys.security.verify_content("test@mail.com", "ffffffffffffff")
        assert cas_validate.called
        cas_validate.assert_called_once_with("test@mail.com", "ffffffffffffff")

    coresys.security.force = True

    with (
        patch(
            "supervisor.security.module.cas_validate",
            AsyncMock(side_effect=CodeNotaryError),
        ) as cas_validate,
        pytest.raises(CodeNotaryError),
    ):
        await coresys.security.verify_content("test@mail.com", "ffffffffffffff")


async def test_integrity_check_disabled(coresys: CoreSys):
    """Test integrity check with disabled content trust."""
    coresys.security.content_trust = False

    result = await coresys.security.integrity_check.__wrapped__(coresys.security)

    assert result.core == ContentTrustResult.UNTESTED
    assert result.supervisor == ContentTrustResult.UNTESTED


async def test_integrity_check(coresys: CoreSys, install_addon_ssh):
    """Test integrity check with content trust."""
    coresys.homeassistant.core.check_trust = AsyncMock()
    coresys.supervisor.check_trust = AsyncMock()
    install_addon_ssh.check_trust = AsyncMock()
    install_addon_ssh.data["codenotary"] = "test@example.com"

    result = await coresys.security.integrity_check.__wrapped__(coresys.security)

    assert result.core == ContentTrustResult.PASS
    assert result.supervisor == ContentTrustResult.PASS
    assert result.addons[install_addon_ssh.slug] == ContentTrustResult.PASS


async def test_integrity_check_error(coresys: CoreSys, install_addon_ssh):
    """Test integrity check with content trust issues."""
    coresys.homeassistant.core.check_trust = AsyncMock(side_effect=CodeNotaryUntrusted)
    coresys.supervisor.check_trust = AsyncMock(side_effect=CodeNotaryUntrusted)
    install_addon_ssh.check_trust = AsyncMock(side_effect=CodeNotaryUntrusted)
    install_addon_ssh.data["codenotary"] = "test@example.com"

    result = await coresys.security.integrity_check.__wrapped__(coresys.security)

    assert result.core == ContentTrustResult.ERROR
    assert result.supervisor == ContentTrustResult.ERROR
    assert result.addons[install_addon_ssh.slug] == ContentTrustResult.ERROR


async def test_integrity_check_failed(coresys: CoreSys, install_addon_ssh):
    """Test integrity check with content trust failed."""
    coresys.homeassistant.core.check_trust = AsyncMock(side_effect=CodeNotaryError)
    coresys.supervisor.check_trust = AsyncMock(side_effect=CodeNotaryError)
    install_addon_ssh.check_trust = AsyncMock(side_effect=CodeNotaryError)
    install_addon_ssh.data["codenotary"] = "test@example.com"

    result = await coresys.security.integrity_check.__wrapped__(coresys.security)

    assert result.core == ContentTrustResult.FAILED
    assert result.supervisor == ContentTrustResult.FAILED
    assert result.addons[install_addon_ssh.slug] == ContentTrustResult.FAILED


async def test_integrity_check_addon(coresys: CoreSys, install_addon_ssh):
    """Test integrity check with content trust but no signed add-ons."""
    coresys.homeassistant.core.check_trust = AsyncMock()
    coresys.supervisor.check_trust = AsyncMock()

    result = await coresys.security.integrity_check.__wrapped__(coresys.security)

    assert result.core == ContentTrustResult.PASS
    assert result.supervisor == ContentTrustResult.PASS
    assert result.addons[install_addon_ssh.slug] == ContentTrustResult.UNTESTED
