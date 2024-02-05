"""Mock of systemd unit dbus service."""

from dbus_fast.service import PropertyAccess, dbus_property

from .base import DBusServiceMock

BUS_NAME = "org.freedesktop.systemd1"
DEFAULT_OBJECT_PATH = "/org/freedesktop/systemd1/unit/tmp_2dyellow_2emount"


def setup(object_path: str | None = None) -> DBusServiceMock:
    """Create dbus mock object."""
    return SystemdUnit(object_path or DEFAULT_OBJECT_PATH)


class SystemdUnit(DBusServiceMock):
    """Systemd Unit mock.

    gdbus introspect --system --dest org.freedesktop.systemd1 --object-path /org/freedesktop/systemd1/unit/tmp_2dyellow_2emount
    """

    interface = "org.freedesktop.systemd1.Unit"
    active_state: list[str] | str = "active"

    def __init__(self, object_path: str):
        """Initialize object."""
        super().__init__()
        self.object_path = object_path

    @dbus_property(access=PropertyAccess.READ)
    def Id(self) -> "s":
        """Get Id."""
        return "tmp-yellow.mount"

    @dbus_property(access=PropertyAccess.READ)
    def Names(self) -> "as":
        """Get Names."""
        return ["tmp-yellow.mount"]

    @dbus_property(access=PropertyAccess.READ)
    def Following(self) -> "s":
        """Get Following."""
        return ""

    @dbus_property(access=PropertyAccess.READ)
    def Requires(self) -> "as":
        """Get Requires."""
        return ["system.slice", "tmp.mount"]

    @dbus_property(access=PropertyAccess.READ)
    def Requisite(self) -> "as":
        """Get Requisite."""
        return []

    @dbus_property(access=PropertyAccess.READ)
    def Wants(self) -> "as":
        """Get Wants."""
        return ["network-online.target"]

    @dbus_property(access=PropertyAccess.READ)
    def BindsTo(self) -> "as":
        """Get BindsTo."""
        return []

    @dbus_property(access=PropertyAccess.READ)
    def PartOf(self) -> "as":
        """Get PartOf."""
        return []

    @dbus_property(access=PropertyAccess.READ)
    def Upholds(self) -> "as":
        """Get Upholds."""
        return []

    @dbus_property(access=PropertyAccess.READ)
    def RequiredBy(self) -> "as":
        """Get RequiredBy."""
        return []

    @dbus_property(access=PropertyAccess.READ)
    def RequisiteOf(self) -> "as":
        """Get RequisiteOf."""
        return []

    @dbus_property(access=PropertyAccess.READ)
    def WantedBy(self) -> "as":
        """Get WantedBy."""
        return []

    @dbus_property(access=PropertyAccess.READ)
    def BoundBy(self) -> "as":
        """Get BoundBy."""
        return []

    @dbus_property(access=PropertyAccess.READ)
    def UpheldBy(self) -> "as":
        """Get UpheldBy."""
        return []

    @dbus_property(access=PropertyAccess.READ)
    def ConsistsOf(self) -> "as":
        """Get ConsistsOf."""
        return []

    @dbus_property(access=PropertyAccess.READ)
    def Conflicts(self) -> "as":
        """Get Conflicts."""
        return ["umount.target"]

    @dbus_property(access=PropertyAccess.READ)
    def ConflictedBy(self) -> "as":
        """Get ConflictedBy."""
        return []

    @dbus_property(access=PropertyAccess.READ)
    def Before(self) -> "as":
        """Get Before."""
        return ["umount.target", "remote-fs.target"]

    @dbus_property(access=PropertyAccess.READ)
    def After(self) -> "as":
        """Get After."""
        return [
            "systemd-journald.socket",
            "system.slice",
            "remote-fs-pre.target",
            "network-online.target",
            "-.mount",
            "network.target",
            "tmp.mount",
        ]

    @dbus_property(access=PropertyAccess.READ)
    def OnSuccess(self) -> "as":
        """Get OnSuccess."""
        return []

    @dbus_property(access=PropertyAccess.READ)
    def OnSuccessOf(self) -> "as":
        """Get OnSuccessOf."""
        return []

    @dbus_property(access=PropertyAccess.READ)
    def OnFailure(self) -> "as":
        """Get OnFailure."""
        return []

    @dbus_property(access=PropertyAccess.READ)
    def OnFailureOf(self) -> "as":
        """Get OnFailureOf."""
        return []

    @dbus_property(access=PropertyAccess.READ)
    def Triggers(self) -> "as":
        """Get Triggers."""
        return []

    @dbus_property(access=PropertyAccess.READ)
    def TriggeredBy(self) -> "as":
        """Get TriggeredBy."""
        return []

    @dbus_property(access=PropertyAccess.READ)
    def PropagatesReloadTo(self) -> "as":
        """Get PropagatesReloadTo."""
        return []

    @dbus_property(access=PropertyAccess.READ)
    def ReloadPropagatedFrom(self) -> "as":
        """Get ReloadPropagatedFrom."""
        return []

    @dbus_property(access=PropertyAccess.READ)
    def PropagatesStopTo(self) -> "as":
        """Get PropagatesStopTo."""
        return []

    @dbus_property(access=PropertyAccess.READ)
    def StopPropagatedFrom(self) -> "as":
        """Get StopPropagatedFrom."""
        return []

    @dbus_property(access=PropertyAccess.READ)
    def JoinsNamespaceOf(self) -> "as":
        """Get JoinsNamespaceOf."""
        return []

    @dbus_property(access=PropertyAccess.READ)
    def SliceOf(self) -> "as":
        """Get SliceOf."""
        return []

    @dbus_property(access=PropertyAccess.READ)
    def RequiresMountsFor(self) -> "as":
        """Get RequiresMountsFor."""
        return ["/tmp"]  # noqa: S108

    @dbus_property(access=PropertyAccess.READ)
    def Documentation(self) -> "as":
        """Get Documentation."""
        return []

    @dbus_property(access=PropertyAccess.READ)
    def Description(self) -> "s":
        """Get Description."""
        return "/tmp/yellow"  # noqa: S108

    @dbus_property(access=PropertyAccess.READ)
    def AccessSELinuxContext(self) -> "s":
        """Get AccessSELinuxContext."""
        return ""

    @dbus_property(access=PropertyAccess.READ)
    def LoadState(self) -> "s":
        """Get LoadState."""
        return "loaded"

    @dbus_property(access=PropertyAccess.READ)
    def ActiveState(self) -> "s":
        """Get ActiveState."""
        if isinstance(self.active_state, list):
            return self.active_state.pop(0)
        return self.active_state

    @dbus_property(access=PropertyAccess.READ)
    def FreezerState(self) -> "s":
        """Get FreezerState."""
        return "running"

    @dbus_property(access=PropertyAccess.READ)
    def SubState(self) -> "s":
        """Get SubState."""
        return "mounted"

    @dbus_property(access=PropertyAccess.READ)
    def FragmentPath(self) -> "s":
        """Get FragmentPath."""
        return "/run/systemd/transient/tmp-yellow.mount"

    @dbus_property(access=PropertyAccess.READ)
    def SourcePath(self) -> "s":
        """Get SourcePath."""
        return ""

    @dbus_property(access=PropertyAccess.READ)
    def DropInPaths(self) -> "as":
        """Get DropInPaths."""
        return []

    @dbus_property(access=PropertyAccess.READ)
    def UnitFileState(self) -> "s":
        """Get UnitFileState."""
        return "transient"

    @dbus_property(access=PropertyAccess.READ)
    def UnitFilePreset(self) -> "s":
        """Get UnitFilePreset."""
        return "enabled"

    @dbus_property(access=PropertyAccess.READ)
    def StateChangeTimestamp(self) -> "t":
        """Get StateChangeTimestamp."""
        return 1682012447583854

    @dbus_property(access=PropertyAccess.READ)
    def StateChangeTimestampMonotonic(self) -> "t":
        """Get StateChangeTimestampMonotonic."""
        return 411597359174

    @dbus_property(access=PropertyAccess.READ)
    def InactiveExitTimestamp(self) -> "t":
        """Get InactiveExitTimestamp."""
        return 1682010434373271

    @dbus_property(access=PropertyAccess.READ)
    def InactiveExitTimestampMonotonic(self) -> "t":
        """Get InactiveExitTimestampMonotonic."""
        return 409584148592

    @dbus_property(access=PropertyAccess.READ)
    def ActiveEnterTimestamp(self) -> "t":
        """Get ActiveEnterTimestamp."""
        return 1682010434467137

    @dbus_property(access=PropertyAccess.READ)
    def ActiveEnterTimestampMonotonic(self) -> "t":
        """Get ActiveEnterTimestampMonotonic."""
        return 409584242457

    @dbus_property(access=PropertyAccess.READ)
    def ActiveExitTimestamp(self) -> "t":
        """Get ActiveExitTimestamp."""
        return 0

    @dbus_property(access=PropertyAccess.READ)
    def ActiveExitTimestampMonotonic(self) -> "t":
        """Get ActiveExitTimestampMonotonic."""
        return 0

    @dbus_property(access=PropertyAccess.READ)
    def InactiveEnterTimestamp(self) -> "t":
        """Get InactiveEnterTimestamp."""
        return 1682010285903114

    @dbus_property(access=PropertyAccess.READ)
    def InactiveEnterTimestampMonotonic(self) -> "t":
        """Get InactiveEnterTimestampMonotonic."""
        return 409435678436

    @dbus_property(access=PropertyAccess.READ)
    def CanStart(self) -> "b":
        """Get CanStart."""
        return True

    @dbus_property(access=PropertyAccess.READ)
    def CanStop(self) -> "b":
        """Get CanStop."""
        return True

    @dbus_property(access=PropertyAccess.READ)
    def CanReload(self) -> "b":
        """Get CanReload."""
        return True

    @dbus_property(access=PropertyAccess.READ)
    def CanIsolate(self) -> "b":
        """Get CanIsolate."""
        return False

    @dbus_property(access=PropertyAccess.READ)
    def CanClean(self) -> "as":
        """Get CanClean."""
        return []

    @dbus_property(access=PropertyAccess.READ)
    def CanFreeze(self) -> "b":
        """Get CanFreeze."""
        return False

    @dbus_property(access=PropertyAccess.READ)
    def Job(self) -> "(uo)":
        """Get Job."""
        return (0, "/")

    @dbus_property(access=PropertyAccess.READ)
    def StopWhenUnneeded(self) -> "b":
        """Get StopWhenUnneeded."""
        return False

    @dbus_property(access=PropertyAccess.READ)
    def RefuseManualStart(self) -> "b":
        """Get RefuseManualStart."""
        return False

    @dbus_property(access=PropertyAccess.READ)
    def RefuseManualStop(self) -> "b":
        """Get RefuseManualStop."""
        return False

    @dbus_property(access=PropertyAccess.READ)
    def AllowIsolate(self) -> "b":
        """Get AllowIsolate."""
        return False

    @dbus_property(access=PropertyAccess.READ)
    def DefaultDependencies(self) -> "b":
        """Get DefaultDependencies."""
        return True

    @dbus_property(access=PropertyAccess.READ)
    def OnSuccessJobMode(self) -> "s":
        """Get OnSuccessJobMode."""
        return "fail"

    @dbus_property(access=PropertyAccess.READ)
    def OnFailureJobMode(self) -> "s":
        """Get OnFailureJobMode."""
        return "replace"

    @dbus_property(access=PropertyAccess.READ)
    def IgnoreOnIsolate(self) -> "b":
        """Get IgnoreOnIsolate."""
        return True

    @dbus_property(access=PropertyAccess.READ)
    def NeedDaemonReload(self) -> "b":
        """Get NeedDaemonReload."""
        return False

    @dbus_property(access=PropertyAccess.READ)
    def Markers(self) -> "as":
        """Get Markers."""
        return []

    @dbus_property(access=PropertyAccess.READ)
    def JobTimeoutUSec(self) -> "t":
        """Get JobTimeoutUSec."""
        return 18446744073709551615

    @dbus_property(access=PropertyAccess.READ)
    def JobRunningTimeoutUSec(self) -> "t":
        """Get JobRunningTimeoutUSec."""
        return 18446744073709551615

    @dbus_property(access=PropertyAccess.READ)
    def JobTimeoutAction(self) -> "s":
        """Get JobTimeoutAction."""
        return "none"

    @dbus_property(access=PropertyAccess.READ)
    def JobTimeoutRebootArgument(self) -> "s":
        """Get JobTimeoutRebootArgument."""
        return ""

    @dbus_property(access=PropertyAccess.READ)
    def ConditionResult(self) -> "b":
        """Get ConditionResult."""
        return True

    @dbus_property(access=PropertyAccess.READ)
    def AssertResult(self) -> "b":
        """Get AssertResult."""
        return True

    @dbus_property(access=PropertyAccess.READ)
    def ConditionTimestamp(self) -> "t":
        """Get ConditionTimestamp."""
        return 1682010434333557

    @dbus_property(access=PropertyAccess.READ)
    def ConditionTimestampMonotonic(self) -> "t":
        """Get ConditionTimestampMonotonic."""
        return 409584108878

    @dbus_property(access=PropertyAccess.READ)
    def AssertTimestamp(self) -> "t":
        """Get AssertTimestamp."""
        return 1682010434333562

    @dbus_property(access=PropertyAccess.READ)
    def AssertTimestampMonotonic(self) -> "t":
        """Get AssertTimestampMonotonic."""
        return 409584108882

    @dbus_property(access=PropertyAccess.READ)
    def Conditions(self) -> "a(sbbsi)":
        """Get Conditions."""
        return []

    @dbus_property(access=PropertyAccess.READ)
    def Asserts(self) -> "a(sbbsi)":
        """Get Asserts."""
        return []

    @dbus_property(access=PropertyAccess.READ)
    def LoadError(self) -> "(ss)":
        """Get LoadError."""
        return ("", "")

    @dbus_property(access=PropertyAccess.READ)
    def Transient(self) -> "b":
        """Get Transient."""
        return True

    @dbus_property(access=PropertyAccess.READ)
    def Perpetual(self) -> "b":
        """Get Perpetual."""
        return False

    @dbus_property(access=PropertyAccess.READ)
    def StartLimitIntervalUSec(self) -> "t":
        """Get StartLimitIntervalUSec."""
        return 10000000

    @dbus_property(access=PropertyAccess.READ)
    def StartLimitBurst(self) -> "u":
        """Get StartLimitBurst."""
        return 5

    @dbus_property(access=PropertyAccess.READ)
    def StartLimitAction(self) -> "s":
        """Get StartLimitAction."""
        return "none"

    @dbus_property(access=PropertyAccess.READ)
    def FailureAction(self) -> "s":
        """Get FailureAction."""
        return "none"

    @dbus_property(access=PropertyAccess.READ)
    def FailureActionExitStatus(self) -> "i":
        """Get FailureActionExitStatus."""
        return -1

    @dbus_property(access=PropertyAccess.READ)
    def SuccessAction(self) -> "s":
        """Get SuccessAction."""
        return "none"

    @dbus_property(access=PropertyAccess.READ)
    def SuccessActionExitStatus(self) -> "i":
        """Get SuccessActionExitStatus."""
        return -1

    @dbus_property(access=PropertyAccess.READ)
    def RebootArgument(self) -> "s":
        """Get RebootArgument."""
        return ""

    @dbus_property(access=PropertyAccess.READ)
    def InvocationID(self) -> "ay":
        """Get InvocationID."""
        return bytes(
            [
                0xA6,
                0xE5,
                0x0F,
                0x64,
                0x3F,
                0x1E,
                0x45,
                0x97,
                0xA7,
                0x2B,
                0x21,
                0xA3,
                0x34,
                0xC0,
                0x66,
                0x86,
            ]
        )

    @dbus_property(access=PropertyAccess.READ)
    def CollectMode(self) -> "s":
        """Get CollectMode."""
        return "inactive"

    @dbus_property(access=PropertyAccess.READ)
    def Refs(self) -> "as":
        """Get Refs."""
        return []

    @dbus_property(access=PropertyAccess.READ)
    def ActivationDetails(self) -> "a(ss)":
        """Get ActivationDetails."""
        return []
