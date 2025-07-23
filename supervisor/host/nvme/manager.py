"""NVME device manager."""

import asyncio
from collections.abc import Awaitable
import json
import logging
from pathlib import Path
from typing import Any

from ...exceptions import HostNvmeError
from .data import Device, NvmeList, NvmeSmartLogData

_LOGGER: logging.Logger = logging.getLogger(__name__)


class NvmeDevice:
    """Interface for NVME Device.

    Currently just provides smart log access using 'nvme smart-log <device> -o json'.
    """

    def __init__(self, path: Path, device: Device):
        """Initialize object."""
        self.id = device.host_id
        self.path = path
        self.device = device

    async def get_smart_log(self) -> NvmeSmartLogData:
        """Run smart log command and return output."""
        cmd = f"nvme smart-log {self.path.as_posix()} -o json"
        proc = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate()
        if proc.returncode != 0:
            raise HostNvmeError(
                f"Failed to run nvme smart-log: {stderr.decode().strip()}",
                _LOGGER.error,
            )
        try:
            raw = json.loads(stdout.decode())
        except json.JSONDecodeError:
            raise HostNvmeError(
                "Failed to parse nvme smart-log output", _LOGGER.error
            ) from None

        return NvmeSmartLogData.from_dict(raw)


class NvmeManager:
    """NVME Manager for machine.

    Lists available NVME devices (if any) and provides management capabilities using nvme-cli.
    """

    def __init__(self) -> None:
        """Initialize object."""
        self.devices: dict[str, NvmeDevice] = {}

    async def _list_nvme_devices(self) -> dict[str, Any]:
        """List all NVME devices on system."""
        cmd = "nvme list -o json"
        proc = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate()
        if proc.returncode != 0:
            raise HostNvmeError(f"Failed to run nvme list: {stderr.decode().strip()}")
        try:
            return json.loads(stdout.decode())
        except json.JSONDecodeError:
            raise HostNvmeError(
                "Failed to parse nvme list output", _LOGGER.error
            ) from None

    def load(self) -> Awaitable[None]:
        """Load info on NVME devices at startup."""
        return self.update()

    async def update(self) -> None:
        """Refresh info on NVME devices."""
        raw = await self._list_nvme_devices()
        self.devices = {}
        for dev in NvmeList.from_dict(raw).devices:
            if (
                dev.subsystems
                and dev.subsystems[0].controllers
                and dev.subsystems[0].controllers[0].namespaces
                and dev.subsystems[0].controllers[0].namespaces[0].name_space
            ):
                path = Path(
                    "/dev",
                    dev.subsystems[0].controllers[0].namespaces[0].name_space,
                )
                self.devices[dev.host_id] = NvmeDevice(path, dev)
            else:
                _LOGGER.info(
                    "Unusable NVME device returned in list with NQN %s and ID %s",
                    dev.host_nqn,
                    dev.host_id,
                )

    def get_by_path(self, path: Path) -> NvmeDevice | None:
        """Get NVME device by path if it exists."""
        for dev in self.devices.values():
            if dev.path == path:
                return dev
        return None
