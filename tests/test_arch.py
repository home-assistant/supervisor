"""Test arch object."""

import pytest

from hassio.arch import CpuArch


async def test_machine_not_exits(coresys, sys_arch):
    """Test arch for raspberrypi."""
    coresys.sys_maschine = None
    coresys.sys_supervisor.arch = "amd64"
    await sys_arch.load()

    assert sys_arch.default == "amd64"
    assert sys_arch.supported == ["amd64"]


async def test_machine_not_exits_in_db(coresys, sys_arch):
    """Test arch for raspberrypi."""
    coresys.sys_maschine = "jedi-master-knight"
    coresys.sys_supervisor.arch = "amd64"
    await sys_arch.load()

    assert sys_arch.default == "amd64"
    assert sys_arch.supported == ["amd64"]


async def test_raspberrypi_arch(coresys, sys_arch):
    """Test arch for raspberrypi."""
    coresys.sys_maschine = "raspberrypi"
    await sys_arch.load()

    assert sys_arch.default == "armhf"
    assert sys_arch.supported == ["armhf"]


async def test_raspberrypi2_arch(coresys, sys_arch):
    """Test arch for raspberrypi2."""
    coresys.sys_maschine = "raspberrypi2"
    await sys_arch.load()

    assert sys_arch.default == "armhf"
    assert sys_arch.supported == ["armhf"]


async def test_raspberrypi3_arch(coresys, sys_arch):
    """Test arch for raspberrypi3."""
    coresys.sys_maschine = "raspberrypi3"
    await sys_arch.load()

    assert sys_arch.default == "armhf"
    assert sys_arch.supported == ["armhf"]


async def test_raspberrypi3_64_arch(coresys, sys_arch):
    """Test arch for raspberrypi3_64."""
    coresys.sys_maschine = "raspberrypi3-64"
    await sys_arch.load()

    assert sys_arch.default == "aarch64"
    assert sys_arch.supported == ["aarch64", "armhf"]


async def test_tinker_arch(coresys, sys_arch):
    """Test arch for tinker."""
    coresys.sys_maschine = "tinker"
    await sys_arch.load()

    assert sys_arch.default == "armhf"
    assert sys_arch.supported == ["armhf"]


async def test_odroid_c2_arch(coresys, sys_arch):
    """Test arch for odroid-c2."""
    coresys.sys_maschine = "odroid-c2"
    await sys_arch.load()

    assert sys_arch.default == "aarch64"
    assert sys_arch.supported == ["aarch64"]


async def test_odroid_xu_arch(coresys, sys_arch):
    """Test arch for odroid-xu."""
    coresys.sys_maschine = "odroid-xu"
    await sys_arch.load()

    assert sys_arch.default == "armhf"
    assert sys_arch.supported == ["armhf"]


async def test_orangepi_prime_arch(coresys, sys_arch):
    """Test arch for orangepi_prime."""
    coresys.sys_maschine = "orangepi-prime"
    await sys_arch.load()

    assert sys_arch.default == "aarch64"
    assert sys_arch.supported == ["aarch64"]


async def test_intel_nuc_arch(coresys, sys_arch):
    """Test arch for intel-nuc."""
    coresys.sys_maschine = "intel-nuc"
    await sys_arch.load()

    assert sys_arch.default == "amd64"
    assert sys_arch.supported == ["amd64", "i386"]


async def test_qemux86_arch(coresys, sys_arch):
    """Test arch for qemux86."""
    coresys.sys_maschine = "qemux86"
    await sys_arch.load()

    assert sys_arch.default == "i386"
    assert sys_arch.supported == ["i386"]


async def test_qemux86_64_arch(coresys, sys_arch):
    """Test arch for qemux86-64."""
    coresys.sys_maschine = "qemux86-64"
    await sys_arch.load()

    assert sys_arch.default == "amd64"
    assert sys_arch.supported == ["amd64", "i386"]


async def test_qemuarm_arch(coresys, sys_arch):
    """Test arch for qemuarm."""
    coresys.sys_maschine = "qemuarm"
    await sys_arch.load()

    assert sys_arch.default == "armhf"
    assert sys_arch.supported == ["armhf"]


async def test_qemuarm_64_arch(coresys, sys_arch):
    """Test arch for qemuarm-64."""
    coresys.sys_maschine = "qemuarm-64"
    await sys_arch.load()

    assert sys_arch.default == "aarch64"
    assert sys_arch.supported == ["aarch64"]
