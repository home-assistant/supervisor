"""Main file for HassIO."""
import asyncio
import logging

import aiohttp
import docker

from .addons import AddonManager
from .api import RestAPI
from .host_control import HostControl
from .const import (
    SOCKET_DOCKER, RUN_UPDATE_INFO_TASKS, RUN_RELOAD_ADDONS_TASKS,
    RUN_UPDATE_SUPERVISOR_TASKS, RUN_WATCHDOG_HOMEASSISTANT,
    RUN_CLEANUP_API_SESSIONS, STARTUP_AFTER, STARTUP_BEFORE,
    STARTUP_INITIALIZE, RUN_RELOAD_SNAPSHOTS_TASKS, RUN_UPDATE_ADDONS_TASKS)
from .homeassistant import HomeAssistant
from .scheduler import Scheduler
from .dock.supervisor import DockerSupervisor
from .snapshots import SnapshotsManager
from .tasks import (
    hassio_update, homeassistant_watchdog, api_sessions_cleanup, addons_update)
from .tools import get_local_ip, fetch_timezone

_LOGGER = logging.getLogger(__name__)


class HassIO(object):
    """Main object of hassio."""

    def __init__(self, loop, config):
        """Initialize hassio object."""
        self.exit_code = 0
        self.loop = loop
        self.config = config
        self.websession = aiohttp.ClientSession(loop=loop)
        self.scheduler = Scheduler(loop)
        self.api = RestAPI(config, loop)
        self.dock = docker.DockerClient(
            base_url="unix:/{}".format(str(SOCKET_DOCKER)), version='auto')

        # init basic docker container
        self.supervisor = DockerSupervisor(config, loop, self.dock, self.stop)

        # init homeassistant
        self.homeassistant = HomeAssistant(
            config, loop, self.dock, self.websession)

        # init HostControl
        self.host_control = HostControl(loop)

        # init addon system
        self.addons = AddonManager(config, loop, self.dock)

        # init snapshot system
        self.snapshots = SnapshotsManager(
            config, loop, self.scheduler, self.addons, self.homeassistant)

    async def setup(self):
        """Setup HassIO orchestration."""
        # supervisor
        if not await self.supervisor.attach():
            _LOGGER.fatal("Can't attach to supervisor docker container!")
        await self.supervisor.cleanup()

        # set running arch
        self.config.arch = self.supervisor.arch

        # set api endpoint
        self.config.api_endpoint = await get_local_ip(self.loop)

        # update timezone
        if self.config.timezone == 'UTC':
            self.config.timezone = await fetch_timezone(self.websession)

        # hostcontrol
        await self.host_control.load()

        # schedule update info tasks
        self.scheduler.register_task(
            self.host_control.load, RUN_UPDATE_INFO_TASKS)

        # rest api views
        self.api.register_host(self.host_control)
        self.api.register_network(self.host_control)
        self.api.register_supervisor(
            self.supervisor, self.snapshots, self.addons, self.host_control,
            self.websession)
        self.api.register_homeassistant(self.homeassistant)
        self.api.register_addons(self.addons)
        self.api.register_security()
        self.api.register_snapshots(self.snapshots)
        self.api.register_panel()

        # schedule api session cleanup
        self.scheduler.register_task(
            api_sessions_cleanup(self.config), RUN_CLEANUP_API_SESSIONS,
            now=True)

        # Load homeassistant
        await self.homeassistant.prepare()

        # Load addons
        await self.addons.prepare()

        # schedule addon update task
        self.scheduler.register_task(
            self.addons.reload, RUN_RELOAD_ADDONS_TASKS, now=True)
        self.scheduler.register_task(
            addons_update(self.loop, self.addons), RUN_UPDATE_ADDONS_TASKS)

        # schedule self update task
        self.scheduler.register_task(
            hassio_update(self.config, self.supervisor, self.websession),
            RUN_UPDATE_SUPERVISOR_TASKS)

        # schedule snapshot update tasks
        self.scheduler.register_task(
            self.snapshots.reload, RUN_RELOAD_SNAPSHOTS_TASKS, now=True)

        # start addon mark as initialize
        await self.addons.auto_boot(STARTUP_INITIALIZE)

    async def start(self):
        """Start HassIO orchestration."""
        # on release channel, try update itself
        # on beta channel, only read new versions
        await asyncio.wait(
            [hassio_update(self.config, self.supervisor, self.websession)()],
            loop=self.loop
        )

        # If laningpage / run upgrade in background
        if self.homeassistant.version == 'landingpage':
            self.loop.create_task(self.homeassistant.install())

        # start api
        await self.api.start()
        _LOGGER.info("Start hassio api on %s", self.config.api_endpoint)

        try:
            # HomeAssistant is already running / supervisor have only reboot
            if await self.homeassistant.is_running():
                _LOGGER.info("HassIO reboot detected")
                return

            # start addon mark as before
            await self.addons.auto_boot(STARTUP_BEFORE)

            # run HomeAssistant
            await self.homeassistant.run()

            # start addon mark as after
            await self.addons.auto_boot(STARTUP_AFTER)

        finally:
            # schedule homeassistant watchdog
            self.scheduler.register_task(
                homeassistant_watchdog(self.loop, self.homeassistant),
                RUN_WATCHDOG_HOMEASSISTANT)

    async def stop(self, exit_code=0):
        """Stop a running orchestration."""
        # don't process scheduler anymore
        self.scheduler.suspend = True

        # process stop tasks
        self.websession.close()
        await self.api.stop()

        self.exit_code = exit_code
        self.loop.stop()
