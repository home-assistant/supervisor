"""Test evaluation base."""
# pylint: disable=import-error
import pytest

from supervisor.coresys import CoreSys
from supervisor.resolution.evaluations.base import EvaluateBase


async def test_evaluation_base(coresys: CoreSys):
    """Test evaluation base."""
    base = EvaluateBase(coresys)
    assert not base.states

    with pytest.raises(NotImplementedError):
        await base.evaluate()

    with pytest.raises(NotImplementedError):
        assert not base.on_failure

    with pytest.raises(NotImplementedError):
        assert not base.reason
