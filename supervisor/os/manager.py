"""OS support on supervisor."""

from dataclasses import dataclass
from datetime import datetime
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
    DBusNotConnectedError,
    HassOSError,
    HassOSJobError,
    HassOSSlotNotFound,
    HassOSSlotUpdateError,
    HassOSUpdateError,
    HostError,
)
from ..jobs.const import JobConcurrency, JobCondition
from ..jobs.decorator import Job
from ..resolution.const import ContextType, IssueType, SuggestionType
from .data_disk import DataDisk

_LOGGER: logging.Logger = logging.getLogger(__name__)

# SSH service on Home Assistant OS consuming /root/.ssh/authorized_keys
DROPBEAR_SERVICE = "dropbear.service"


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
    def from_dict(cls, data: SlotStatusDataType) -> SlotStatus:
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
            boot_status=RaucState(data["boot-status"])
            if "boot-status" in data
            else None,
            bootname=data.get("bootname"),
            parent=data.get("parent"),
        )


class OSManager(CoreSysAttributes):
    """OS interface inside supervisor."""

    def __init__(self, coresys: CoreSys):
        """Initialize HassOS handler."""
        self.coresys: CoreSys = coresys
        self._datadisk: DataDisk = DataDisk(coresys)
        self._available: bool = False
        self._version: AwesomeVersion | None = None
        self._version_pending: AwesomeVersion | None = None
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
    def latest_version_unrestricted(self) -> AwesomeVersion | None:
        """Return current latest version of HassOS for board ignoring upgrade restrictions."""
        return self.sys_updater.version_hassos_unrestricted

    @property
    def version_pending(self) -> AwesomeVersion | None:
        """Return version of an installed update that awaits a reboot to activate."""
        return self._version_pending

    @property
    def need_update(self) -> bool:
        """Return true if a HassOS update is available."""
        try:
            return (
                self.version is not None
                and self.latest_version is not None
                and self.version < self.latest_version
                and (
                    self.version_pending is None
                    or self.latest_version != self.version_pending
                )
            )
        except AwesomeVersionException, TypeError:
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
        if not self._slots:
            raise HassOSSlotNotFound

        for name, status in self._slots.items():
            if status.bootname == boot_name:
                return name
        raise HassOSSlotNotFound

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

        return raw_url.format(
            version=str(version), board=update_board, os_name=update_os_name
        )

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
            # Nudge a fresh connectivity check; the probe is authoritative,
            # this error path only hints that something may be wrong.
            self.sys_supervisor.request_connectivity_check()
            raise HassOSUpdateError(
                f"Can't fetch OTA update from {url}: {err!s}", _LOGGER.error
            ) from err

        except OSError as err:
            self.sys_resolution.check_oserror(err)
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
                raise NotImplementedError

            cpe = CPE(self.sys_host.info.cpe)
            os_name = cpe.get_product()[0]
            if os_name not in ("hassos", "haos"):
                self._board = BOARD_NAME_SUPERVISED.lower()
                raise NotImplementedError
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

    async def _detect_pending_update(self) -> None:
        """Detect an installed update that still requires a reboot to activate.

        A successful rauc install makes the target slot the primary boot slot
        while the old version keeps running until reboot. Supervisor may
        restart in that window, so recover the pending state from rauc.

        Must run after the booted slot was marked good: rauc's GRUB backend
        only treats a slot as primary once it has no boot attempts pending,
        so until the boot attempt counter of the booted slot is reset,
        GetPrimary reports the previous slot as primary on every boot.
        """
        try:
            primary = await self.sys_dbus.rauc.get_primary()
        except DBusError, DBusNotConnectedError:
            _LOGGER.warning("Can't get primary boot slot from rauc")
            return

        if (
            not self._slots
            or (status := self._slots.get(primary)) is None
            or not status.bundle_version
            or not status.bootname
        ):
            return

        # Nothing pending if the primary slot is the booted one or holds
        # the same version as the running system
        if (
            status.bootname == self.sys_dbus.rauc.boot_slot
            or status.bundle_version == self.version
        ):
            return

        self._version_pending = status.bundle_version
        _LOGGER.info(
            "Home Assistant Operating System %s is installed and pending a reboot to activate",
            status.bundle_version,
        )
        self.sys_resolution.create_issue(
            IssueType.REBOOT_REQUIRED,
            ContextType.SYSTEM,
            suggestions=[SuggestionType.EXECUTE_REBOOT],
        )

    @Job(
        name="os_manager_config_sync",
        conditions=[JobCondition.HAOS],
        on_condition=HassOSJobError,
    )
    async def config_sync(self) -> None:
        """Trigger a host config reload from usb."""
        _LOGGER.info(
            "Synchronizing configuration from USB with Home Assistant Operating System."
        )
        # hassos-config.service was renamed to haos-config.service in HAOS 18.0.
        # The unit's Alias= is not reported by systemd's ListUnits, which
        # ServiceManager.exists() relies on, so call the correct unit here.
        if self.version is not None and self.version >= AwesomeVersion("18.0.rc1"):
            service = "haos-config.service"
        else:
            service = "hassos-config.service"
        await self.sys_host.services.restart(service)

    @Job(
        name="os_manager_update",
        conditions=[
            JobCondition.HAOS,
            JobCondition.HEALTHY,
            JobCondition.INTERNET_SYSTEM,
            JobCondition.RUNNING,
            JobCondition.SUPERVISOR_UPDATED,
        ],
        on_condition=HassOSJobError,
        concurrency=JobConcurrency.REJECT,
    )
    async def update(self, version: AwesomeVersion | None = None) -> None:
        """Update HassOS system."""
        version = version or self.latest_version

        # Check installed version
        if not version:
            raise HassOSUpdateError(
                "No version information available, cannot update", _LOGGER.error
            )
        if version == self.version:
            raise HassOSUpdateError(
                f"Version {version!s} is already installed", _LOGGER.warning
            )
        if self.version_pending is not None and version == self.version_pending:
            raise HassOSUpdateError(
                f"Version {version!s} is already installed, reboot the system to activate it",
                _LOGGER.warning,
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
            await self.sys_run_in_executor(int_ota.unlink)

        # Update success
        if 0 in completed:
            _LOGGER.info(
                "Install of Home Assistant Operating System %s success; reboot required",
                version,
            )
            self._version_pending = version
            self.sys_resolution.create_issue(
                IssueType.REBOOT_REQUIRED,
                ContextType.SYSTEM,
                suggestions=[SuggestionType.EXECUTE_REBOOT],
            )
            return

        # Update failed
        await self.sys_dbus.rauc.update()
        _LOGGER.error(
            "Home Assistant Operating System update failed with: %s",
            self.sys_dbus.rauc.last_error,
        )
        # The failed install overwrote the target slot, so a previously
        # installed update pending activation is gone as well
        self._version_pending = None
        raise HassOSUpdateError

    @Job(
        name="os_manager_update_raspberrypi_firmware",
        conditions=[JobCondition.HAOS],
        on_condition=HassOSJobError,
        concurrency=JobConcurrency.REJECT,
    )
    async def update_raspberrypi_firmware(self) -> None:
        """Update Raspberry Pi firmware (and VL805 where present).

        Always raises a REBOOT_REQUIRED issue on success — the running
        bootloader is the old one until reboot, regardless of whether the
        update was flashed live (BCM2712) or staged for next boot (BCM2711).
        """
        if not self.sys_dbus.agent.board.has_rpi_firmware:
            raise HassOSJobError(
                "Raspberry Pi firmware is not available on this board",
                _LOGGER.error,
            )

        rpi = self.sys_dbus.agent.board.rpi_firmware
        if rpi.update_blocked:
            raise HassOSJobError(
                "Raspberry Pi firmware update is unavailable on this boot device",
                _LOGGER.warning,
            )

        try:
            await rpi.update_firmware()
        except DBusError as err:
            raise HassOSJobError(
                f"Raspberry Pi firmware update failed: {err}. "
                "Check the Host logs for details.",
                _LOGGER.error,
            ) from err

        _LOGGER.info("Raspberry Pi firmware update completed; reboot required")
        self.sys_resolution.create_issue(
            IssueType.REBOOT_REQUIRED,
            ContextType.SYSTEM,
            suggestions=[SuggestionType.EXECUTE_REBOOT],
        )

    @Job(name="os_manager_mark_healthy", conditions=[JobCondition.HAOS], internal=True)
    async def mark_healthy(self) -> None:
        """Set booted partition as good for rauc."""
        try:
            # Marking the booted slot good resets its boot attempt counter,
            # which the pending update detection below relies on: rauc's GRUB
            # backend only treats a slot as primary once it has no boot
            # attempts pending.
            response = await self.sys_dbus.rauc.mark(RaucState.GOOD, "booted")
        except DBusError:
            _LOGGER.exception("Can't mark booted partition as healthy!")
            return
        _LOGGER.info("Rauc: slot %s - %s", self.sys_dbus.rauc.boot_slot, response[1])

        await self.reload()
        await self._detect_pending_update()

        try:
            # Marking the booted slot as active makes it the primary boot
            # slot again, which would cancel an installed update that still
            # awaits a reboot to activate.
            if not self.version_pending:
                response = await self.sys_dbus.rauc.mark(RaucState.ACTIVE, "booted")
                await self.reload()
                _LOGGER.info(
                    "Rauc: slot %s - %s", self.sys_dbus.rauc.boot_slot, response[1]
                )
        except DBusError:
            _LOGGER.exception("Can't mark booted partition as active!")

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
            raise HassOSSlotUpdateError(
                f"Can't mark {boot_name} as active!", _LOGGER.error
            ) from err

        _LOGGER.info("Rauc: %s - %s", self.sys_dbus.rauc.boot_slot, response[1])

        _LOGGER.info("Rebooting into new boot slot now")
        await self.sys_host.control.reboot()

    @Job(
        name="os_manager_set_ssh_authorized_keys",
        conditions=[JobCondition.HAOS],
        on_condition=HassOSJobError,
        concurrency=JobConcurrency.REJECT,
        internal=True,
    )
    async def set_ssh_authorized_keys(self, keys: list[str]) -> None:
        """Replace root's SSH authorized keys on the host and start dropbear.

        OS Agent validates each key and only offers clear and append
        operations, so the replacement is not atomic: if an append is
        rejected or fails, keys added before it remain in place.
        """
        _LOGGER.info("Replacing SSH authorized keys on host (%d keys)", len(keys))
        try:
            await self.sys_dbus.agent.system.clear_ssh_auth_keys()
        except DBusError as err:
            raise HassOSError(
                f"Can't clear SSH authorized keys: {err!s}", _LOGGER.error
            ) from err

        for key in keys:
            try:
                await self.sys_dbus.agent.system.add_ssh_auth_key(key)
            except DBusError as err:
                raise HassOSError(
                    f"Can't add SSH authorized key: {err!s}", _LOGGER.error
                ) from err

        if not keys:
            return

        # dropbear on Home Assistant OS is gated by
        # ConditionFileNotEmpty=/root/.ssh/authorized_keys, which systemd only
        # evaluates when the unit starts. A running dropbear re-reads the file
        # on every authentication attempt and starting an active unit is a
        # no-op, so only the stopped service needs this.
        try:
            await self.sys_host.services.start(DROPBEAR_SERVICE)
        except (HostError, DBusError) as err:
            raise HassOSError(
                f"SSH authorized keys written, but can't start dropbear: {err!s}",
                _LOGGER.error,
            ) from err
