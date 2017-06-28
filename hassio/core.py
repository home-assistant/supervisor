"""Main file for HassIO."""
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
    STARTUP_INITIALIZE)
from .scheduler import Scheduler
from .dock.homeassistant import DockerHomeAssistant
from .dock.supervisor import DockerSupervisor
from .tasks import (
    hassio_update, homeassistant_watchdog, homeassistant_setup,
    api_sessions_cleanup)
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
        self.homeassistant = DockerHomeAssistant(config, loop, self.dock)

        # init HostControl
        self.host_control = HostControl(loop)

        # init addon system
        self.addons = AddonManager(config, loop, self.dock)

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
            self.supervisor, self.addons, self.host_control)
        self.api.register_homeassistant(self.homeassistant)
        self.api.register_addons(self.addons)
        self.api.register_security()
        self.api.register_panel()

        # schedule api session cleanup
        self.scheduler.register_task(
            api_sessions_cleanup(self.config), RUN_CLEANUP_API_SESSIONS,
            now=True)

        # schedule update info tasks
        self.scheduler.register_task(
            self.config.fetch_update_infos, RUN_UPDATE_INFO_TASKS,
            now=True)

        # first start of supervisor?
        if not await self.homeassistant.exists():
            _LOGGER.info("No HomeAssistant docker found.")
            await homeassistant_setup(
                self.config, self.loop, self.homeassistant, self.websession)
        else:
            await self.homeassistant.attach()

        # Load addons
        await self.addons.prepare()

        # schedule addon update task
        self.scheduler.register_task(
            self.addons.reload, RUN_RELOAD_ADDONS_TASKS, now=True)

        # schedule self update task
        self.scheduler.register_task(
            hassio_update(self.config, self.supervisor),
            RUN_UPDATE_SUPERVISOR_TASKS)

        # start addon mark as initialize
        await self.addons.auto_boot(STARTUP_INITIALIZE)

    async def start(self):
        """Start HassIO orchestration."""
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
        self.scheduler.stop()

        # process stop tasks
        self.websession.close()
        await self.api.stop()

        self.exit_code = exit_code
        self.loop.stop()
