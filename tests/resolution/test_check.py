"""Test checks."""

from unittest.mock import Mock, patch

from supervisor.const import CoreState
from supervisor.coresys import CoreSys
from supervisor.resolution.checks.core_security import CheckCoreSecurity
from supervisor.utils import check_exception_chain


async def test_check_system_error(coresys: CoreSys, capture_exception: Mock):
    """Test error while checking system."""
    await coresys.core.set_state(CoreState.STARTUP)

    with (
        patch.object(CheckCoreSecurity, "run_check", side_effect=ValueError),
        patch("shutil.disk_usage", return_value=(42, 42, 2 * (1024.0**3))),
    ):
        await coresys.resolution.check.check_system()

    capture_exception.assert_called_once()
    assert check_exception_chain(capture_exception.call_args[0][0], ValueError)
