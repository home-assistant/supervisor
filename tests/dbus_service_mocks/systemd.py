"""Mock of systemd dbus service."""

from dbus_fast import DBusError
from dbus_fast.service import PropertyAccess, dbus_property

from .base import DBusServiceMock, dbus_method
from .systemd_unit import SystemdUnit

BUS_NAME = "org.freedesktop.systemd1"


def setup(object_path: str | None = None) -> DBusServiceMock:
    """Create dbus mock object."""
    return Systemd()


class Systemd(DBusServiceMock):
    """Systemd mock.

    gdbus introspect --system --dest org.freedesktop.systemd1 --object-path /org/freedesktop/systemd1
    """

    object_path = "/org/freedesktop/systemd1"
    interface = "org.freedesktop.systemd1.Manager"
    log_level = "info"
    log_target = "journal-or-kmsg"
    runtime_watchdog_usec = 0
    reboot_watchdog_usec = 600000000
    kexec_watchdog_usec = 0
    service_watchdogs = True
    virtualization = ""
    response_get_unit: (
        dict[str, list[str | DBusError]] | list[str | DBusError] | str | DBusError
    ) = "/org/freedesktop/systemd1/unit/tmp_2dyellow_2emount"
    response_stop_unit: str | DBusError = "/org/freedesktop/systemd1/job/7623"
    response_reload_or_restart_unit: str | DBusError = (
        "/org/freedesktop/systemd1/job/7623"
    )
    response_start_transient_unit: str | DBusError = (
        "/org/freedesktop/systemd1/job/7623"
    )
    mock_systemd_unit: SystemdUnit | None = None

    @dbus_property(access=PropertyAccess.READ)
    def Version(self) -> "s":
        """Get Version."""
        return "245.4-4ubuntu3.11"

    @dbus_property(access=PropertyAccess.READ)
    def Features(self) -> "s":
        """Get Features."""
        return "+PAM +AUDIT +SELINUX +IMA +APPARMOR +SMACK +SYSVINIT +UTMP +LIBCRYPTSETUP +GCRYPT +GNUTLS +ACL +XZ +LZ4 +SECCOMP +BLKID +ELFUTILS +KMOD +IDN2 -IDN +PCRE2 default-hierarchy=hybrid"

    @dbus_property(access=PropertyAccess.READ)
    def Virtualization(self) -> "s":
        """Get Virtualization."""
        return self.virtualization

    @dbus_property(access=PropertyAccess.READ)
    def Architecture(self) -> "s":
        """Get Architecture."""
        return "x86-64"

    @dbus_property(access=PropertyAccess.READ)
    def Tainted(self) -> "s":
        """Get Tainted."""
        return ""

    @dbus_property(access=PropertyAccess.READ)
    def FirmwareTimestamp(self) -> "t":
        """Get FirmwareTimestamp."""
        return 0

    @dbus_property(access=PropertyAccess.READ)
    def FirmwareTimestampMonotonic(self) -> "t":
        """Get FirmwareTimestampMonotonic."""
        return 28723572

    @dbus_property(access=PropertyAccess.READ)
    def LoaderTimestamp(self) -> "t":
        """Get LoaderTimestamp."""
        return 0

    @dbus_property(access=PropertyAccess.READ)
    def LoaderTimestampMonotonic(self) -> "t":
        """Get LoaderTimestampMonotonic."""
        return 12402885

    @dbus_property(access=PropertyAccess.READ)
    def KernelTimestamp(self) -> "t":
        """Get KernelTimestamp."""
        return 1632236694969442

    @dbus_property(access=PropertyAccess.READ)
    def KernelTimestampMonotonic(self) -> "t":
        """Get KernelTimestampMonotonic."""
        return 0

    @dbus_property(access=PropertyAccess.READ)
    def InitRDTimestamp(self) -> "t":
        """Get InitRDTimestamp."""
        return 0

    @dbus_property(access=PropertyAccess.READ)
    def InitRDTimestampMonotonic(self) -> "t":
        """Get InitRDTimestampMonotonic."""
        return 0

    @dbus_property(access=PropertyAccess.READ)
    def UserspaceTimestamp(self) -> "t":
        """Get UserspaceTimestamp."""
        return 1632236699147681

    @dbus_property(access=PropertyAccess.READ)
    def UserspaceTimestampMonotonic(self) -> "t":
        """Get UserspaceTimestampMonotonic."""
        return 4178239

    @dbus_property(access=PropertyAccess.READ)
    def FinishTimestamp(self) -> "t":
        """Get FinishTimestamp."""
        return 1632236713344227

    @dbus_property(access=PropertyAccess.READ)
    def FinishTimestampMonotonic(self) -> "t":
        """Get FinishTimestampMonotonic."""
        return 18374785

    @dbus_property(access=PropertyAccess.READ)
    def SecurityStartTimestamp(self) -> "t":
        """Get SecurityStartTimestamp."""
        return 1632236699156494

    @dbus_property(access=PropertyAccess.READ)
    def SecurityStartTimestampMonotonic(self) -> "t":
        """Get SecurityStartTimestampMonotonic."""
        return 4187052

    @dbus_property(access=PropertyAccess.READ)
    def SecurityFinishTimestamp(self) -> "t":
        """Get SecurityFinishTimestamp."""
        return 1632236699156980

    @dbus_property(access=PropertyAccess.READ)
    def SecurityFinishTimestampMonotonic(self) -> "t":
        """Get SecurityFinishTimestampMonotonic."""
        return 4187538

    @dbus_property(access=PropertyAccess.READ)
    def GeneratorsStartTimestamp(self) -> "t":
        """Get GeneratorsStartTimestamp."""
        return 1632236699281427

    @dbus_property(access=PropertyAccess.READ)
    def GeneratorsStartTimestampMonotonic(self) -> "t":
        """Get GeneratorsStartTimestampMonotonic."""
        return 4311984

    @dbus_property(access=PropertyAccess.READ)
    def GeneratorsFinishTimestamp(self) -> "t":
        """Get GeneratorsFinishTimestamp."""
        return 1632236699334042

    @dbus_property(access=PropertyAccess.READ)
    def GeneratorsFinishTimestampMonotonic(self) -> "t":
        """Get GeneratorsFinishTimestampMonotonic."""
        return 4364600

    @dbus_property(access=PropertyAccess.READ)
    def UnitsLoadStartTimestamp(self) -> "t":
        """Get UnitsLoadStartTimestamp."""
        return 1632236699334044

    @dbus_property(access=PropertyAccess.READ)
    def UnitsLoadStartTimestampMonotonic(self) -> "t":
        """Get UnitsLoadStartTimestampMonotonic."""
        return 4364602

    @dbus_property(access=PropertyAccess.READ)
    def UnitsLoadFinishTimestamp(self) -> "t":
        """Get UnitsLoadFinishTimestamp."""
        return 1632236699424558

    @dbus_property(access=PropertyAccess.READ)
    def UnitsLoadFinishTimestampMonotonic(self) -> "t":
        """Get UnitsLoadFinishTimestampMonotonic."""
        return 4455116

    @dbus_property(access=PropertyAccess.READ)
    def InitRDSecurityStartTimestamp(self) -> "t":
        """Get InitRDSecurityStartTimestamp."""
        return 0

    @dbus_property(access=PropertyAccess.READ)
    def InitRDSecurityStartTimestampMonotonic(self) -> "t":
        """Get InitRDSecurityStartTimestampMonotonic."""
        return 0

    @dbus_property(access=PropertyAccess.READ)
    def InitRDSecurityFinishTimestamp(self) -> "t":
        """Get InitRDSecurityFinishTimestamp."""
        return 0

    @dbus_property(access=PropertyAccess.READ)
    def InitRDSecurityFinishTimestampMonotonic(self) -> "t":
        """Get InitRDSecurityFinishTimestampMonotonic."""
        return 0

    @dbus_property(access=PropertyAccess.READ)
    def InitRDGeneratorsStartTimestamp(self) -> "t":
        """Get InitRDGeneratorsStartTimestamp."""
        return 0

    @dbus_property(access=PropertyAccess.READ)
    def InitRDGeneratorsStartTimestampMonotonic(self) -> "t":
        """Get InitRDGeneratorsStartTimestampMonotonic."""
        return 0

    @dbus_property(access=PropertyAccess.READ)
    def InitRDGeneratorsFinishTimestamp(self) -> "t":
        """Get InitRDGeneratorsFinishTimestamp."""
        return 0

    @dbus_property(access=PropertyAccess.READ)
    def InitRDGeneratorsFinishTimestampMonotonic(self) -> "t":
        """Get InitRDGeneratorsFinishTimestampMonotonic."""
        return 0

    @dbus_property(access=PropertyAccess.READ)
    def InitRDUnitsLoadStartTimestamp(self) -> "t":
        """Get InitRDUnitsLoadStartTimestamp."""
        return 0

    @dbus_property(access=PropertyAccess.READ)
    def InitRDUnitsLoadStartTimestampMonotonic(self) -> "t":
        """Get InitRDUnitsLoadStartTimestampMonotonic."""
        return 0

    @dbus_property(access=PropertyAccess.READ)
    def InitRDUnitsLoadFinishTimestamp(self) -> "t":
        """Get InitRDUnitsLoadFinishTimestamp."""
        return 0

    @dbus_property(access=PropertyAccess.READ)
    def InitRDUnitsLoadFinishTimestampMonotonic(self) -> "t":
        """Get InitRDUnitsLoadFinishTimestampMonotonic."""
        return 0

    @dbus_property()
    def LogLevel(self) -> "s":
        """Get LogLevel."""
        return self.log_level

    @LogLevel.setter
    def LogLevel(self, value: "s"):
        """Set LogLevel. Does not emit prop change."""
        self.log_level = value

    @dbus_property()
    def LogTarget(self) -> "s":
        """Get LogTarget."""
        return self.log_target

    @LogTarget.setter
    def LogTarget(self, value: "s"):
        """Set LogTarget. Does not emit prop change."""
        self.log_target = value

    @dbus_property(access=PropertyAccess.READ)
    def NNames(self) -> "u":
        """Get NNames."""
        return 564

    @dbus_property(access=PropertyAccess.READ)
    def NFailedUnits(self) -> "u":
        """Get NFailedUnits."""
        return 0

    @dbus_property(access=PropertyAccess.READ)
    def NJobs(self) -> "u":
        """Get NJobs."""
        return 0

    @dbus_property(access=PropertyAccess.READ)
    def NInstalledJobs(self) -> "u":
        """Get NInstalledJobs."""
        return 1575

    @dbus_property(access=PropertyAccess.READ)
    def NFailedJobs(self) -> "u":
        """Get NFailedJobs."""
        return 0

    @dbus_property(access=PropertyAccess.READ)
    def Progress(self) -> "d":
        """Get Progress."""
        return 1.0

    @dbus_property(access=PropertyAccess.READ)
    def Environment(self) -> "as":
        """Get Environment."""
        return [
            "LANG=en_US.UTF-8",
            "LC_ADDRESS=nb_NO.UTF-8",
            "LC_IDENTIFICATION=nb_NO.UTF-8",
            "LC_MEASUREMENT=nb_NO.UTF-8",
            "LC_MONETARY=nb_NO.UTF-8",
            "LC_NAME=nb_NO.UTF-8",
            "LC_NUMERIC=nb_NO.UTF-8",
            "LC_PAPER=nb_NO.UTF-8",
            "LC_TELEPHONE=nb_NO.UTF-8",
            "LC_TIME=nb_NO.UTF-8",
            "PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/snap/bin",
        ]

    @dbus_property(access=PropertyAccess.READ)
    def ConfirmSpawn(self) -> "b":
        """Get ConfirmSpawn."""
        return False

    @dbus_property(access=PropertyAccess.READ)
    def ShowStatus(self) -> "b":
        """Get ShowStatus."""
        return False

    @dbus_property(access=PropertyAccess.READ)
    def UnitPath(self) -> "as":
        """Get UnitPath."""
        return [
            "/etc/systemd/system.control",
            "/run/systemd/system.control",
            "/run/systemd/transient",
            "/run/systemd/generator.early",
            "/etc/systemd/system",
            "/etc/systemd/system.attached",
            "/run/systemd/system",
            "/run/systemd/system.attached",
            "/run/systemd/generator",
            "/usr/local/lib/systemd/system",
            "/lib/systemd/system",
            "/usr/lib/systemd/system",
            "/run/systemd/generator.late",
        ]

    @dbus_property(access=PropertyAccess.READ)
    def DefaultStandardOutput(self) -> "s":
        """Get DefaultStandardOutput."""
        return "journal"

    @dbus_property(access=PropertyAccess.READ)
    def DefaultStandardError(self) -> "s":
        """Get DefaultStandardError."""
        return "journal"

    @dbus_property()
    def RuntimeWatchdogUSec(self) -> "t":
        """Get RuntimeWatchdogUSec."""
        return self.runtime_watchdog_usec

    @RuntimeWatchdogUSec.setter
    def RuntimeWatchdogUSec(self, value: "t"):
        """Set RuntimeWatchdogUSec. Does not emit prop change."""
        self.runtime_watchdog_usec = value

    @dbus_property()
    def RebootWatchdogUSec(self) -> "t":
        """Get RebootWatchdogUSec."""
        return self.reboot_watchdog_usec

    @RebootWatchdogUSec.setter
    def RebootWatchdogUSec(self, value: "t"):
        """Set RebootWatchdogUSec. Does not emit prop change."""
        self.RebootWatchdogUSec = value

    @dbus_property()
    def KExecWatchdogUSec(self) -> "t":
        """Get KExecWatchdogUSec."""
        return self.kexec_watchdog_usec

    @KExecWatchdogUSec.setter
    def KExecWatchdogUSec(self, value: "t"):
        """Set KExecWatchdogUSec. Does not emit prop change."""
        self.KExecWatchdogUSec = value

    @dbus_property()
    def ServiceWatchdogs(self) -> "b":
        """Get ServiceWatchdogs."""
        return self.service_watchdogs

    @ServiceWatchdogs.setter
    def ServiceWatchdogs(self, value: "b"):
        """Set ServiceWatchdogs. Does not emit prop change."""
        self.service_watchdogs = value

    @dbus_property(access=PropertyAccess.READ)
    def ControlGroup(self) -> "s":
        """Get ControlGroup."""
        return ""

    @dbus_property(access=PropertyAccess.READ)
    def SystemState(self) -> "s":
        """Get SystemState."""
        return "running"

    @dbus_property(access=PropertyAccess.READ)
    def ExitCode(self) -> "y":
        """Get ExitCode."""
        return 0x00

    @dbus_property(access=PropertyAccess.READ)
    def DefaultTimerAccuracyUSec(self) -> "t":
        """Get DefaultTimerAccuracyUSec."""
        return 60000000

    @dbus_property(access=PropertyAccess.READ)
    def DefaultTimeoutStartUSec(self) -> "t":
        """Get DefaultTimeoutStartUSec."""
        return 90000000

    @dbus_property(access=PropertyAccess.READ)
    def DefaultTimeoutStopUSec(self) -> "t":
        """Get DefaultTimeoutStopUSec."""
        return 90000000

    @dbus_property(access=PropertyAccess.READ)
    def DefaultTimeoutAbortUSec(self) -> "t":
        """Get DefaultTimeoutAbortUSec."""
        return 90000000

    @dbus_property(access=PropertyAccess.READ)
    def DefaultRestartUSec(self) -> "t":
        """Get DefaultRestartUSec."""
        return 100000

    @dbus_property(access=PropertyAccess.READ)
    def DefaultStartLimitIntervalUSec(self) -> "t":
        """Get DefaultStartLimitIntervalUSec."""
        return 10000000

    @dbus_property(access=PropertyAccess.READ)
    def DefaultStartLimitBurst(self) -> "u":
        """Get DefaultStartLimitBurst."""
        return 5

    @dbus_property(access=PropertyAccess.READ)
    def DefaultCPUAccounting(self) -> "b":
        """Get DefaultCPUAccounting."""
        return False

    @dbus_property(access=PropertyAccess.READ)
    def DefaultBlockIOAccounting(self) -> "b":
        """Get DefaultBlockIOAccounting."""
        return False

    @dbus_property(access=PropertyAccess.READ)
    def DefaultMemoryAccounting(self) -> "b":
        """Get DefaultMemoryAccounting."""
        return True

    @dbus_property(access=PropertyAccess.READ)
    def DefaultTasksAccounting(self) -> "b":
        """Get DefaultTasksAccounting."""
        return True

    @dbus_property(access=PropertyAccess.READ)
    def DefaultLimitCPU(self) -> "t":
        """Get DefaultLimitCPU."""
        return 18446744073709551615

    @dbus_property(access=PropertyAccess.READ)
    def DefaultLimitCPUSoft(self) -> "t":
        """Get DefaultLimitCPUSoft."""
        return 18446744073709551615

    @dbus_property(access=PropertyAccess.READ)
    def DefaultLimitFSIZE(self) -> "t":
        """Get DefaultLimitFSIZE."""
        return 18446744073709551615

    @dbus_property(access=PropertyAccess.READ)
    def DefaultLimitFSIZESoft(self) -> "t":
        """Get DefaultLimitFSIZESoft."""
        return 18446744073709551615

    @dbus_property(access=PropertyAccess.READ)
    def DefaultLimitDATA(self) -> "t":
        """Get DefaultLimitDATA."""
        return 18446744073709551615

    @dbus_property(access=PropertyAccess.READ)
    def DefaultLimitDATASoft(self) -> "t":
        """Get DefaultLimitDATASoft."""
        return 18446744073709551615

    @dbus_property(access=PropertyAccess.READ)
    def DefaultLimitSTACK(self) -> "t":
        """Get DefaultLimitSTACK."""
        return 18446744073709551615

    @dbus_property(access=PropertyAccess.READ)
    def DefaultLimitSTACKSoft(self) -> "t":
        """Get DefaultLimitSTACKSoft."""
        return 8388608

    @dbus_property(access=PropertyAccess.READ)
    def DefaultLimitCORE(self) -> "t":
        """Get DefaultLimitCORE."""
        return 18446744073709551615

    @dbus_property(access=PropertyAccess.READ)
    def DefaultLimitCORESoft(self) -> "t":
        """Get DefaultLimitCORESoft."""
        return 0

    @dbus_property(access=PropertyAccess.READ)
    def DefaultLimitRSS(self) -> "t":
        """Get DefaultLimitRSS."""
        return 18446744073709551615

    @dbus_property(access=PropertyAccess.READ)
    def DefaultLimitRSSSoft(self) -> "t":
        """Get DefaultLimitRSSSoft."""
        return 18446744073709551615

    @dbus_property(access=PropertyAccess.READ)
    def DefaultLimitNOFILE(self) -> "t":
        """Get DefaultLimitNOFILE."""
        return 524288

    @dbus_property(access=PropertyAccess.READ)
    def DefaultLimitNOFILESoft(self) -> "t":
        """Get DefaultLimitNOFILESoft."""
        return 1024

    @dbus_property(access=PropertyAccess.READ)
    def DefaultLimitAS(self) -> "t":
        """Get DefaultLimitAS."""
        return 18446744073709551615

    @dbus_property(access=PropertyAccess.READ)
    def DefaultLimitASSoft(self) -> "t":
        """Get DefaultLimitASSoft."""
        return 18446744073709551615

    @dbus_property(access=PropertyAccess.READ)
    def DefaultLimitNPROC(self) -> "t":
        """Get DefaultLimitNPROC."""
        return 127764

    @dbus_property(access=PropertyAccess.READ)
    def DefaultLimitNPROCSoft(self) -> "t":
        """Get DefaultLimitNPROCSoft."""
        return 127764

    @dbus_property(access=PropertyAccess.READ)
    def DefaultLimitMEMLOCK(self) -> "t":
        """Get DefaultLimitMEMLOCK."""
        return 65536

    @dbus_property(access=PropertyAccess.READ)
    def DefaultLimitMEMLOCKSoft(self) -> "t":
        """Get DefaultLimitMEMLOCKSoft."""
        return 65536

    @dbus_property(access=PropertyAccess.READ)
    def DefaultLimitLOCKS(self) -> "t":
        """Get DefaultLimitLOCKS."""
        return 18446744073709551615

    @dbus_property(access=PropertyAccess.READ)
    def DefaultLimitLOCKSSoft(self) -> "t":
        """Get DefaultLimitLOCKSSoft."""
        return 18446744073709551615

    @dbus_property(access=PropertyAccess.READ)
    def DefaultLimitSIGPENDING(self) -> "t":
        """Get DefaultLimitSIGPENDING."""
        return 127764

    @dbus_property(access=PropertyAccess.READ)
    def DefaultLimitSIGPENDINGSoft(self) -> "t":
        """Get DefaultLimitSIGPENDINGSoft."""
        return 127764

    @dbus_property(access=PropertyAccess.READ)
    def DefaultLimitMSGQUEUE(self) -> "t":
        """Get DefaultLimitMSGQUEUE."""
        return 819200

    @dbus_property(access=PropertyAccess.READ)
    def DefaultLimitMSGQUEUESoft(self) -> "t":
        """Get DefaultLimitMSGQUEUESoft."""
        return 819200

    @dbus_property(access=PropertyAccess.READ)
    def DefaultLimitNICE(self) -> "t":
        """Get DefaultLimitNICE."""
        return 0

    @dbus_property(access=PropertyAccess.READ)
    def DefaultLimitNICESoft(self) -> "t":
        """Get DefaultLimitNICESoft."""
        return 0

    @dbus_property(access=PropertyAccess.READ)
    def DefaultLimitRTPRIO(self) -> "t":
        """Get DefaultLimitRTPRIO."""
        return 0

    @dbus_property(access=PropertyAccess.READ)
    def DefaultLimitRTPRIOSoft(self) -> "t":
        """Get DefaultLimitRTPRIOSoft."""
        return 0

    @dbus_property(access=PropertyAccess.READ)
    def DefaultLimitRTTIME(self) -> "t":
        """Get DefaultLimitRTTIME."""
        return 18446744073709551615

    @dbus_property(access=PropertyAccess.READ)
    def DefaultLimitRTTIMESoft(self) -> "t":
        """Get DefaultLimitRTTIMESoft."""
        return 18446744073709551615

    @dbus_property(access=PropertyAccess.READ)
    def DefaultTasksMax(self) -> "t":
        """Get DefaultTasksMax."""
        return 38329

    @dbus_property(access=PropertyAccess.READ)
    def TimerSlackNSec(self) -> "t":
        """Get TimerSlackNSec."""
        return 50000

    @dbus_property(access=PropertyAccess.READ)
    def DefaultOOMPolicy(self) -> "s":
        """Get DefaultOOMPolicy."""
        return "stop"

    @dbus_property(access=PropertyAccess.READ)
    def DefaultOOMScoreAdjust(self) -> "i":
        """Get DefaultOOMScoreAdjust."""
        return 0

    @dbus_property(access=PropertyAccess.READ)
    def CtrlAltDelBurstAction(self) -> "s":
        """Get CtrlAltDelBurstAction."""
        return "reboot-force"

    @dbus_method()
    def Reboot(self) -> None:
        """Reboot host computer."""

    @dbus_method()
    def PowerOff(self) -> None:
        """Power off host computer."""

    @dbus_method()
    def StartUnit(self, name: "s", mode: "s") -> "o":
        """Start a service unit."""
        if self.mock_systemd_unit:
            self.mock_systemd_unit.active_state = "active"
        return "/org/freedesktop/systemd1/job/7623"

    @dbus_method()
    def StopUnit(self, name: "s", mode: "s") -> "o":
        """Stop a service unit."""
        if isinstance(self.response_stop_unit, DBusError):
            raise self.response_stop_unit  # pylint: disable=raising-bad-type
        if self.mock_systemd_unit:
            self.mock_systemd_unit.active_state = "inactive"
        return self.response_stop_unit

    @dbus_method()
    def ReloadOrRestartUnit(self, name: "s", mode: "s") -> "o":
        """Reload or restart a service unit."""
        if isinstance(self.response_reload_or_restart_unit, DBusError):
            raise self.response_reload_or_restart_unit  # pylint: disable=raising-bad-type
        if self.mock_systemd_unit:
            self.mock_systemd_unit.active_state = "active"
        return self.response_reload_or_restart_unit

    @dbus_method()
    def RestartUnit(self, name: "s", mode: "s") -> "o":
        """Restart a service unit."""
        if self.mock_systemd_unit:
            self.mock_systemd_unit.active_state = "active"
        return "/org/freedesktop/systemd1/job/7623"

    @dbus_method()
    def StartTransientUnit(
        self, name: "s", mode: "s", properties: "a(sv)", aux: "a(sa(sv))"
    ) -> "o":
        """Start a transient service unit."""
        if isinstance(self.response_start_transient_unit, DBusError):
            raise self.response_start_transient_unit  # pylint: disable=raising-bad-type
        if self.mock_systemd_unit:
            self.mock_systemd_unit.active_state = "active"
        return self.response_start_transient_unit

    @dbus_method()
    def ResetFailedUnit(self, name: "s") -> None:
        """Reset a failed unit."""
        if self.mock_systemd_unit:
            self.mock_systemd_unit.active_state = "inactive"

    @dbus_method()
    def GetUnit(self, name: "s") -> "s":
        """Get unit."""
        if isinstance(self.response_get_unit, dict):
            unit = self.response_get_unit[name].pop(0)
        elif isinstance(self.response_get_unit, list):
            unit = self.response_get_unit.pop(0)
        else:
            unit = self.response_get_unit

        if isinstance(unit, DBusError):
            raise unit
        return unit

    @dbus_method()
    def ListUnits(
        self,
    ) -> "a(ssssssouso)":
        """Return a list of available services."""
        return [
            [
                "etc-machine\\x2did.mount",
                "/etc/machine-id",
                "loaded",
                "active",
                "mounted",
                "",
                "/org/freedesktop/systemd1/unit/etc_2dmachine_5cx2did_2emount",
                0,
                "",
                "/",
            ],
            [
                "firewalld.service",
                "firewalld.service",
                "not-found",
                "inactive",
                "dead",
                "",
                "/org/freedesktop/systemd1/unit/firewalld_2eservice",
                0,
                "",
                "/",
            ],
            [
                "sys-devices-virtual-tty-ttypd.device",
                "/sys/devices/virtual/tty/ttypd",
                "loaded",
                "active",
                "plugged",
                "",
                "/org/freedesktop/systemd1/unit/sys_2ddevices_2dvirtual_2dtty_2dttypd_2edevice",
                0,
                "",
                "/",
            ],
            [
                "zram-swap.service",
                "HassOS ZRAM swap",
                "loaded",
                "active",
                "exited",
                "",
                "/org/freedesktop/systemd1/unit/zram_2dswap_2eservice",
                0,
                "",
                "/",
            ],
        ]
