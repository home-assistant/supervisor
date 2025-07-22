"""NVME cli data structures."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class CriticalWarning:
    """NVME Critical Warning model."""

    value: int
    available_spare: int
    temp_threshold: int
    reliability_degraded: int
    ro: int
    vmbu_failed: int
    pmr_ro: int

    @classmethod
    def from_dict(cls: type[CriticalWarning], data: dict[str, Any]) -> CriticalWarning:
        """Create CriticalWarning from dictionary."""
        return cls(
            value=data["value"],
            available_spare=data["available_spare"],
            temp_threshold=data["temp_threshold"],
            reliability_degraded=data["reliability_degraded"],
            ro=data["ro"],
            vmbu_failed=data["vmbu_failed"],
            pmr_ro=data["pmr_ro"],
        )


@dataclass
class NvmeSmartLogData:
    """NVME Smart log model.

    Documentation on fields at https://manpages.debian.org/testing/libnvme-dev/nvme_smart_log.2.en.html.
    """

    critical_warning: int
    temperature: int
    avail_spare: int
    spare_thresh: int
    percent_used: int
    endurance_grp_critical_warning_summary: int
    data_units_read: int
    data_units_written: int
    host_read_commands: int
    host_write_commands: int
    controller_busy_time: int
    power_cycles: int
    power_on_hours: int
    unsafe_shutdowns: int
    media_errors: int
    num_err_log_entries: int
    warning_temp_time: int
    critical_comp_time: int
    # According to documentation there can be up to 8 of these, depends on the device
    # Documentation says devices should report 0 if not implemented but test device
    # only had 1 and 2 so making them optional to be safe
    temperature_sensor_1: int | None
    temperature_sensor_2: int | None
    temperature_sensor_3: int | None
    temperature_sensor_4: int | None
    temperature_sensor_5: int | None
    temperature_sensor_6: int | None
    temperature_sensor_7: int | None
    temperature_sensor_8: int | None
    thm_temp1_trans_count: int
    thm_temp2_trans_count: int
    thm_temp1_total_time: int
    thm_temp2_total_time: int

    @classmethod
    def from_dict(
        cls: type[NvmeSmartLogData], data: dict[str, Any]
    ) -> NvmeSmartLogData:
        """Create NVME Smart Log Data from dictionary."""
        return cls(
            # Critical warning seems to sometimes be a number and sometimes be a breakdown of warning types
            # For now lets simplify and just keep the warning count
            critical_warning=data["critical_warning"]
            if isinstance(data["critical_warning"], int)
            else CriticalWarning.from_dict(data["critical_warning"]).value,
            temperature=data["temperature"],
            avail_spare=data["avail_spare"],
            spare_thresh=data["spare_thresh"],
            percent_used=data["percent_used"],
            endurance_grp_critical_warning_summary=data[
                "endurance_grp_critical_warning_summary"
            ],
            data_units_read=data["data_units_read"],
            data_units_written=data["data_units_written"],
            host_read_commands=data["host_read_commands"],
            host_write_commands=data["host_write_commands"],
            controller_busy_time=data["controller_busy_time"],
            power_cycles=data["power_cycles"],
            power_on_hours=data["power_on_hours"],
            unsafe_shutdowns=data["unsafe_shutdowns"],
            media_errors=data["media_errors"],
            num_err_log_entries=data["num_err_log_entries"],
            warning_temp_time=data["warning_temp_time"],
            critical_comp_time=data["critical_comp_time"],
            temperature_sensor_1=data.get("temperature_sensor_1"),
            temperature_sensor_2=data.get("temperature_sensor_2"),
            temperature_sensor_3=data.get("temperature_sensor_3"),
            temperature_sensor_4=data.get("temperature_sensor_4"),
            temperature_sensor_5=data.get("temperature_sensor_5"),
            temperature_sensor_6=data.get("temperature_sensor_6"),
            temperature_sensor_7=data.get("temperature_sensor_7"),
            temperature_sensor_8=data.get("temperature_sensor_8"),
            thm_temp1_trans_count=data["thm_temp1_trans_count"],
            thm_temp2_trans_count=data["thm_temp2_trans_count"],
            thm_temp1_total_time=data["thm_temp1_total_time"],
            thm_temp2_total_time=data["thm_temp2_total_time"],
        )


@dataclass
class Namespace:
    """NVME namespace model."""

    name_space: str
    generic: str
    nsid: int
    used_bytes: int
    maximum_lba: int
    physical_size: int
    sector_size: int

    @classmethod
    def from_dict(cls: type[Namespace], data: dict[str, Any]) -> Namespace:
        """Create Namespace from dictionary."""
        return cls(
            name_space=data["NameSpace"],
            generic=data["Generic"],
            nsid=data["NSID"],
            used_bytes=data["UsedBytes"],
            maximum_lba=data["MaximumLBA"],
            physical_size=data["PhysicalSize"],
            sector_size=data["SectorSize"],
        )


@dataclass
class Controller:
    """NVME Controller model."""

    controller: str
    cntlid: str
    serial_number: str
    model_number: str
    firmware: str
    transport: str
    address: str
    slot: str
    namespaces: list[Namespace]
    paths: list[Any]

    @classmethod
    def from_dict(cls: type[Controller], data: dict[str, Any]) -> Controller:
        """Create Controller from dictionary."""
        return cls(
            controller=data["Controller"],
            cntlid=data["Cntlid"],
            serial_number=data["SerialNumber"],
            model_number=data["ModelNumber"],
            firmware=data["Firmware"],
            transport=data["Transport"],
            address=data["Address"],
            slot=data["Slot"],
            namespaces=[Namespace.from_dict(ns) for ns in data.get("Namespaces", [])],
            paths=data.get("Paths", []),
        )


@dataclass
class Subsystem:
    """NVME Subsystem model."""

    subsystem: str
    subsystem_nqn: str
    controllers: list[Controller]
    namespaces: list[Any]

    @classmethod
    def from_dict(cls: type[Subsystem], data: dict[str, Any]) -> Subsystem:
        """Create Subsystem from dictionary."""
        return cls(
            subsystem=data["Subsystem"],
            subsystem_nqn=data["SubsystemNQN"],
            controllers=[Controller.from_dict(c) for c in data.get("Controllers", [])],
            namespaces=list(data.get("Namespaces", [])),
        )


@dataclass
class Device:
    """NVME Device model."""

    host_nqn: str
    host_id: str
    subsystems: list[Subsystem]

    @classmethod
    def from_dict(cls: type[Device], data: dict[str, Any]) -> Device:
        """Create Device from dictionary."""
        return cls(
            host_nqn=data["HostNQN"],
            host_id=data["HostID"],
            subsystems=[Subsystem.from_dict(s) for s in data.get("Subsystems", [])],
        )


@dataclass
class NvmeList:
    """NVME List model."""

    devices: list[Device]

    @classmethod
    def from_dict(cls: type[NvmeList], data: dict[str, Any]) -> NvmeList:
        """Create NVME List from dictionary."""
        return cls(devices=[Device.from_dict(d) for d in data.get("Devices", [])])
