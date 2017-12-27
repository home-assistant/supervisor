"""Main file for HassIO."""
import asyncio
import logging

from .addons import AddonManager
from .api import RestAPI
from .const import (
    RUN_UPDATE_INFO_TASKS, RUN_RELOAD_ADDONS_TASKS,
    RUN_UPDATE_SUPERVISOR_TASKS, RUN_WATCHDOG_HOMEASSISTANT_DOCKER,
    RUN_CLEANUP_API_SESSIONS, STARTUP_SYSTEM, STARTUP_SERVICES,
    STARTUP_APPLICATION, STARTUP_INITIALIZE, RUN_RELOAD_SNAPSHOTS_TASKS,
    RUN_UPDATE_ADDONS_TASKS)
from .homeassistant import HomeAssistant
from .dock.supervisor import DockerSupervisor
from .snapshots import SnapshotsManager
from .updater import Updater
from .tasks import (
    hassio_update, homeassistant_watchdog_docker, api_sessions_cleanup,
    addons_update)
from .utils.datetime import fetch_timezone

_LOGGER = logging.getLogger(__name__)


class HassIO(object):
    """Main object of hassio."""

    def __init__(self, coresys):
        """Initialize hassio object."""
        self.coresys = coresys
        self.loop = coresys.loop
        self.config = coresys.config
        self.hardware = coresys.hardware
        self.host_control = coresys.host_control
        self.websession = coresys.websession

        self.updater = Updater(coresys)
        self.api = RestAPI(coresys)
        self.supervisor = DockerSupervisor(coresys)
        self.homeassistant = HomeAssistant(coresys, self.updater)
        self.addons = AddonManager(coresys)
        self.snapshots = SnapshotsManager(
            coresys, self.addons, self.homeassistant)

    async def setup(self):
        """Setup HassIO orchestration."""
        # supervisor
        if not await self.supervisor.attach():
            _LOGGER.fatal("Can't setup supervisor docker container!")
        await self.supervisor.cleanup()

        # set running arch
        self.coresys.arch = self.supervisor.arch

        # update timezone
        if self.config.timezone == 'UTC':
            self.config.timezone = await fetch_timezone(self.websession)

        # hostcontrol
        await self.host_control.load()

        # schedule update info tasks
        self.scheduler.register_task(
            self.host_control.load, RUN_UPDATE_INFO_TASKS)

        # rest api views
        self.api.register_host(self.host_control, self.hardware)
        self.api.register_network(self.host_control)
        self.api.register_supervisor(
            self.supervisor, self.snapshots, self.addons, self.host_control,
            self.updater)
        self.api.register_homeassistant(self.homeassistant)
        self.api.register_proxy(self.homeassistant)
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
            hassio_update(self.supervisor, self.updater),
            RUN_UPDATE_SUPERVISOR_TASKS)

        # schedule snapshot update tasks
        self.scheduler.register_task(
            self.snapshots.reload, RUN_RELOAD_SNAPSHOTS_TASKS, now=True)

        # start dns forwarding
        self.loop.create_task(self.dns.start())

        # start addon mark as initialize
        await self.addons.auto_boot(STARTUP_INITIALIZE)

    async def start(self):
        """Start HassIO orchestration."""
        # on release channel, try update itself
        # on beta channel, only read new versions
        await asyncio.wait(
            [hassio_update(self.supervisor, self.updater)()],
            loop=self.loop
        )

        # start api
        await self.api.start()
        _LOGGER.info("Start hassio api on %s", self.docker.network.supervisor)

        try:
            # HomeAssistant is already running / supervisor have only reboot
            if self.hardware.last_boot == self.config.last_boot:
                _LOGGER.info("HassIO reboot detected")
                return

            # start addon mark as system
            await self.addons.auto_boot(STARTUP_SYSTEM)

            # start addon mark as services
            await self.addons.auto_boot(STARTUP_SERVICES)

            # run HomeAssistant
            if self.homeassistant.boot:
                await self.homeassistant.run()

            # start addon mark as application
            await self.addons.auto_boot(STARTUP_APPLICATION)

            # store new last boot
            self.config.last_boot = self.hardware.last_boot

        finally:
            # schedule homeassistant watchdog
            self.scheduler.register_task(
                homeassistant_watchdog_docker(self.loop, self.homeassistant),
                RUN_WATCHDOG_HOMEASSISTANT_DOCKER)

            # self.scheduler.register_task(
            #    homeassistant_watchdog_api(self.loop, self.homeassistant),
            #    RUN_WATCHDOG_HOMEASSISTANT_API)

            # If landingpage / run upgrade in background
            if self.homeassistant.version == 'landingpage':
                self.loop.create_task(self.homeassistant.install())

    async def stop(self):
        """Stop a running orchestration."""
        # don't process scheduler anymore
        self.scheduler.suspend = True

        # process stop tasks
        self.websession.close()
        self.homeassistant.websession.close()

        # process async stop tasks
        await asyncio.wait([self.api.stop(), self.dns.stop()], loop=self.loop)
