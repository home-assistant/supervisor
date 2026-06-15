"""Test Home Assistant core."""

import asyncio
from datetime import datetime, timedelta
from http import HTTPStatus
from unittest.mock import ANY, AsyncMock, MagicMock, Mock, PropertyMock, call, patch

import aiodocker
from aiodocker.containers import DockerContainer
from awesomeversion import AwesomeVersion
import pytest
from time_machine import travel

from supervisor.const import CpuArch
from supervisor.coresys import CoreSys
from supervisor.docker.homeassistant import DockerHomeAssistant
from supervisor.docker.interface import DockerInterface
from supervisor.docker.manager import DockerAPI
from supervisor.exceptions import (
    AudioUpdateError,
    DockerError,
    HomeAssistantCrashError,
    HomeAssistantError,
    HomeAssistantJobError,
    SupervisorUpdateError,
)
from supervisor.homeassistant.api import APIState
from supervisor.homeassistant.const import LANDINGPAGE, WSEvent
from supervisor.homeassistant.core import HomeAssistantCore
from supervisor.homeassistant.module import HomeAssistant
from supervisor.resolution.const import ContextType, IssueType
from supervisor.resolution.data import Issue
from supervisor.updater import Updater

from tests.common import AsyncIterator, load_json_fixture


async def test_update_fails_if_out_of_date(coresys: CoreSys):
    """Test update of Home Assistant fails when supervisor or plugin is out of date."""
    coresys.hardware.disk.get_disk_free_space = lambda x: 5000

    with (
        patch.object(
            type(coresys.supervisor), "need_update", new=PropertyMock(return_value=True)
        ),
        pytest.raises(HomeAssistantJobError),
    ):
        await coresys.homeassistant.core.update()

    with (
        patch.object(
            type(coresys.plugins.audio),
            "need_update",
            new=PropertyMock(return_value=True),
        ),
        patch.object(
            type(coresys.plugins.audio), "update", side_effect=AudioUpdateError
        ),
        pytest.raises(HomeAssistantJobError),
    ):
        await coresys.homeassistant.core.update()


async def test_install_landingpage_docker_ratelimit_error(
    coresys: CoreSys, capture_exception: Mock, caplog: pytest.LogCaptureFixture
):
    """Test install landing page fails due to docker ratelimit error."""
    coresys.security.force = True
    coresys.docker.images.pull.side_effect = [
        aiodocker.DockerError(HTTPStatus.TOO_MANY_REQUESTS, {"message": "ratelimit"}),
        AsyncIterator([{}]),
    ]

    with (
        patch.object(DockerHomeAssistant, "attach", side_effect=DockerError),
        patch.object(
            Updater,
            "image_homeassistant",
            new=PropertyMock(return_value="homeassistant"),
        ),
        patch.object(
            DockerInterface, "arch", new=PropertyMock(return_value=CpuArch.AMD64)
        ),
        patch("supervisor.homeassistant.core.asyncio.sleep") as sleep,
    ):
        await coresys.homeassistant.core.install_landingpage()
        sleep.assert_awaited_once_with(30)

    assert "Failed to install landingpage, retrying after 30sec" in caplog.text
    capture_exception.assert_not_called()
    assert (
        Issue(IssueType.DOCKER_RATELIMIT, ContextType.SYSTEM)
        in coresys.resolution.issues
    )
    assert "Unhandled exception:" not in caplog.text


@pytest.mark.parametrize(
    "err",
    [
        aiodocker.DockerError(HTTPStatus.INTERNAL_SERVER_ERROR, {"message": "fail"}),
        aiodocker.DockerError(HTTPStatus.NOT_FOUND, {"message": "missing"}),
    ],
)
async def test_install_landingpage_other_error(
    coresys: CoreSys,
    capture_exception: Mock,
    caplog: pytest.LogCaptureFixture,
    err: aiodocker.DockerError,
):
    """Test install landing page fails due to other error."""
    coresys.docker.images.inspect.side_effect = [err, MagicMock()]

    with (
        patch.object(DockerHomeAssistant, "attach", side_effect=DockerError),
        patch.object(
            Updater,
            "image_homeassistant",
            new=PropertyMock(return_value="homeassistant"),
        ),
        patch.object(
            DockerInterface, "arch", new=PropertyMock(return_value=CpuArch.AMD64)
        ),
        patch("supervisor.homeassistant.core.asyncio.sleep") as sleep,
    ):
        await coresys.homeassistant.core.install_landingpage()
        sleep.assert_awaited_once_with(30)

    assert "Failed to install landingpage, retrying after 30sec" in caplog.text
    capture_exception.assert_called_once_with(err)
    assert "Unhandled exception:" not in caplog.text


