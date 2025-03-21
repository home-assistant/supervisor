"""OS support on supervisor."""

from collections.abc import Awaitable
from dataclasses import dataclass
from datetime import datetime
import errno
import logging
from pathlib import Path, PurePath

import aiohttp
from awesomeversion import AwesomeVersion, AwesomeVersionException
from cpe import CPE

from ..coresys import CoreSys, CoreSysAttributes
from ..dbus.agent.boards.const import BOARD_NAME_SUPERVISED
from ..dbus.rauc import RaucState, SlotStatusDataType
from ..exceptions import (
    DBusError,
    HassOSJobError,
    HassOSSlotNotFound,
    HassOSSlotUpdateError,
    HassOSUpdateError,
)
from ..jobs.const import JobCondition, JobExecutionLimit
from ..jobs.decorator import Job
from ..resolution.const import UnhealthyReason
from ..utils.sentry import async_capture_exception
from .data_disk import DataDisk

_LOGGER: logging.Logger = logging.getLogger(__name__)


@dataclass(slots=True, frozen=True)
class SlotStatus:
    """Status of a slot."""

    class_: str
    type_: str
    state: str
    device: PurePath
    bundle_compatible: str | None = None
    sha256: str | None = None
    size: int | None = None
    installed_count: int | None = None
    bundle_version: AwesomeVersion | None = None
    installed_timestamp: datetime | None = None
    status: str | None = None
    activated_count: int | None = None
    activated_timestamp: datetime | None = None
    boot_status: RaucState | None = None
    bootname: str | None = None
    parent: str | None = None

    @classmethod
    def from_dict(cls, data: SlotStatusDataType) -> "SlotStatus":
        """Create SlotStatus from dictionary."""
        return cls(
            class_=data["class"],
            type_=data["type"],
            state=data["state"],
            device=PurePath(data["device"]),
            bundle_compatible=data.get("bundle.compatible"),
            sha256=data.get("sha256"),
            size=data.get("size"),
            installed_count=data.get("installed.count"),
            bundle_version=AwesomeVersion(data["bundle.version"])
            if "bundle.version" in data
            else None,
            installed_timestamp=datetime.fromisoformat(data["installed.timestamp"])
            if "installed.timestamp" in data
            else None,
            status=data.get("status"),
            activated_count=data.get("activated.count"),
            activated_timestamp=datetime.fromisoformat(data["activated.timestamp"])
            if "activated.timestamp" in data
            else None,
            boot_status=data.get("boot-status"),
            bootname=data.get("bootname"),
            parent=data.get("parent"),
        )

    def to_dict(self) -> SlotStatusDataType:
        """Get dictionary representation."""
        out: SlotStatusDataType = {
            "class": self.class_,
            "type": self.type_,
            "state": self.state,
            "device": self.device.as_posix(),
        }

        if self.bundle_compatible is not None:
            out["bundle.compatible"] = self.bundle_compatible
        if self.sha256 is not None:
            out["sha256"] = self.sha256
        if self.size is not None:
            out["size"] = self.size
        if self.installed_count is not None:
            out["installed.count"] = self.installed_count
        if self.bundle_version is not None:
            out["bundle.version"] = str(self.bundle_version)
        if self.installed_timestamp is not None:
            out["installed.timestamp"] = str(self.installed_timestamp)
        if self.status is not None:
            out["status"] = self.status
        if self.activated_count is not None:
            out["activated.count"] = self.activated_count
        if self.activated_timestamp:
            out["activated.timestamp"] = str(self.activated_timestamp)
        if self.boot_status:
            out["boot-status"] = self.boot_status
        if self.bootname is not None:
            out["bootname"] = self.bootname
        if self.parent is not None:
            out["parent"] = self.parent

        return out


