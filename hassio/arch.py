"""Handle Arch for underlay maschine/platforms."""
import logging
from pathlib import Path
import platform
from typing import List

from .coresys import CoreSys, CoreSysAttributes
from .exceptions import HassioArchNotFound, JsonFileError
from .utils.json import read_json_file

_LOGGER = logging.getLogger(__name__)

ARCH_JSON: Path = Path(__file__).parent.joinpath("data/arch.json")

MAP_CPU = {
    "armv7": "armv7",
    "armv6": "armhf",
    "armv8": "aarch64",
    "aarch64": "aarch64",
    "i686": "i386",
    "x86_64": "amd64",
}


class CpuArch(CoreSysAttributes):
    """Manage available architectures."""

    def __init__(self, coresys: CoreSys) -> None:
        """Initialize CPU Architecture handler."""
        self.coresys = coresys
        self._supported_arch: List[str] = []
        self._default_arch: str

    @property
    def default(self) -> str:
        """Return system default arch."""
        return self._default_arch

    @property
    def supervisor(self) -> str:
        """Return supervisor arch."""
        return self.sys_supervisor.arch

    @property
    def supported(self) -> List[str]:
        """Return support arch by CPU/Machine."""
        return self._supported_arch

    async def load(self) -> None:
        """Load data and initialize default arch."""
        try:
            arch_data = read_json_file(ARCH_JSON)
        except JsonFileError:
            _LOGGER.warning("Can't read arch json")
            return

        native_support = self.detect_cpu()

        # Evaluate current CPU/Platform
        if not self.sys_machine or self.sys_machine not in arch_data:
            _LOGGER.warning("Can't detect underlay machine type!")
            self._default_arch = native_support
            self._supported_arch.append(self.default)
            return

        # Use configs from arch.json
        self._supported_arch.extend(arch_data[self.sys_machine])
        self._default_arch = self.supported[0]

        # Make sure native support is in supported list
        if native_support not in self._supported_arch:
            self._supported_arch.append(native_support)

    def is_supported(self, arch_list: List[str]) -> bool:
        """Return True if there is a supported arch by this platform."""
        return not set(self.supported).isdisjoint(set(arch_list))

    def match(self, arch_list: List[str]) -> str:
        """Return best match for this CPU/Platform."""
        for self_arch in self.supported:
            if self_arch in arch_list:
                return self_arch
        raise HassioArchNotFound()

    def detect_cpu(self) -> str:
        """Return the arch type of local CPU."""
        cpu = platform.machine()
        for check, value in MAP_CPU.items():
            if cpu.startswith(check):
                return value
        return self.sys_supervisor.arch