async def test_install_docker_ratelimit_error(
    coresys: CoreSys, capture_exception: Mock, caplog: pytest.LogCaptureFixture
):
    """Test install fails due to docker ratelimit error."""
    coresys.security.force = True
    coresys.docker.images.pull.side_effect = [
        aiodocker.DockerError(HTTPStatus.TOO_MANY_REQUESTS, {"message": "ratelimit"}),
        AsyncIterator([{}]),
    ]

    with (
        patch.object(HomeAssistantCore, "start"),
        patch.object(DockerHomeAssistant, "cleanup"),
        patch.object(
            Updater,
            "image_homeassistant",
            new=PropertyMock(return_value="homeassistant"),
        ),
        patch.object(
            Updater, "version_homeassistant", new=PropertyMock(return_value="2022.7.3")
        ),
        patch.object(
            DockerInterface, "arch", new=PropertyMock(return_value=CpuArch.AMD64)
        ),
        patch("supervisor.homeassistant.core.asyncio.sleep") as sleep,
    ):
        await coresys.homeassistant.core.install()
        sleep.assert_awaited_once_with(30)

    assert "Error on Home Assistant installation. Retrying in 30sec" in caplog.text
    capture_exception.assert_not_called()
    assert (
        Issue(IssueType.DOCKER_RATELIMIT, ContextType.SYSTEM)
        in coresys.resolution.issues
    )
    assert "Unhandled exception:" not in caplog.text


@pytest.mark.parametrize(
    "err",
    [
        aiodocker.DockerError(HTTPStatus.INTERNAL_SERVER_ERROR, {"message": "fail"}),
        aiodocker.DockerError(HTTPStatus.NOT_FOUND, {"message": "missing"}),
    ],
)
async def test_install_other_error(
    coresys: CoreSys,
    capture_exception: Mock,
    caplog: pytest.LogCaptureFixture,
    err: aiodocker.DockerError,
):
    """Test install fails due to other error."""
    coresys.docker.images.inspect.side_effect = [err, MagicMock()]

    with (
        patch.object(HomeAssistantCore, "start"),
        patch.object(DockerHomeAssistant, "cleanup"),
        patch.object(
            Updater,
            "image_homeassistant",
            new=PropertyMock(return_value="homeassistant"),
        ),
        patch.object(
            Updater, "version_homeassistant", new=PropertyMock(return_value="2022.7.3")
        ),
        patch.object(
            DockerInterface, "arch", new=PropertyMock(return_value=CpuArch.AMD64)
        ),
        patch("supervisor.homeassistant.core.asyncio.sleep") as sleep,
    ):
        await coresys.homeassistant.core.install()
        sleep.assert_awaited_once_with(30)

    assert "Error on Home Assistant installation. Retrying in 30sec" in caplog.text
    capture_exception.assert_called_once_with(err)
    assert "Unhandled exception:" not in caplog.text


async def test_install_supervisor_needs_update_auto_update_enabled(
    coresys: CoreSys, caplog: pytest.LogCaptureFixture
):
    """Test install proceeds with supervisor update first when auto-update is enabled."""
    with (
        patch.object(HomeAssistantCore, "start"),
        patch.object(DockerHomeAssistant, "cleanup"),
        patch.object(
            Updater,
            "image_homeassistant",
            new=PropertyMock(return_value="homeassistant"),
        ),
        patch.object(
            Updater, "version_homeassistant", new=PropertyMock(return_value="2022.7.3")
        ),
        patch.object(
            DockerInterface, "arch", new=PropertyMock(return_value=CpuArch.AMD64)
        ),
        patch.object(
            type(coresys.supervisor), "need_update", new=PropertyMock(return_value=True)
        ),
        patch.object(
            type(coresys.updater), "auto_update", new=PropertyMock(return_value=True)
        ),
        patch.object(coresys.supervisor, "update") as supervisor_update,
        patch("supervisor.homeassistant.core.asyncio.sleep"),
    ):
        await coresys.homeassistant.core.install()
        supervisor_update.assert_awaited_once()

    assert (
        "Supervisor has a pending update and must be updated before installing Home Assistant Core"
        in caplog.text
    )


