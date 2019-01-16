"""Common test functions."""
from unittest.mock import MagicMock

import pytest


@pytest.fixture
def coresys():
    """Create a CoreSys Mock."""
    coresys_obj = MagicMock()
    coresys_obj.sys_supervisor = MagicMock()
    coresys_obj.sys_arch = MagicMock()

    yield coresys_obj


@pytest.fixture
def sys_arch(coresys):
    """Create a CpuArch."""
    yield CpuArch(coresys)
