"""Handle Arch for underlay maschine/platforms."""
import json
import logging
from typing import List
from pathlib import Path

from .coresys import CoreSysAttributes, CoreSys
from .exceptions import HassioArchNotFound
from .utils.json import read_json_file

_LOGGER = logging.getLogger(__name__)


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
    def supported(self) -> List[str]:
        """Return support arch by CPU/Machine."""
        return self._supported_arch

    async def load(self) -> None:
        """Load data and initialize default arch."""
        try:
            arch_file = Path(__file__).parent.joinpath("arch.json")
            arch_data = read_json_file(arch_file)
        except (OSError, json.JSONDecodeError) as err:
            _LOGGER.warning("Can't read arch json: %s", err)
            return

        # Evaluate current CPU/Platform
        if not self.sys_machine or self.sys_machine not in arch_data:
            _LOGGER.warning("Can't detect underlay machine type!")
            self._default_arch = self.sys_supervisor.arch
            self._supported_arch.append(self.default)
            return

        # Use configs from arch.json
        self._supported_arch.extend(arch_data[self.sys_machine])
        self._default_arch = self.supported[0]

    def is_supported(self, arch_list: List[str]) -> bool:
        """Return True if there is a supported arch by this platform."""
        return not set(self.supported).isdisjoint(set(arch_list))

    def match(self, arch_list: List[str]) -> str:
        """Return best match for this CPU/Platform."""
        for self_arch in self.supported:
            if self_arch in arch_list:
                return self_arch
        raise HassioArchNotFound()