async def test_install_supervisor_needs_update_auto_update_disabled(
    coresys: CoreSys, caplog: pytest.LogCaptureFixture
):
    """Test install proceeds with core anyway when supervisor needs update but auto-update is disabled."""
    with (
        patch.object(HomeAssistantCore, "start"),
        patch.object(DockerHomeAssistant, "cleanup"),
        patch.object(
            Updater,
            "image_homeassistant",
            new=PropertyMock(return_value="homeassistant"),
        ),
        patch.object(
            Updater, "version_homeassistant", new=PropertyMock(return_value="2022.7.3")
        ),
        patch.object(
            DockerInterface, "arch", new=PropertyMock(return_value=CpuArch.AMD64)
        ),
        patch.object(
            type(coresys.supervisor), "need_update", new=PropertyMock(return_value=True)
        ),
        patch.object(
            type(coresys.updater), "auto_update", new=PropertyMock(return_value=False)
        ),
        patch.object(coresys.supervisor, "update") as supervisor_update,
        patch("supervisor.homeassistant.core.asyncio.sleep"),
    ):
        await coresys.homeassistant.core.install()
        supervisor_update.assert_not_called()

    assert "Supervisor has a pending update but auto-update is disabled" in caplog.text
    assert "unknown issues may occur" in caplog.text


async def test_install_supervisor_update_fails_retries(
    coresys: CoreSys, caplog: pytest.LogCaptureFixture
):
    """Test install retries after 30s when supervisor update fails."""
    # Supervisor reports needing update on first pass, not on second
    need_update_values = [True, False]
    need_update_mock = PropertyMock(side_effect=need_update_values)

    with (
        patch.object(HomeAssistantCore, "start"),
        patch.object(DockerHomeAssistant, "cleanup"),
        patch.object(
            Updater,
            "image_homeassistant",
            new=PropertyMock(return_value="homeassistant"),
        ),
        patch.object(
            Updater, "version_homeassistant", new=PropertyMock(return_value="2022.7.3")
        ),
        patch.object(
            DockerInterface, "arch", new=PropertyMock(return_value=CpuArch.AMD64)
        ),
        patch.object(type(coresys.supervisor), "need_update", new=need_update_mock),
        patch.object(
            type(coresys.updater), "auto_update", new=PropertyMock(return_value=True)
        ),
        patch.object(
            coresys.supervisor,
            "update",
            side_effect=SupervisorUpdateError("update failed"),
        ),
        patch("supervisor.homeassistant.core.asyncio.sleep") as sleep,
    ):
        await coresys.homeassistant.core.install()
        sleep.assert_any_await(30)

    assert "Supervisor update failed, retrying in 30sec" in caplog.text


@pytest.mark.parametrize(
    ("active_job", "expected_log"),
    [
        (None, "Home Assistant Core installation in progress"),
        (MagicMock(progress=45.0), "Downloading Home Assistant Core image, 45%"),
    ],
)
async def test_install_logs_progress_periodically(
    coresys: CoreSys,
    caplog: pytest.LogCaptureFixture,
    active_job: MagicMock | None,
    expected_log: str,
):
    """Test install logs progress periodically during image pull."""
    coresys.security.force = True
    coresys.docker.images.pull.return_value = AsyncIterator([{}])
    original_wait_for = asyncio.wait_for

    async def mock_wait_for(coro, *, timeout=None):
        """Immediately timeout for the progress log wait, pass through others."""
        if timeout == 15:
            coro.close()
            await asyncio.sleep(0)
            raise TimeoutError
        return await original_wait_for(coro, timeout=timeout)

    with (
        patch.object(HomeAssistantCore, "start"),
        patch.object(DockerHomeAssistant, "cleanup"),
        patch.object(
            Updater,
            "image_homeassistant",
            new=PropertyMock(return_value="homeassistant"),
        ),
        patch.object(
            Updater, "version_homeassistant", new=PropertyMock(return_value="2022.7.3")
        ),
        patch.object(
            DockerInterface, "arch", new=PropertyMock(return_value=CpuArch.AMD64)
        ),
        patch("supervisor.homeassistant.core.asyncio.wait_for", new=mock_wait_for),
        patch.object(
            DockerHomeAssistant,
            "active_job",
            new=PropertyMock(return_value=active_job),
        ),
    ):
        await coresys.homeassistant.core.install()

    assert expected_log in caplog.text


