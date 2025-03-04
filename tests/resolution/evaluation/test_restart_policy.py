"""Test evaluate restart policy.."""

from unittest.mock import MagicMock, patch

from awesomeversion import AwesomeVersion

from supervisor.addons.addon import Addon
from supervisor.const import CoreState
from supervisor.coresys import CoreSys
from supervisor.resolution.evaluations.restart_policy import EvaluateRestartPolicy

from tests.common import load_json_fixture

TEST_VERSION = AwesomeVersion("1.0.0")


async def test_evaluation(coresys: CoreSys, install_addon_ssh: Addon):
    """Test evaluation."""
    restart_policy = EvaluateRestartPolicy(coresys)
    await coresys.core.set_state(CoreState.RUNNING)

    await restart_policy()
    assert restart_policy.reason not in coresys.resolution.unsupported

    no_restart_attrs = load_json_fixture("container_attrs.json")
    always_restart_attrs = load_json_fixture("container_attrs.json")
    always_restart_attrs["HostConfig"]["RestartPolicy"]["Name"] = "always"
    addon_attrs = no_restart_attrs
    observer_attrs = always_restart_attrs

    def get_container(name: str):
        meta = MagicMock()
        meta.attrs = observer_attrs if name == "hassio_observer" else addon_attrs
        return meta

    coresys.docker.containers.get = get_container
    await coresys.plugins.observer.instance.attach(TEST_VERSION)
    await install_addon_ssh.instance.attach(TEST_VERSION)

    await restart_policy()
    assert restart_policy.reason not in coresys.resolution.unsupported

    addon_attrs = always_restart_attrs
    await install_addon_ssh.instance.attach(TEST_VERSION)
    await restart_policy()
    assert restart_policy.reason in coresys.resolution.unsupported

    addon_attrs = no_restart_attrs
    await install_addon_ssh.instance.attach(TEST_VERSION)
    await restart_policy()
    assert restart_policy.reason not in coresys.resolution.unsupported

    observer_attrs = no_restart_attrs
    await coresys.plugins.observer.instance.attach(TEST_VERSION)
    await restart_policy()
    assert restart_policy.reason in coresys.resolution.unsupported


async def test_did_run(coresys: CoreSys):
    """Test that the evaluation ran as expected."""
    restart_policy = EvaluateRestartPolicy(coresys)
    should_run = restart_policy.states
    should_not_run = [state for state in CoreState if state not in should_run]
    assert len(should_run) != 0
    assert len(should_not_run) != 0

    with patch(
        "supervisor.resolution.evaluations.restart_policy.EvaluateRestartPolicy.evaluate",
        return_value=False,
    ) as evaluate:
        for state in should_run:
            await coresys.core.set_state(state)
            await restart_policy()
            evaluate.assert_called_once()
            evaluate.reset_mock()

        for state in should_not_run:
            await coresys.core.set_state(state)
            await restart_policy()
            evaluate.assert_not_called()
            evaluate.reset_mock()
