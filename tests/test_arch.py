"""Test arch object."""
from unittest.mock import patch

import pytest


@pytest.fixture(name="mock_detect_cpu", autouse=True)
def mock_detect_cpu_fixture():
    """Mock cpu detection."""
    with patch("platform.machine") as detect_mock:
        detect_mock.return_value = "Unknown"
        yield detect_mock


async def test_machine_not_exits(coresys, sys_machine, sys_supervisor):
    """Test arch for raspberrypi."""
    sys_machine.return_value = None
    sys_supervisor.arch = "amd64"
    await coresys.arch.load()

    assert coresys.arch.default == "amd64"
    assert coresys.arch.supported == ["amd64"]


async def test_machine_not_exits_in_db(coresys, sys_machine, sys_supervisor):
    """Test arch for raspberrypi."""
    sys_machine.return_value = "jedi-master-knight"
    sys_supervisor.arch = "amd64"
    await coresys.arch.load()

    assert coresys.arch.default == "amd64"
    assert coresys.arch.supported == ["amd64"]


async def test_supervisor_arch(coresys, sys_machine, sys_supervisor):
    """Test arch for raspberrypi."""
    sys_machine.return_value = None
    sys_supervisor.arch = "amd64"
    assert coresys.arch.supervisor == "amd64"

    await coresys.arch.load()

    assert coresys.arch.supervisor == "amd64"


async def test_raspberrypi_arch(coresys, sys_machine, sys_supervisor):
    """Test arch for raspberrypi."""
    sys_machine.return_value = "raspberrypi"
    sys_supervisor.arch = "armhf"
    await coresys.arch.load()

    assert coresys.arch.default == "armhf"
    assert coresys.arch.supported == ["armhf"]


async def test_raspberrypi2_arch(coresys, sys_machine, sys_supervisor):
    """Test arch for raspberrypi2."""
    sys_machine.return_value = "raspberrypi2"
    sys_supervisor.arch = "armv7"
    await coresys.arch.load()

    assert coresys.arch.default == "armv7"
    assert coresys.arch.supported == ["armv7", "armhf"]


async def test_raspberrypi3_arch(coresys, sys_machine, sys_supervisor):
    """Test arch for raspberrypi3."""
    sys_machine.return_value = "raspberrypi3"
    sys_supervisor.arch = "armv7"
    await coresys.arch.load()

    assert coresys.arch.default == "armv7"
    assert coresys.arch.supported == ["armv7", "armhf"]


async def test_raspberrypi3_64_arch(coresys, sys_machine, sys_supervisor):
    """Test arch for raspberrypi3_64."""
    sys_machine.return_value = "raspberrypi3-64"
    sys_supervisor.arch = "aarch64"
    await coresys.arch.load()

    assert coresys.arch.default == "aarch64"
    assert coresys.arch.supported == ["aarch64", "armv7", "armhf"]


async def test_raspberrypi4_arch(coresys, sys_machine, sys_supervisor):
    """Test arch for raspberrypi4."""
    sys_machine.return_value = "raspberrypi4"
    sys_supervisor.arch = "armv7"
    await coresys.arch.load()

    assert coresys.arch.default == "armv7"
    assert coresys.arch.supported == ["armv7", "armhf"]


async def test_raspberrypi4_64_arch(coresys, sys_machine, sys_supervisor):
    """Test arch for raspberrypi4_64."""
    sys_machine.return_value = "raspberrypi4-64"
    sys_supervisor.arch = "aarch64"
    await coresys.arch.load()

    assert coresys.arch.default == "aarch64"
    assert coresys.arch.supported == ["aarch64", "armv7", "armhf"]


async def test_tinker_arch(coresys, sys_machine, sys_supervisor):
    """Test arch for tinker."""
    sys_machine.return_value = "tinker"
    sys_supervisor.arch = "armv7"
    await coresys.arch.load()

    assert coresys.arch.default == "armv7"
    assert coresys.arch.supported == ["armv7", "armhf"]


async def test_odroid_c2_arch(coresys, sys_machine, sys_supervisor):
    """Test arch for odroid-c2."""
    sys_machine.return_value = "odroid-c2"
    sys_supervisor.arch = "aarch64"
    await coresys.arch.load()

    assert coresys.arch.default == "aarch64"
    assert coresys.arch.supported == ["aarch64", "armv7", "armhf"]


async def test_odroid_c4_arch(coresys, sys_machine, sys_supervisor):
    """Test arch for odroid-c4."""
    sys_machine.return_value = "odroid-c4"
    sys_supervisor.arch = "aarch64"
    await coresys.arch.load()

    assert coresys.arch.default == "aarch64"
    assert coresys.arch.supported == ["aarch64", "armv7", "armhf"]


async def test_odroid_n2_arch(coresys, sys_machine, sys_supervisor):
    """Test arch for odroid-n2."""
    sys_machine.return_value = "odroid-n2"
    sys_supervisor.arch = "aarch64"
    await coresys.arch.load()

    assert coresys.arch.default == "aarch64"
    assert coresys.arch.supported == ["aarch64", "armv7", "armhf"]


async def test_odroid_xu_arch(coresys, sys_machine, sys_supervisor):
    """Test arch for odroid-xu."""
    sys_machine.return_value = "odroid-xu"
    sys_supervisor.arch = "armv7"
    await coresys.arch.load()

    assert coresys.arch.default == "armv7"
    assert coresys.arch.supported == ["armv7", "armhf"]


async def test_intel_nuc_arch(coresys, sys_machine, sys_supervisor):
    """Test arch for intel-nuc."""
    sys_machine.return_value = "intel-nuc"
    sys_supervisor.arch = "amd64"
    await coresys.arch.load()

    assert coresys.arch.default == "amd64"
    assert coresys.arch.supported == ["amd64", "i386"]


async def test_qemux86_arch(coresys, sys_machine, sys_supervisor):
    """Test arch for qemux86."""
    sys_machine.return_value = "qemux86"
    sys_supervisor.arch = "i386"
    await coresys.arch.load()

    assert coresys.arch.default == "i386"
    assert coresys.arch.supported == ["i386"]


async def test_qemux86_64_arch(coresys, sys_machine, sys_supervisor):
    """Test arch for qemux86-64."""
    sys_machine.return_value = "qemux86-64"
    sys_supervisor.arch = "amd64"
    await coresys.arch.load()

    assert coresys.arch.default == "amd64"
    assert coresys.arch.supported == ["amd64", "i386"]


async def test_qemuarm_arch(coresys, sys_machine, sys_supervisor):
    """Test arch for qemuarm."""
    sys_machine.return_value = "qemuarm"
    sys_supervisor.arch = "armhf"
    await coresys.arch.load()

    assert coresys.arch.default == "armhf"
    assert coresys.arch.supported == ["armhf"]


async def test_qemuarm_64_arch(coresys, sys_machine, sys_supervisor):
    """Test arch for qemuarm-64."""
    sys_machine.return_value = "qemuarm-64"
    sys_supervisor.arch = "aarch64"
    await coresys.arch.load()

    assert coresys.arch.default == "aarch64"
    assert coresys.arch.supported == ["aarch64"]


async def test_qemuarm_arch_native_armv7(
    coresys, sys_machine, mock_detect_cpu, sys_supervisor
):
    """Test arch for qemuarm."""
    sys_machine.return_value = "qemuarm"
    sys_supervisor.arch = "armhf"
    mock_detect_cpu.return_value = "armv7l"
    await coresys.arch.load()

    assert coresys.arch.default == "armhf"
    assert coresys.arch.supported == ["armhf", "armv7"]