async def test_install_exposes_core_install_job_with_progress(
    coresys: CoreSys, ha_ws_client: AsyncMock
):
    """Test initial Core install exposes a progress-reporting job for the landing page.

    During the initial Core install the landing page frontend polls
    ``/jobs/info`` and looks for a root job named ``home_assistant_core_install``
    to render a download progress bar, reading the job's ``progress`` field
    directly (see home-assistant/frontend#52359). This test guards that contract:
    Supervisor must expose a non-internal ``home_assistant_core_install`` job
    whose progress is driven by the underlying docker image pull (via
    ``child_job_syncs``), so it reports intermediate progress rather than jumping
    straight from 0 to 100.
    """
    coresys.security.force = True

    logs = load_json_fixture("docker_pull_image_log_containerd_snapshot.json")
    coresys.docker.images.pull.return_value = AsyncIterator(logs)

    with (
        patch.object(HomeAssistantCore, "start"),
        patch.object(DockerHomeAssistant, "cleanup"),
        patch.object(
            Updater,
            "image_homeassistant",
            new=PropertyMock(return_value="homeassistant"),
        ),
        patch.object(
            Updater, "version_homeassistant", new=PropertyMock(return_value="2022.7.3")
        ),
        patch.object(
            DockerInterface, "arch", new=PropertyMock(return_value=CpuArch.AMD64)
        ),
    ):
        await coresys.homeassistant.core.install()

    await asyncio.sleep(0)

    # The job events the landing page would observe via /jobs/info for the
    # install job. Receiving events at all proves the job is non-internal.
    install_events = [
        msg["data"]["data"]
        for c in ha_ws_client.async_send_command.call_args_list
        if (msg := c.args[0])["data"].get("event") == WSEvent.JOB
        and msg["data"]["data"]["name"] == "home_assistant_core_install"
    ]

    assert install_events
    # The landing page matches it as a root job (jobs[0]); it must not be nested.
    assert all(event["parent_id"] is None for event in install_events)

    # Progress is driven by the docker pull: starts at 0, reports intermediate
    # values, and completes at 100 - not a bare 0 -> 100 jump.
    progress = [event["progress"] for event in install_events]
    assert progress[0] == 0
    assert any(0 < value < 100 for value in progress)
    assert progress[-1] == 100
    assert install_events[-1]["done"] is True


def _core_install_progress(ha_ws_client: AsyncMock) -> list[float]:
    """Return the progress values reported for the Core install job over the WS."""
    return [
        msg["data"]["data"]["progress"]
        for c in ha_ws_client.async_send_command.call_args_list
        if (msg := c.args[0])["data"].get("event") == WSEvent.JOB
        and msg["data"]["data"]["name"] == "home_assistant_core_install"
    ]


