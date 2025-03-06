
import sys
from unittest.mock import patch
from supervisor.bootstrap import initialize_coresys


async def test_sentry_disabled_by_default(supervisor_name):
    """Test diagnostics off by default."""
    with (
        patch("supervisor.bootstrap.initialize_system"),
        patch("sentry_sdk.init") as sentry_init,
    ):
        await initialize_coresys()
        sentry_init.assert_not_called()