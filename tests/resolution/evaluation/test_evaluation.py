"""Test evaluation."""
# pylint: disable=import-error
from unittest.mock import patch

from supervisor.const import CoreState
from supervisor.coresys import CoreSys
from supervisor.resolution.const import UnsupportedReason


async def test_evaluation_initialize(coresys: CoreSys):
    """Test evaluation for initialize."""
    coresys.core.state = CoreState.INITIALIZE
    with patch(
        "supervisor.resolution.evaluations.dbus.EvaluateDbus.evaluate",
        return_value=False,
    ) as dbus, patch(
        "supervisor.resolution.evaluations.lxc.EvaluateLxc.evaluate",
        return_value=False,
    ) as lxc, patch(
        "supervisor.resolution.evaluations.privileged.EvaluatePrivileged.evaluate",
        return_value=False,
    ) as privileged, patch(
        "supervisor.resolution.evaluations.docker_configuration.EvaluateDockerConfiguration.evaluate",
        return_value=False,
    ) as docker_configuration, patch(
        "supervisor.resolution.evaluations.docker_version.EvaluateDockerVersion.evaluate",
        return_value=False,
    ) as docker_version:
        await coresys.resolution.evaluate.evaluate_system()
        dbus.assert_called_once()
        lxc.assert_called_once()
        privileged.assert_called_once()
        docker_configuration.assert_called_once()
        docker_version.assert_called_once()


async def test_evaluation_setup(coresys: CoreSys):
    """Test evaluation for setup."""
    coresys.core.state = CoreState.SETUP
    with patch(
        "supervisor.resolution.evaluations.operating_system.EvaluateOperatingSystem.evaluate",
        return_value=False,
    ) as operating_system, patch(
        "supervisor.resolution.evaluations.container.EvaluateContainer.evaluate",
        return_value=False,
    ) as container, patch(
        "supervisor.resolution.evaluations.network_manager.EvaluateNetworkManager.evaluate",
        return_value=False,
    ) as network_manager, patch(
        "supervisor.resolution.evaluations.systemd.EvaluateSystemd.evaluate",
        return_value=False,
    ) as systemd:
        await coresys.resolution.evaluate.evaluate_system()
        operating_system.assert_called_once()
        container.assert_called_once()
        network_manager.assert_called_once()
        systemd.assert_called_once()


async def test_evaluation_running(coresys: CoreSys):
    """Test evaluation for running."""
    coresys.core.state = CoreState.RUNNING
    with patch(
        "supervisor.resolution.evaluations.container.EvaluateContainer.evaluate",
        return_value=False,
    ) as container, patch(
        "supervisor.resolution.evaluations.network_manager.EvaluateNetworkManager.evaluate",
        return_value=False,
    ) as network_manager:
        await coresys.resolution.evaluate.evaluate_system()
        container.assert_called_once()
        network_manager.assert_called_once()


async def test_adding_and_removing_unsupported_reason(coresys: CoreSys):
    """Test adding and removing unsupported reason."""
    coresys.core.state = CoreState.RUNNING
    assert UnsupportedReason.NETWORK_MANAGER not in coresys.resolution.unsupported

    with patch(
        "supervisor.resolution.evaluations.network_manager.EvaluateNetworkManager.evaluate",
        return_value=True,
    ):
        await coresys.resolution.evaluate.evaluate_system()
        assert UnsupportedReason.NETWORK_MANAGER in coresys.resolution.unsupported
        assert not coresys.core.supported

    with patch(
        "supervisor.resolution.evaluations.network_manager.EvaluateNetworkManager.evaluate",
        return_value=False,
    ):
        await coresys.resolution.evaluate.evaluate_system()
        assert UnsupportedReason.NETWORK_MANAGER not in coresys.resolution.unsupported
        assert coresys.core.supported
