"""Test arch object."""


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


async def test_raspberrypi_arch(coresys, sys_machine):
    """Test arch for raspberrypi."""
    sys_machine.return_value = "raspberrypi"
    await coresys.arch.load()

    assert coresys.arch.default == "armhf"
    assert coresys.arch.supported == ["armhf"]


async def test_raspberrypi2_arch(coresys, sys_machine):
    """Test arch for raspberrypi2."""
    sys_machine.return_value = "raspberrypi2"
    await coresys.arch.load()

    assert coresys.arch.default == "armhf"
    assert coresys.arch.supported == ["armhf"]


async def test_raspberrypi3_arch(coresys, sys_machine):
    """Test arch for raspberrypi3."""
    sys_machine.return_value = "raspberrypi3"
    await coresys.arch.load()

    assert coresys.arch.default == "armhf"
    assert coresys.arch.supported == ["armhf"]


async def test_raspberrypi3_64_arch(coresys, sys_machine):
    """Test arch for raspberrypi3_64."""
    sys_machine.return_value = "raspberrypi3-64"
    await coresys.arch.load()

    assert coresys.arch.default == "aarch64"
    assert coresys.arch.supported == ["aarch64", "armhf"]


async def test_tinker_arch(coresys, sys_machine):
    """Test arch for tinker."""
    sys_machine.return_value = "tinker"
    await coresys.arch.load()

    assert coresys.arch.default == "armhf"
    assert coresys.arch.supported == ["armhf"]


async def test_odroid_c2_arch(coresys, sys_machine):
    """Test arch for odroid-c2."""
    sys_machine.return_value = "odroid-c2"
    await coresys.arch.load()

    assert coresys.arch.default == "aarch64"
    assert coresys.arch.supported == ["aarch64"]


async def test_odroid_xu_arch(coresys, sys_machine):
    """Test arch for odroid-xu."""
    sys_machine.return_value = "odroid-xu"
    await coresys.arch.load()

    assert coresys.arch.default == "armhf"
    assert coresys.arch.supported == ["armhf"]


async def test_orangepi_prime_arch(coresys, sys_machine):
    """Test arch for orangepi_prime."""
    sys_machine.return_value = "orangepi-prime"
    await coresys.arch.load()

    assert coresys.arch.default == "aarch64"
    assert coresys.arch.supported == ["aarch64"]


async def test_intel_nuc_arch(coresys, sys_machine):
    """Test arch for intel-nuc."""
    sys_machine.return_value = "intel-nuc"
    await coresys.arch.load()

    assert coresys.arch.default == "amd64"
    assert coresys.arch.supported == ["amd64", "i386"]


async def test_qemux86_arch(coresys, sys_machine):
    """Test arch for qemux86."""
    sys_machine.return_value = "qemux86"
    await coresys.arch.load()

    assert coresys.arch.default == "i386"
    assert coresys.arch.supported == ["i386"]


async def test_qemux86_64_arch(coresys, sys_machine):
    """Test arch for qemux86-64."""
    sys_machine.return_value = "qemux86-64"
    await coresys.arch.load()

    assert coresys.arch.default == "amd64"
    assert coresys.arch.supported == ["amd64", "i386"]


async def test_qemuarm_arch(coresys, sys_machine):
    """Test arch for qemuarm."""
    sys_machine.return_value = "qemuarm"
    await coresys.arch.load()

    assert coresys.arch.default == "armhf"
    assert coresys.arch.supported == ["armhf"]


async def test_qemuarm_64_arch(coresys, sys_machine):
    """Test arch for qemuarm-64."""
    sys_machine.return_value = "qemuarm-64"
    await coresys.arch.load()

    assert coresys.arch.default == "aarch64"
    assert coresys.arch.supported == ["aarch64"]
