"""Test evaluations."""

from unittest.mock import Mock, patch

from supervisor.const import CoreState
from supervisor.coresys import CoreSys
from supervisor.utils import check_exception_chain


async def test_evaluate_system_error(coresys: CoreSys, capture_exception: Mock):
    """Test error while evaluating system."""
    await coresys.core.set_state(CoreState.RUNNING)

    with patch(
        "supervisor.resolution.evaluations.source_mods.calc_checksum_path_sourcecode",
        side_effect=RuntimeError,
    ):
        await coresys.resolution.evaluate.evaluate_system()

    capture_exception.assert_called_once()
    assert check_exception_chain(capture_exception.call_args[0][0], RuntimeError)
