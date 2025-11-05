"""Test evaluation supported system architectures."""

from unittest.mock import PropertyMock, patch

import pytest

from supervisor.const import CoreState
from supervisor.coresys import CoreSys
from supervisor.resolution.evaluations.system_architecture import (
    EvaluateSystemArchitecture,
)


@pytest.mark.parametrize("arch", ["i386", "armhf", "armv7"])
async def test_evaluation_unsupported_architectures(
    coresys: CoreSys,
    arch: str,
):
    """Test evaluation of unsupported system architectures."""
    system_architecture = EvaluateSystemArchitecture(coresys)
    await coresys.core.set_state(CoreState.INITIALIZE)

    with patch.object(
        type(coresys.supervisor), "arch", PropertyMock(return_value=arch)
    ):
        await system_architecture()
        assert system_architecture.reason in coresys.resolution.unsupported


@pytest.mark.parametrize("arch", ["amd64", "aarch64"])
async def test_evaluation_supported_architectures(
    coresys: CoreSys,
    arch: str,
):
    """Test evaluation of supported system architectures."""
    system_architecture = EvaluateSystemArchitecture(coresys)
    await coresys.core.set_state(CoreState.INITIALIZE)

    with patch.object(
        type(coresys.supervisor), "arch", PropertyMock(return_value=arch)
    ):
        await system_architecture()
        assert system_architecture.reason not in coresys.resolution.unsupported
