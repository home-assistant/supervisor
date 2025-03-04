"""Test evaluation base."""

from unittest.mock import patch

import pytest

from supervisor.const import CoreState
from supervisor.coresys import CoreSys
from supervisor.resolution.evaluations.virtualization_image import (
    EvaluateVirtualizationImage,
)

from tests.dbus_service_mocks.base import DBusServiceMock
from tests.dbus_service_mocks.systemd import Systemd as SystemdService


async def test_evaluation(
    coresys: CoreSys,
    all_dbus_services: dict[str, DBusServiceMock | dict[str, DBusServiceMock]],
):
    """Test evaluation."""
    systemd_service: SystemdService = all_dbus_services["systemd"]
    virtualization = EvaluateVirtualizationImage(coresys)
    await coresys.core.set_state(CoreState.SETUP)

    with patch(
        "supervisor.os.manager.CPE.get_target_hardware", return_value=["generic-x86-64"]
    ):
        systemd_service.virtualization = "vmware"
        await coresys.dbus.systemd.update()

        assert not coresys.os.available
        await virtualization()
        assert virtualization.reason not in coresys.resolution.unsupported

        await coresys.os.load()
        assert coresys.os.available
        await virtualization()
        assert virtualization.reason in coresys.resolution.unsupported

        systemd_service.virtualization = ""
        await coresys.dbus.systemd.update()
        await virtualization()
        assert virtualization.reason not in coresys.resolution.unsupported


@pytest.mark.parametrize("board", ["ova", "generic-aarch64"])
async def test_evaluation_supported_images(
    coresys: CoreSys,
    all_dbus_services: dict[str, DBusServiceMock | dict[str, DBusServiceMock]],
    board: str,
):
    """Test supported images for virtualization do not trigger unsupported."""
    systemd_service: SystemdService = all_dbus_services["systemd"]
    virtualization = EvaluateVirtualizationImage(coresys)
    await coresys.core.set_state(CoreState.SETUP)

    with patch("supervisor.os.manager.CPE.get_target_hardware", return_value=[board]):
        systemd_service.virtualization = "vmware"
        await coresys.dbus.systemd.update()
        await coresys.os.load()

        await virtualization()
        assert virtualization.reason not in coresys.resolution.unsupported


async def test_did_run(coresys: CoreSys):
    """Test that the evaluation ran as expected."""
    virtualization = EvaluateVirtualizationImage(coresys)
    should_run = virtualization.states
    should_not_run = [state for state in CoreState if state not in should_run]
    assert len(should_run) != 0
    assert len(should_not_run) != 0

    with patch(
        "supervisor.resolution.evaluations.virtualization_image.EvaluateVirtualizationImage.evaluate",
        return_value=None,
    ) as evaluate:
        for state in should_run:
            await coresys.core.set_state(state)
            await virtualization()
            evaluate.assert_called_once()
            evaluate.reset_mock()

        for state in should_not_run:
            await coresys.core.set_state(state)
            await virtualization()
            evaluate.assert_not_called()
            evaluate.reset_mock()