async def test_install_progress_excludes_supervisor_self_update(
    coresys: CoreSys, ha_ws_client: AsyncMock
):
    """Test a Supervisor self-update pull does not count towards Core install progress.

    When Supervisor needs updating first, that runs its own docker image pull
    (a ``docker_interface_install`` job carrying the Supervisor container
    reference). The Core install job's ``child_job_syncs`` is scoped to the Home
    Assistant container, so the Supervisor pull must not move the Core install
    progress.
    """
    coresys.security.force = True

    logs = load_json_fixture("docker_pull_image_log_containerd_snapshot.json")
    coresys.docker.images.pull.return_value = AsyncIterator(logs)

    progress_after_self_update: list[float] = []

    async def fake_supervisor_update(*args, **kwargs) -> None:
        """Emulate a Supervisor self-update pulling its own image."""
        child = coresys.jobs.new_job(
            "docker_interface_install", reference="hassio_supervisor"
        )
        with child.start():
            child.progress = 100
        progress_after_self_update.append(coresys.jobs.current.progress)

    with (
        patch.object(HomeAssistantCore, "start"),
        patch.object(DockerHomeAssistant, "cleanup"),
        patch.object(
            Updater,
            "image_homeassistant",
            new=PropertyMock(return_value="homeassistant"),
        ),
        patch.object(
            Updater, "version_homeassistant", new=PropertyMock(return_value="2022.7.3")
        ),
        patch.object(
            DockerInterface, "arch", new=PropertyMock(return_value=CpuArch.AMD64)
        ),
        patch.object(
            type(coresys.supervisor),
            "need_update",
            new=PropertyMock(return_value=True),
        ),
        patch.object(
            type(coresys.updater), "auto_update", new=PropertyMock(return_value=True)
        ),
        patch.object(coresys.supervisor, "update", new=fake_supervisor_update),
    ):
        await coresys.homeassistant.core.install()

    await asyncio.sleep(0)

    # The Supervisor self-update pull reached 100% but must not have moved the
    # Core install job (it would be 100 here if the sync were not scoped).
    assert progress_after_self_update == [0]
    # The Core image pull afterwards still drives the job to completion.
    assert _core_install_progress(ha_ws_client)[-1] == 100


async def test_install_resets_progress_on_retry(
    coresys: CoreSys, ha_ws_client: AsyncMock
):
    """Test a failed install attempt resets progress instead of overshooting.

    The Core image pull runs in a retry loop. Docker resumes already-downloaded
    layers, so a retry's fresh pull reports them immediately and would otherwise
    push the synced progress straight to 100% if it stacked on top of the failed
    attempt. The sync resets to the baseline on a re-triggered child, so the bar
    restarts rather than overshooting.
    """
    coresys.security.force = True

    partial_then_error = [
        {
            "status": "Pulling from home-assistant/odroid-n2-homeassistant",
            "id": "1.2.3",
        },
        {"status": "Pulling fs layer", "progressDetail": {}, "id": "1578b14a573c"},
        {
            "status": "Downloading",
            "progressDetail": {"current": 500, "total": 1000},
            "id": "1578b14a573c",
        },
        {"errorDetail": {"message": "failure"}, "error": "failure"},
    ]
    full = load_json_fixture("docker_pull_image_log_containerd_snapshot.json")
    coresys.docker.images.pull.side_effect = [
        AsyncIterator(partial_then_error),
        AsyncIterator(full),
    ]

    with (
        patch.object(HomeAssistantCore, "start"),
        patch.object(DockerHomeAssistant, "cleanup"),
        patch.object(
            Updater,
            "image_homeassistant",
            new=PropertyMock(return_value="homeassistant"),
        ),
        patch.object(
            Updater, "version_homeassistant", new=PropertyMock(return_value="2022.7.3")
        ),
        patch.object(
            DockerInterface, "arch", new=PropertyMock(return_value=CpuArch.AMD64)
        ),
        patch("supervisor.homeassistant.core.asyncio.sleep"),
    ):
        await coresys.homeassistant.core.install()

    await asyncio.sleep(0)

    progress = _core_install_progress(ha_ws_client)
    first_nonzero = next(i for i, value in enumerate(progress) if value > 0)
    # The first attempt moved the bar, then the retry reset it back to 0 before
    # climbing to completion (rather than continuing from the failed progress).
    assert 0 in progress[first_nonzero:]
    assert progress[-1] == 100


