"""Main file for HassIO."""
import asyncio
import logging

import aiohttp
import docker

from . import bootstrap
from .addons import AddonManager
from .api import RestAPI
from .host_control import HostControl
from .const import (
    SOCKET_DOCKER, RUN_UPDATE_INFO_TASKS, RUN_RELOAD_ADDONS_TASKS,
    RUN_UPDATE_SUPERVISOR_TASKS, RUN_WATCHDOG_HOMEASSISTANT,
    RUN_CLEANUP_API_SESSIONS, STARTUP_AFTER, STARTUP_BEFORE)
from .scheduler import Scheduler
from .dock.homeassistant import DockerHomeAssistant
from .dock.supervisor import DockerSupervisor
from .tasks import (
    hassio_update, homeassistant_watchdog, homeassistant_setup,
    api_sessions_cleanup)
from .tools import get_arch_from_image, get_local_ip

_LOGGER = logging.getLogger(__name__)


class HassIO(object):
    """Main object of hassio."""

    def __init__(self, loop):
        """Initialize hassio object."""
        self.exit_code = 0
        self.loop = loop
        self.websession = aiohttp.ClientSession(loop=self.loop)
        self.config = bootstrap.initialize_system_data(self.websession)
        self.scheduler = Scheduler(self.loop)
        self.api = RestAPI(self.config, self.loop)
        self.dock = docker.DockerClient(
            base_url="unix:/{}".format(str(SOCKET_DOCKER)), version='auto')

        # init basic docker container
        self.supervisor = DockerSupervisor(
            self.config, self.loop, self.dock, self)
        self.homeassistant = DockerHomeAssistant(
            self.config, self.loop, self.dock)

        # init HostControl
        self.host_control = HostControl(self.loop)

        # init addon system
        self.addons = AddonManager(self.config, self.loop, self.dock)

    async def setup(self):
        """Setup HassIO orchestration."""
        # supervisor
        await self.supervisor.attach()
        await self.supervisor.cleanup()

        # set api endpoint
        self.config.api_endpoint = await get_local_ip(self.loop)

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
                self.config, self.loop, self.homeassistant)

        # Load addons
        arch = get_arch_from_image(self.supervisor.image)
        await self.addons.prepare(arch)

        # schedule addon update task
        self.scheduler.register_task(
            self.addons.reload, RUN_RELOAD_ADDONS_TASKS, now=True)

        # schedule self update task
        self.scheduler.register_task(
            hassio_update(self.config, self.supervisor),
            RUN_UPDATE_SUPERVISOR_TASKS)

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

        # process stop task pararell
        tasks = [self.websession.close(), self.api.stop()]
        await asyncio.wait(tasks, loop=self.loop)

        self.exit_code = exit_code
        self.loop.stop()
