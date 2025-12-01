"""Handle Arch for underlay maschine/platforms."""

import logging
from pathlib import Path
import platform

from .const import CpuArch
from .coresys import CoreSys, CoreSysAttributes
from .exceptions import ConfigurationFileError, HassioArchNotFound
from .utils.json import read_json_file

_LOGGER: logging.Logger = logging.getLogger(__name__)

ARCH_JSON: Path = Path(__file__).parent.joinpath("data/arch.json")

MAP_CPU: dict[str, CpuArch] = {
    "armv7": CpuArch.ARMV7,
    "armv6": CpuArch.ARMHF,
    "armv8": CpuArch.AARCH64,
    "aarch64": CpuArch.AARCH64,
    "i686": CpuArch.I386,
    "x86_64": CpuArch.AMD64,
}


class CpuArchManager(CoreSysAttributes):
    """Manage available architectures."""

    def __init__(self, coresys: CoreSys) -> None:
        """Initialize CPU Architecture handler."""
        self.coresys = coresys
        self._supported_arch: list[CpuArch] = []
        self._supported_set: set[CpuArch] = set()
        self._default_arch: CpuArch

    @property
    def default(self) -> CpuArch:
        """Return system default arch."""
        return self._default_arch

    @property
    def supervisor(self) -> CpuArch:
        """Return supervisor arch."""
        if self.sys_supervisor.arch:
            return CpuArch(self.sys_supervisor.arch)
        return self._default_arch

    @property
    def supported(self) -> list[CpuArch]:
        """Return support arch by CPU/Machine."""
        return self._supported_arch

    async def load(self) -> None:
        """Load data and initialize default arch."""
        try:
            arch_data = await self.sys_run_in_executor(read_json_file, ARCH_JSON)
        except ConfigurationFileError:
            _LOGGER.warning("Can't read arch json file from %s", ARCH_JSON)
            return

        native_support = self.detect_cpu()

        # Evaluate current CPU/Platform
        if not self.sys_machine or self.sys_machine not in arch_data:
            _LOGGER.warning("Can't detect the machine type!")
            self._default_arch = native_support
            self._supported_arch.append(self.default)
            return

        # Use configs from arch.json
        self._supported_arch.extend(CpuArch(a) for a in arch_data[self.sys_machine])
        self._default_arch = self.supported[0]

        # Make sure native support is in supported list
        if native_support not in self._supported_arch:
            self._supported_arch.append(native_support)

        self._supported_set = set(self._supported_arch)

    def is_supported(self, arch_list: list[str]) -> bool:
        """Return True if there is a supported arch by this platform."""
        return not self._supported_set.isdisjoint(arch_list)

    def match(self, arch_list: list[str]) -> CpuArch:
        """Return best match for this CPU/Platform."""
        for self_arch in self.supported:
            if self_arch in arch_list:
                return self_arch
        raise HassioArchNotFound()

    def detect_cpu(self) -> CpuArch:
        """Return the arch type of local CPU."""
        cpu = platform.machine()
        for check, value in MAP_CPU.items():
            if cpu.startswith(check):
                return value
        if self.sys_supervisor.arch:
            _LOGGER.warning(
                "Unknown CPU architecture %s, falling back to Supervisor architecture.",
                cpu,
            )
            return CpuArch(self.sys_supervisor.arch)
        _LOGGER.warning(
            "Unknown CPU architecture %s, assuming CPU architecture equals Supervisor architecture.",
            cpu,
        )
        # Return the cpu string as-is, wrapped in CpuArch (may fail if invalid)
        return CpuArch(cpu)