@pytest.mark.parametrize(
    ("container_exc", "image_exc", "delete_calls"),
    [
        (aiodocker.DockerError(404, {"message": "missing"}), None, []),
        (
            None,
            aiodocker.DockerError(404, {"message": "missing"}),
            [call(force=True, v=True)],
        ),
        (None, None, [call(force=True, v=True)]),
    ],
)
@pytest.mark.usefixtures("path_extern")
async def test_start(
    coresys: CoreSys,
    container: DockerContainer,
    container_exc: aiodocker.DockerError | None,
    image_exc: aiodocker.DockerError | None,
    delete_calls: list[call],
):
    """Test starting Home Assistant."""
    coresys.docker.images.inspect.return_value = {"Id": "123"}
    coresys.docker.images.inspect.side_effect = image_exc
    container.id = "123"
    coresys.docker.containers.get.side_effect = container_exc

    with (
        patch.object(
            HomeAssistant,
            "version",
            new=PropertyMock(return_value=AwesomeVersion("2023.7.0")),
        ),
        patch.object(DockerAPI, "run", return_value=container.show.return_value) as run,
        patch.object(HomeAssistantCore, "_block_till_run") as block_till_run,
    ):
        await coresys.homeassistant.core.start()

        block_till_run.assert_called_once()
        run.assert_called_once()
        assert (
            run.call_args.args[0] == "ghcr.io/home-assistant/qemux86-64-homeassistant"
        )
        assert run.call_args.kwargs["tag"] == AwesomeVersion("2023.7.0")
        assert run.call_args.kwargs["name"] == "homeassistant"
        assert run.call_args.kwargs["hostname"] == "homeassistant"

    container.stop.assert_not_called()
    assert container.delete.call_args_list == delete_calls


@pytest.mark.usefixtures("path_extern")
async def test_start_existing_container(coresys: CoreSys, container: DockerContainer):
    """Test starting Home Assistant when container exists and is viable."""
    coresys.docker.images.inspect.return_value = {"Id": "123"}
    container.show.return_value["Image"] = "123"
    container.show.return_value["State"]["Status"] = "exited"
    container.show.return_value["State"]["Running"] = False

    with (
        patch.object(
            HomeAssistant,
            "version",
            new=PropertyMock(return_value=AwesomeVersion("2023.7.0")),
        ),
        patch.object(HomeAssistantCore, "_block_till_run") as block_till_run,
    ):
        await coresys.homeassistant.core.start()
        block_till_run.assert_called_once()

    container.start.assert_called_once()
    container.stop.assert_not_called()
    container.delete.assert_not_called()
    coresys.docker.containers.create.assert_not_called()


@pytest.mark.parametrize("exists", [True, False])
async def test_stop(coresys: CoreSys, container: DockerContainer, exists: bool):
    """Test stoppping Home Assistant."""
    if exists:
        container.show.return_value["State"]["Status"] = "running"
        container.show.return_value["State"]["Running"] = True
    else:
        coresys.docker.containers.get.side_effect = aiodocker.DockerError(
            404, {"message": "missing"}
        )

    await coresys.homeassistant.core.stop()

    container.delete.assert_not_called()
    if exists:
        container.stop.assert_called_once_with(t=260)
    else:
        container.stop.assert_not_called()


async def test_restart(coresys: CoreSys, container: DockerContainer):
    """Test restarting Home Assistant."""
    with patch.object(HomeAssistantCore, "_block_till_run") as block_till_run:
        await coresys.homeassistant.core.restart()
        block_till_run.assert_called_once()

    container.restart.assert_called_once_with(t=260)
    container.stop.assert_not_called()


@pytest.mark.parametrize(
    "get_error",
    [
        aiodocker.DockerError(404, {"message": "missing"}),
        aiodocker.DockerError(500, {"message": "fail"}),
        None,
    ],
)
async def test_restart_failures(
    coresys: CoreSys,
    container: DockerContainer,
    get_error: aiodocker.DockerError | None,
):
    """Test restart fails when container missing or can't be restarted."""
    container.restart.side_effect = aiodocker.DockerError(500, {"message": "fail"})
    if get_error:
        coresys.docker.containers.get.side_effect = get_error

    with pytest.raises(HomeAssistantError):
        await coresys.homeassistant.core.restart()


@pytest.mark.parametrize(
    ("get_error", "running"),
    [
        (aiodocker.DockerError(404, {"message": "missing"}), False),
        (aiodocker.DockerError(500, {"message": "fail"}), False),
        (None, False),
        (None, True),
    ],
)
async def test_stats_failures(
    coresys: CoreSys,
    container: DockerContainer,
    get_error: aiodocker.DockerError | None,
    running: bool,
):
    """Test errors when getting stats."""
    container.show.return_value["State"]["Status"] = "running" if running else "stopped"
    container.show.return_value["State"]["Running"] = running
    container.stats.side_effect = aiodocker.DockerError(500, {"message": "fail"})
    if get_error:
        coresys.docker.containers.get.side_effect = get_error

    with pytest.raises(HomeAssistantError):
        await coresys.homeassistant.core.stats()


