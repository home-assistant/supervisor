"""Main file for Supervisor."""
import asyncio
from contextlib import suppress
import logging
from typing import Awaitable, List, Optional

import async_timeout

from .const import RUN_SUPERVISOR_STATE, AddonStartup, CoreState
from .coresys import CoreSys, CoreSysAttributes
from .exceptions import (
    HassioError,
    HomeAssistantCrashError,
    HomeAssistantError,
    SupervisorUpdateError,
)
from .resolution.const import ContextType, IssueType, UnhealthyReason

_LOGGER: logging.Logger = logging.getLogger(__name__)


class Core(CoreSysAttributes):
    """Main object of Supervisor."""

    def __init__(self, coresys: CoreSys) -> None:
        """Initialize Supervisor object."""
        self.coresys: CoreSys = coresys
        self._state: Optional[CoreState] = None

    @property
    def state(self) -> CoreState:
        """Return state of the core."""
        return self._state

    @property
    def supported(self) -> bool:
        """Return true if the installation is supported."""
        return len(self.sys_resolution.unsupported) == 0

    @property
    def healthy(self) -> bool:
        """Return true if the installation is healthy."""
        return len(self.sys_resolution.unhealthy) == 0

    @state.setter
    def state(self, new_state: CoreState) -> None:
        """Set core into new state."""
        try:
            RUN_SUPERVISOR_STATE.write_text(new_state.value)
        except OSError as err:
            _LOGGER.warning(
                "Can't update the Supervisor state to %s: %s", new_state, err
            )
        finally:
            self._state = new_state

    async def connect(self) -> None:
        """Connect Supervisor container."""
        self.state = CoreState.INITIALIZE

        # Load information from container
        await self.sys_supervisor.load()

        # Evaluate the system
        await self.sys_resolution.evaluate.evaluate_system()

        # Check supervisor version/update
        if self.sys_dev:
            self.sys_config.version = self.sys_supervisor.version
        elif self.sys_config.version != self.sys_supervisor.version:
            self.sys_resolution.create_issue(
                IssueType.UPDATE_ROLLBACK, ContextType.SUPERVISOR
            )
            self.sys_resolution.unhealthy = UnhealthyReason.SUPERVISOR
            _LOGGER.error(
                "Update '%s' of Supervisor '%s' failed!",
                self.sys_config.version,
                self.sys_supervisor.version,
            )

    async def setup(self) -> None:
        """Start setting up supervisor orchestration."""
        self.state = CoreState.SETUP

        setup_loads: List[Awaitable[None]] = [
            # rest api views
            self.sys_api.load(),
            # Load DBus
            self.sys_dbus.load(),
            # Load Host
            self.sys_host.load(),
            # Load Plugins container
            self.sys_plugins.load(),
            # load last available data
            self.sys_updater.load(),
            # Load Home Assistant
            self.sys_homeassistant.load(),
            # Load CPU/Arch
            self.sys_arch.load(),
            # Load HassOS
            self.sys_os.load(),
            # Load Stores
            self.sys_store.load(),
            # Load Add-ons
            self.sys_addons.load(),
            # load last available data
            self.sys_snapshots.load(),
            # load services
            self.sys_services.load(),
            # Load discovery
            self.sys_discovery.load(),
            # Load ingress
            self.sys_ingress.load(),
            # Load Resoulution
            self.sys_resolution.load(),
        ]

        # Execute each load task in secure context
        for setup_task in setup_loads:
            try:
                await setup_task
            except Exception as err:  # pylint: disable=broad-except
                _LOGGER.critical(
                    "Fatal error happening on load Task %s: %s", setup_task, err
                )
                self.sys_resolution.unhealthy = UnhealthyReason.SETUP
                self.sys_capture_exception(err)

        # Evaluate the system
        await self.sys_resolution.evaluate.evaluate_system()

    async def start(self) -> None:
        """Start Supervisor orchestration."""
        self.state = CoreState.STARTUP

        # Check if system is healthy
        if not self.supported:
            _LOGGER.warning("System running in a unsupported environment!")
        if not self.healthy:
            _LOGGER.critical(
                "System running in a unhealthy state and need manual intervention!"
            )

        # Check internet on startup
        await self.sys_supervisor.check_connectivity()

        # Mark booted partition as healthy
        if self.sys_os.available:
            await self.sys_os.mark_healthy()

        # On release channel, try update itself
        if self.sys_supervisor.need_update:
            try:
                if not self.healthy:
                    _LOGGER.warning("Ignoring Supervisor updates!")
                else:
                    await self.sys_supervisor.update()
                    return
            except SupervisorUpdateError as err:
                _LOGGER.critical(
                    "Can't update Supervisor! This will break some Add-ons or affect "
                    "future version of Home Assistant!"
                )
                self.sys_capture_exception(err)

        # Start addon mark as initialize
        await self.sys_addons.boot(AddonStartup.INITIALIZE)

        try:
            # HomeAssistant is already running / supervisor have only reboot
            if self.sys_hardware.last_boot == self.sys_config.last_boot:
                _LOGGER.info("Supervisor reboot detected")
                return

            # reset register services / discovery
            self.sys_services.reset()

            # start addon mark as system
            await self.sys_addons.boot(AddonStartup.SYSTEM)

            # start addon mark as services
            await self.sys_addons.boot(AddonStartup.SERVICES)

            # run HomeAssistant
            if (
                self.sys_homeassistant.boot
                and not await self.sys_homeassistant.core.is_running()
            ):
                try:
                    await self.sys_homeassistant.core.start()
                except HomeAssistantCrashError as err:
                    _LOGGER.error("Can't start Home Assistant Core - rebuiling")
                    self.sys_capture_exception(err)

                    with suppress(HomeAssistantError):
                        await self.sys_homeassistant.core.rebuild()
                except HomeAssistantError as err:
                    self.sys_capture_exception(err)
            else:
                _LOGGER.info("Skiping start of Home Assistant")

            # start addon mark as application
            await self.sys_addons.boot(AddonStartup.APPLICATION)

            # store new last boot
            self._update_last_boot()

        finally:
            # Add core tasks into scheduler
            await self.sys_tasks.load()

            # If landingpage / run upgrade in background
            if self.sys_homeassistant.version == "landingpage":
                self.sys_create_task(self.sys_homeassistant.core.install())

            # Start observe the host Hardware
            await self.sys_hwmonitor.load()

            # Upate Host/Deivce information
            self.sys_create_task(self.sys_host.reload())
            self.sys_create_task(self.sys_updater.reload())

            self.state = CoreState.RUNNING
            _LOGGER.info("Supervisor is up and running")

    async def stop(self) -> None:
        """Stop a running orchestration."""
        # store new last boot / prevent time adjustments
        if self.state in (CoreState.RUNNING, CoreState.SHUTDOWN, CoreState.FREEZE):
            self._update_last_boot()
        if self.state in (CoreState.STOPPING, CoreState.CLOSE):
            return

        # don't process scheduler anymore
        self.state = CoreState.STOPPING

        # Stage 1
        try:
            async with async_timeout.timeout(10):
                await asyncio.wait([self.sys_api.stop(), self.sys_scheduler.shutdown()])
        except asyncio.TimeoutError:
            _LOGGER.warning("Stage 1: Force Shutdown!")

        # Stage 2
        try:
            async with async_timeout.timeout(10):
                await asyncio.wait(
                    [
                        self.sys_websession.close(),
                        self.sys_websession_ssl.close(),
                        self.sys_ingress.unload(),
                        self.sys_hwmonitor.unload(),
                    ]
                )
        except asyncio.TimeoutError:
            _LOGGER.warning("Stage 2: Force Shutdown!")

        self.state = CoreState.CLOSE
        _LOGGER.info("Supervisor is down")
        self.sys_loop.stop()

    async def shutdown(self) -> None:
        """Shutdown all running containers in correct order."""
        # don't process scheduler anymore
        if self.state == CoreState.RUNNING:
            self.state = CoreState.SHUTDOWN

        # Shutdown Application Add-ons, using Home Assistant API
        await self.sys_addons.shutdown(AddonStartup.APPLICATION)

        # Close Home Assistant
        with suppress(HassioError):
            await self.sys_homeassistant.core.stop()

        # Shutdown System Add-ons
        await self.sys_addons.shutdown(AddonStartup.SERVICES)
        await self.sys_addons.shutdown(AddonStartup.SYSTEM)
        await self.sys_addons.shutdown(AddonStartup.INITIALIZE)

        # Shutdown all Plugins
        if self.state in (CoreState.STOPPING, CoreState.SHUTDOWN):
            await self.sys_plugins.shutdown()

    def _update_last_boot(self) -> None:
        """Update last boot time."""
        self.sys_config.last_boot = self.sys_hardware.last_boot
        self.sys_config.save_data()

    async def repair(self) -> None:
        """Repair system integrity."""
        _LOGGER.info("Starting repair of Supervisor Environment")
        await self.sys_run_in_executor(self.sys_docker.repair)

        # Fix plugins
        await self.sys_plugins.repair()

        # Restore core functionality
        await self.sys_addons.repair()
        await self.sys_homeassistant.core.repair()

        # Tag version for latest
        await self.sys_supervisor.repair()
        _LOGGER.info("Finished repair of Supervisor Environment")

    async def factory_reset(self) -> None:
        """Reset the system as soft factory reset."""
        _LOGGER.info("Starting factory reset of Supervisor Environment")
        self.state = CoreState.FREEZE

        reset_tasks: List[Awaitable[None]] = [
            self.sys_addons.factory_reset(),
            self.sys_homeassistant.factory_reset(),
            self.sys_plugins.factory_reset(),
            self.sys_host.factory_reset(),
        ]
        for task in reset_tasks:
            await task

        # Reset system settings
        self.sys_config.reset_data()
        self.sys_config.save_data()

        # Restart Supervisor
        self.stop()