class OSManager(CoreSysAttributes):
    """OS interface inside supervisor."""

    def __init__(self, coresys: CoreSys):
        """Initialize HassOS handler."""
        self.coresys: CoreSys = coresys
        self._datadisk: DataDisk = DataDisk(coresys)
        self._available: bool = False
        self._version: AwesomeVersion | None = None
        self._board: str | None = None
        self._os_name: str | None = None
        self._slots: dict[str, SlotStatus] | None = None

    @property
    def available(self) -> bool:
        """Return True, if HassOS on host."""
        return self._available

    @property
    def version(self) -> AwesomeVersion | None:
        """Return version of HassOS."""
        return self._version

    @property
    def latest_version(self) -> AwesomeVersion | None:
        """Return version of HassOS."""
        return self.sys_updater.version_hassos

    @property
    def need_update(self) -> bool:
        """Return true if a HassOS update is available."""
        try:
            return self.version < self.latest_version
        except (AwesomeVersionException, TypeError):
            return False

    @property
    def board(self) -> str | None:
        """Return board name."""
        return self._board

    @property
    def os_name(self) -> str | None:
        """Return OS name."""
        return self._os_name

    @property
    def datadisk(self) -> DataDisk:
        """Return Operating-System datadisk."""
        return self._datadisk

    @property
    def slots(self) -> list[SlotStatus]:
        """Return status of slots."""
        if not self._slots:
            return []
        return list(self._slots.values())

    def get_slot_name(self, boot_name: str) -> str:
        """Get slot name from boot name."""
        for name, status in self._slots.items():
            if status.bootname == boot_name:
                return name
        raise HassOSSlotNotFound()

    def _get_download_url(self, version: AwesomeVersion) -> str:
        raw_url = self.sys_updater.ota_url
        if raw_url is None:
            raise HassOSUpdateError("Don't have an URL for OTA updates!", _LOGGER.error)

        update_board = self.board
        update_os_name = self.os_name

        # OS version 6 and later renamed intel-nuc to generic-x86-64...
        if update_board == "intel-nuc" and version >= 6.0:
            update_board = "generic-x86-64"

        # The OS name used to be hassos before renaming to haos...
        if version < 6.0:
            update_os_name = "hassos"
        else:
            update_os_name = "haos"

        url = raw_url.format(
            version=str(version), board=update_board, os_name=update_os_name
        )
        return url

    async def _download_raucb(self, url: str, raucb: Path) -> None:
        """Download rauc bundle (OTA) from URL."""
        _LOGGER.info("Fetch OTA update from %s", url)
        try:
            timeout = aiohttp.ClientTimeout(total=60 * 60, connect=180)
            async with self.sys_websession.get(url, timeout=timeout) as request:
                if request.status != 200:
                    raise HassOSUpdateError(
                        f"Error raised from OTA Webserver: {request.status}",
                        _LOGGER.error,
                    )

                # Download RAUCB file
                ota_file = await self.sys_run_in_executor(raucb.open, "wb")
                try:
                    while True:
                        chunk = await request.content.read(1_048_576)
                        if not chunk:
                            break
                        await self.sys_run_in_executor(ota_file.write, chunk)
                finally:
                    await self.sys_run_in_executor(ota_file.close)

            _LOGGER.info("Completed download of OTA update file %s", raucb)

        except (aiohttp.ClientError, TimeoutError) as err:
            self.sys_supervisor.connectivity = False
            raise HassOSUpdateError(
                f"Can't fetch OTA update from {url}: {err!s}", _LOGGER.error
            ) from err

        except OSError as err:
            if err.errno == errno.EBADMSG:
                self.sys_resolution.add_unhealthy_reason(
                    UnhealthyReason.OSERROR_BAD_MESSAGE
                )
            raise HassOSUpdateError(
                f"Can't write OTA file: {err!s}", _LOGGER.error
            ) from err

    @Job(name="os_manager_reload", conditions=[JobCondition.HAOS], internal=True)
    async def reload(self) -> None:
        """Update cache of slot statuses."""
        self._slots = {
            slot[0]: SlotStatus.from_dict(slot[1])
            for slot in await self.sys_dbus.rauc.get_slot_status()
        }

    async def load(self) -> None:
        """Load HassOS data."""
        try:
            if not self.sys_host.info.cpe:
                raise NotImplementedError()

            cpe = CPE(self.sys_host.info.cpe)
            os_name = cpe.get_product()[0]
            if os_name not in ("hassos", "haos"):
                self._board = BOARD_NAME_SUPERVISED.lower()
                raise NotImplementedError()
        except NotImplementedError:
            _LOGGER.info("No Home Assistant Operating System found")
            return

        # Store meta data
        self._available = True
        self.sys_host.supported_features.cache_clear()
        self._version = AwesomeVersion(cpe.get_version()[0])
        self._board = cpe.get_target_hardware()[0]
        self._os_name = cpe.get_product()[0]
        await self.reload()

        await self.datadisk.load()

        _LOGGER.info(
            "Detect Home Assistant Operating System %s / BootSlot %s",
            self.version,
            self.sys_dbus.rauc.boot_slot,
        )

    @Job(
        name="os_manager_config_sync",
        conditions=[JobCondition.HAOS],
        on_condition=HassOSJobError,
    )
    async def config_sync(self) -> Awaitable[None]:
        """Trigger a host config reload from usb.

        Return a coroutine.
        """
        _LOGGER.info(
            "Synchronizing configuration from USB with Home Assistant Operating System."
        )
        await self.sys_host.services.restart("hassos-config.service")

    @Job(
        name="os_manager_update",
        conditions=[
            JobCondition.HAOS,
            JobCondition.INTERNET_SYSTEM,
            JobCondition.RUNNING,
            JobCondition.SUPERVISOR_UPDATED,
        ],
        limit=JobExecutionLimit.ONCE,
        on_condition=HassOSJobError,
    )
    async def update(self, version: AwesomeVersion | None = None) -> None:
        """Update HassOS system."""
        version = version or self.latest_version

        # Check installed version
        if version == self.version:
            raise HassOSUpdateError(
                f"Version {version!s} is already installed", _LOGGER.warning
            )

        # Fetch files from internet
        ota_url = self._get_download_url(version)
        int_ota = Path(self.sys_config.path_tmp, f"hassos-{version!s}.raucb")
        await self._download_raucb(ota_url, int_ota)
        ext_ota = Path(self.sys_config.path_extern_tmp, int_ota.name)

        try:
            async with self.sys_dbus.rauc.signal_completed() as signal:
                # Start listening for signals before triggering install
                # This prevents a race condition with install complete signal

                await self.sys_dbus.rauc.install(ext_ota)
                completed = await signal.wait_for_signal()

        except DBusError as err:
            raise HassOSUpdateError("Rauc communication error", _LOGGER.error) from err

        finally:
            int_ota.unlink()

        # Update success
        if 0 in completed:
            _LOGGER.info(
                "Install of Home Assistant Operating System %s success", version
            )
            self.sys_create_task(self.sys_host.control.reboot())
            return

        # Update failed
        await self.sys_dbus.rauc.update()
        _LOGGER.error(
            "Home Assistant Operating System update failed with: %s",
            self.sys_dbus.rauc.last_error,
        )
        raise HassOSUpdateError()

    @Job(name="os_manager_mark_healthy", conditions=[JobCondition.HAOS], internal=True)
    async def mark_healthy(self) -> None:
        """Set booted partition as good for rauc."""
        try:
            responses = [
                await self.sys_dbus.rauc.mark(RaucState.ACTIVE, "booted"),
                await self.sys_dbus.rauc.mark(RaucState.GOOD, "booted"),
            ]
        except DBusError:
            _LOGGER.exception("Can't mark booted partition as healthy!")
        else:
            _LOGGER.info(
                "Rauc: slot %s - %s, %s",
                self.sys_dbus.rauc.boot_slot,
                responses[0][1],
                responses[1][1],
            )
            await self.reload()

    @Job(
        name="os_manager_set_boot_slot",
        conditions=[JobCondition.HAOS],
        on_condition=HassOSJobError,
        internal=True,
    )
    async def set_boot_slot(self, boot_name: str) -> None:
        """Set active boot slot."""
        try:
            response = await self.sys_dbus.rauc.mark(
                RaucState.ACTIVE, self.get_slot_name(boot_name)
            )
        except DBusError as err:
            await async_capture_exception(err)
            raise HassOSSlotUpdateError(
                f"Can't mark {boot_name} as active!", _LOGGER.error
            ) from err

        _LOGGER.info("Rauc: %s - %s", self.sys_dbus.rauc.boot_slot, response[1])

        _LOGGER.info("Rebooting into new boot slot now")
        await self.sys_host.control.reboot()