async def test_api_check_timeout(
    coresys: CoreSys, container: DockerContainer, caplog: pytest.LogCaptureFixture
):
    """Test attempts to contact the API timeout."""
    container.show.return_value["State"]["Status"] = "stopped"
    container.show.return_value["State"]["Running"] = False
    coresys.homeassistant.version = AwesomeVersion("2023.9.0")
    coresys.homeassistant.api.get_api_state.return_value = None

    async def mock_instance_start(*_):
        container.show.return_value["State"]["Status"] = "running"
        container.show.return_value["State"]["Running"] = True

    with (
        patch.object(DockerHomeAssistant, "start", new=mock_instance_start),
        patch.object(DockerAPI, "container_is_initialized", return_value=True),
        travel(datetime(2023, 10, 2, 0, 0, 0), tick=False) as traveller,
    ):

        async def mock_sleep(*args):
            traveller.shift(timedelta(minutes=1))

        with (
            patch("supervisor.homeassistant.core.asyncio.sleep", new=mock_sleep),
            pytest.raises(HomeAssistantCrashError),
        ):
            await coresys.homeassistant.core.start()

    assert coresys.homeassistant.api.get_api_state.call_count == 10
    assert (
        "No Home Assistant Core response, assuming a fatal startup error" in caplog.text
    )


async def test_api_check_success(
    coresys: CoreSys, container: DockerContainer, caplog: pytest.LogCaptureFixture
):
    """Test attempts to contact the API timeout."""
    container.show.return_value["State"]["Status"] = "stopped"
    container.show.return_value["State"]["Running"] = False
    coresys.homeassistant.version = AwesomeVersion("2023.9.0")

    async def mock_instance_start(*_):
        container.show.return_value["State"]["Status"] = "running"
        container.show.return_value["State"]["Running"] = True

    with (
        patch.object(DockerHomeAssistant, "start", new=mock_instance_start),
        patch.object(DockerAPI, "container_is_initialized", return_value=True),
        travel(datetime(2023, 10, 2, 0, 0, 0), tick=False) as traveller,
    ):

        async def mock_sleep(*args):
            traveller.shift(timedelta(minutes=1))

        with patch("supervisor.homeassistant.core.asyncio.sleep", new=mock_sleep):
            await coresys.homeassistant.core.start()

    assert coresys.homeassistant.api.get_api_state.call_count == 1
    assert "Detect a running Home Assistant instance" in caplog.text


async def test_api_check_database_migration(
    coresys: CoreSys, container: DockerContainer, caplog: pytest.LogCaptureFixture
):
    """Test attempts to contact the API timeout."""
    calls = []

    def mock_api_state(*args):
        calls.append(None)
        if len(calls) > 50:
            return APIState("RUNNING", False)
        return APIState("NOT_RUNNING", True)

    container.show.return_value["State"]["Status"] = "stopped"
    container.show.return_value["State"]["Running"] = False
    coresys.homeassistant.version = AwesomeVersion("2023.9.0")
    coresys.homeassistant.api.get_api_state.side_effect = mock_api_state

    async def mock_instance_start(*_):
        container.show.return_value["State"]["Status"] = "running"
        container.show.return_value["State"]["Running"] = True

    with (
        patch.object(DockerHomeAssistant, "start", new=mock_instance_start),
        patch.object(DockerAPI, "container_is_initialized", return_value=True),
        travel(datetime(2023, 10, 2, 0, 0, 0), tick=False) as traveller,
    ):

        async def mock_sleep(*args):
            traveller.shift(timedelta(minutes=1))

        with patch("supervisor.homeassistant.core.asyncio.sleep", new=mock_sleep):
            await coresys.homeassistant.core.start()

    assert coresys.homeassistant.api.get_api_state.call_count == 51
    assert "Detect a running Home Assistant instance" in caplog.text


