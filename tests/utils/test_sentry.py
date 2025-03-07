"""Unit tests for Sentry."""

from unittest.mock import patch

import pytest

from supervisor.bootstrap import initialize_coresys


@pytest.mark.usefixtures("supervisor_name", "docker")
async def test_sentry_disabled_by_default():
    """Test diagnostics off by default."""
    with (
        patch("supervisor.bootstrap.initialize_system"),
        patch("sentry_sdk.init") as sentry_init,
    ):
        await initialize_coresys()
        sentry_init.assert_not_called()