async def test_core_loads_wrong_image_for_machine(
    coresys: CoreSys, container: DockerContainer
):
    """Test core is loaded with wrong image for machine."""
    coresys.homeassistant.set_image("ghcr.io/home-assistant/odroid-n2-homeassistant")
    coresys.homeassistant.version = AwesomeVersion("2024.4.0")

    with patch.object(
        DockerAPI,
        "pull_image",
        return_value={
            "Id": "abc123",
            "Config": {"Labels": {"io.hass.version": "2024.4.0"}},
        },
    ) as pull_image:
        container.show.return_value |= pull_image.return_value
        await coresys.homeassistant.core.load()
        pull_image.assert_called_once_with(
            ANY,
            "ghcr.io/home-assistant/qemux86-64-homeassistant",
            "2024.4.0",
            platform="linux/amd64",
            auth=None,
        )

    container.delete.assert_called_once_with(force=True, v=True)
    assert coresys.docker.images.delete.call_args_list[0] == call(
        "ghcr.io/home-assistant/odroid-n2-homeassistant:latest",
        force=True,
    )
    assert coresys.docker.images.delete.call_args_list[1] == call(
        "ghcr.io/home-assistant/odroid-n2-homeassistant:2024.4.0",
        force=True,
    )
    assert (
        coresys.homeassistant.image == "ghcr.io/home-assistant/qemux86-64-homeassistant"
    )


@pytest.mark.usefixtures("path_extern")
async def test_load_preinstalled_landingpage_keeps_version(
    coresys: CoreSys, container: DockerContainer
):
    """Test load keeps LANDINGPAGE when the landingpage image has a real version label.

    Regression test: the landingpage image stamps a real Core version into its
    io.hass.version label while keeping io.hass.type=landingpage. On a Supervisor
    restart the persisted version (LANDINGPAGE) must not be overwritten with that
    real version, otherwise the landingpage is mistaken for an installed Core and
    Core never gets installed.
    """
    coresys.homeassistant.version = LANDINGPAGE
    coresys.homeassistant.override_image = True
    container.show.return_value["Config"] = {
        "Labels": {
            "io.hass.type": "landingpage",
            "io.hass.version": "2026.06.3",
        }
    }

    with patch.object(DockerHomeAssistant, "is_running", return_value=True):
        await coresys.homeassistant.core.load()

    assert coresys.homeassistant.version == LANDINGPAGE


async def test_core_load_allows_image_override(
    coresys: CoreSys, container: DockerContainer
):
    """Test core does not change image if user overrode it."""
    coresys.homeassistant.set_image("ghcr.io/home-assistant/odroid-n2-homeassistant")
    coresys.homeassistant.version = AwesomeVersion("2024.4.0")
    container.show.return_value["Config"] = {"Labels": {"io.hass.version": "2024.4.0"}}

    coresys.homeassistant.override_image = True
    await coresys.homeassistant.core.load()

    container.delete.assert_not_called()
    coresys.docker.images.delete.assert_not_called()
    coresys.docker.images.inspect.assert_not_called()
    assert (
        coresys.homeassistant.image == "ghcr.io/home-assistant/odroid-n2-homeassistant"
    )


async def test_core_loads_wrong_image_for_architecture(
    coresys: CoreSys, container: DockerContainer
):
    """Test core is loaded with wrong image for architecture."""
    coresys.homeassistant.version = AwesomeVersion("2024.4.0")
    coresys.docker.images.inspect.return_value = img_data = (
        coresys.docker.images.inspect.return_value
        | {
            "Architecture": "arm64",
            "Config": {"Labels": {"io.hass.version": "2024.4.0"}},
        }
    )
    container.show.return_value |= img_data

    with patch.object(
        DockerAPI,
        "pull_image",
        return_value=img_data | {"Architecture": "amd64"},
    ) as pull_image:
        await coresys.homeassistant.core.load()
        pull_image.assert_called_once_with(
            ANY,
            "ghcr.io/home-assistant/qemux86-64-homeassistant",
            "2024.4.0",
            platform="linux/amd64",
            auth=None,
        )

    container.delete.assert_called_once_with(force=True, v=True)
    assert coresys.docker.images.delete.call_args_list[0] == call(
        "ghcr.io/home-assistant/qemux86-64-homeassistant:latest",
        force=True,
    )
    assert coresys.docker.images.delete.call_args_list[1] == call(
        "ghcr.io/home-assistant/qemux86-64-homeassistant:2024.4.0",
        force=True,
    )
    assert (
        coresys.homeassistant.image == "ghcr.io/home-assistant/qemux86-64-homeassistant"
    )
