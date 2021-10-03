"""Home Assistant dns plugin.

Code: https://github.com/home-assistant/plugin-dns
"""
import asyncio
from contextlib import suppress
from ipaddress import IPv4Address
import logging
from pathlib import Path
from typing import Optional

import attr
from awesomeversion import AwesomeVersion
import jinja2
import voluptuous as vol

from ..const import ATTR_SERVERS, DNS_SUFFIX, LogLevel
from ..coresys import CoreSys
from ..docker.dns import DockerDNS
from ..docker.stats import DockerStats
from ..exceptions import (
    ConfigurationFileError,
    CoreDNSError,
    CoreDNSUpdateError,
    DockerError,
)
from ..resolution.const import ContextType, IssueType, SuggestionType
from ..utils.json import write_json_file
from ..validate import dns_url
from .base import PluginBase
from .const import FILE_HASSIO_DNS
from .validate import SCHEMA_DNS_CONFIG

_LOGGER: logging.Logger = logging.getLogger(__name__)

HOSTS_TMPL: Path = Path(__file__).parents[1].joinpath("data/hosts.tmpl")
RESOLV_TMPL: Path = Path(__file__).parents[1].joinpath("data/resolv.tmpl")
HOST_RESOLV: Path = Path("/etc/resolv.conf")


@attr.s
class HostEntry:
    """Single entry in hosts."""

    ip_address: IPv4Address = attr.ib()
    names: list[str] = attr.ib()


class PluginDns(PluginBase):
    """Home Assistant core object for handle it."""

    def __init__(self, coresys: CoreSys):
        """Initialize hass object."""
        super().__init__(FILE_HASSIO_DNS, SCHEMA_DNS_CONFIG)
        self.slug = "dns"
        self.coresys: CoreSys = coresys
        self.instance: DockerDNS = DockerDNS(coresys)
        self.resolv_template: Optional[jinja2.Template] = None
        self.hosts_template: Optional[jinja2.Template] = None

        self._hosts: list[HostEntry] = []
        self._loop: bool = False

    @property
    def hosts(self) -> Path:
        """Return Path to corefile."""
        return Path(self.sys_config.path_dns, "hosts")

    @property
    def coredns_config(self) -> Path:
        """Return Path to coredns config file."""
        return Path(self.sys_config.path_dns, "coredns.json")

    @property
    def locals(self) -> list[str]:
        """Return list of local system DNS servers."""
        servers: list[str] = []
        for server in [
            f"dns://{server!s}" for server in self.sys_host.network.dns_servers
        ]:
            with suppress(vol.Invalid):
                servers.append(dns_url(server))

        return servers

    @property
    def servers(self) -> list[str]:
        """Return list of DNS servers."""
        return self._data[ATTR_SERVERS]

    @servers.setter
    def servers(self, value: list[str]) -> None:
        """Return list of DNS servers."""
        self._data[ATTR_SERVERS] = value

    @property
    def latest_version(self) -> Optional[AwesomeVersion]:
        """Return latest version of CoreDNS."""
        return self.sys_updater.version_dns

    async def load(self) -> None:
        """Load DNS setup."""
        # Initialize CoreDNS Template
        try:
            self.resolv_template = jinja2.Template(RESOLV_TMPL.read_text())
        except OSError as err:
            _LOGGER.error("Can't read resolve.tmpl: %s", err)
        try:
            self.hosts_template = jinja2.Template(HOSTS_TMPL.read_text())
        except OSError as err:
            _LOGGER.error("Can't read hosts.tmpl: %s", err)

        # Check CoreDNS state
        self._init_hosts()
        try:
            # Evaluate Version if we lost this information
            if not self.version:
                self.version = await self.instance.get_latest_version()

            await self.instance.attach(version=self.version)
        except DockerError:
            _LOGGER.info(
                "No CoreDNS plugin Docker image %s found.", self.instance.image
            )

            # Install CoreDNS
            with suppress(CoreDNSError):
                await self.install()
        else:
            self.version = self.instance.version
            self.image = self.instance.image
            self.save_data()

        # Run CoreDNS
        with suppress(CoreDNSError):
            if not await self.instance.is_running():
                await self.start()

        # Update supervisor
        self._write_resolv(HOST_RESOLV)
        await self.sys_supervisor.check_connectivity()

    async def install(self) -> None:
        """Install CoreDNS."""
        _LOGGER.info("Running setup for CoreDNS plugin")
        while True:
            # read homeassistant tag and install it
            if not self.latest_version:
                await self.sys_updater.reload()

            if self.latest_version:
                with suppress(DockerError):
                    await self.instance.install(
                        self.latest_version, image=self.sys_updater.image_dns
                    )
                    break
            _LOGGER.warning("Error on install CoreDNS plugin. Retry in 30sec")
            await asyncio.sleep(30)

        _LOGGER.info("CoreDNS plugin now installed")
        self.version = self.instance.version
        self.image = self.sys_updater.image_dns
        self.save_data()

        # Init Hosts
        self.write_hosts()

    async def update(self, version: Optional[AwesomeVersion] = None) -> None:
        """Update CoreDNS plugin."""
        version = version or self.latest_version
        old_image = self.image

        if version == self.version:
            _LOGGER.warning("Version %s is already installed for CoreDNS", version)
            return

        # Update
        try:
            await self.instance.update(version, image=self.sys_updater.image_dns)
        except DockerError as err:
            raise CoreDNSUpdateError("CoreDNS update failed", _LOGGER.error) from err

        else:
            self.version = version
            self.image = self.sys_updater.image_dns
            self.save_data()

        # Cleanup
        with suppress(DockerError):
            await self.instance.cleanup(old_image=old_image)

        # Start CoreDNS
        await self.start()

    async def restart(self) -> None:
        """Restart CoreDNS plugin."""
        self._write_config()
        _LOGGER.info("Restarting CoreDNS plugin")
        try:
            await self.instance.restart()
        except DockerError as err:
            raise CoreDNSError(f"Can't start CoreDNS plugin", _LOGGER.error) from err

    async def start(self) -> None:
        """Run CoreDNS."""
        self._write_config()

        # Start Instance
        _LOGGER.info("Starting CoreDNS plugin")
        try:
            await self.instance.run()
        except DockerError as err:
            raise CoreDNSError("Can't start CoreDNS plugin", _LOGGER.error) from err

    async def stop(self) -> None:
        """Stop CoreDNS."""
        _LOGGER.info("Stopping CoreDNS plugin")
        try:
            await self.instance.stop()
        except DockerError as err:
            raise CoreDNSError("Can't stop CoreDNS plugin", _LOGGER.error) from err

    async def reset(self) -> None:
        """Reset DNS and hosts."""
        # Reset manually defined DNS
        self.servers.clear()
        self.save_data()

        # Resets hosts
        with suppress(OSError):
            self.hosts.unlink()
        self._init_hosts()

        # Reset loop protection
        self._loop = False

        await self.sys_addons.sync_dns()

    async def loop_detection(self) -> None:
        """Check if there was a loop found."""
        log = await self.instance.logs()

        # Check the log for loop plugin output
        if b"plugin/loop: Loop" in log:
            _LOGGER.error("Detected a DNS loop in local Network!")
            self._loop = True
            self.sys_resolution.create_issue(
                IssueType.DNS_LOOP,
                ContextType.PLUGIN,
                reference=self.slug,
                suggestions=[SuggestionType.EXECUTE_RESET],
            )
        else:
            self._loop = False

    def _write_config(self) -> None:
        """Write CoreDNS config."""
        debug: bool = self.sys_config.logging == LogLevel.DEBUG
        dns_servers: list[str] = []
        dns_locals: list[str] = []

        # Prepare DNS serverlist: Prio 1 Manual, Prio 2 Local, Prio 3 Fallback
        if not self._loop:
            dns_servers = self.servers
            dns_locals = self.locals
        else:
            _LOGGER.warning("Ignoring user DNS settings because of loop")

        # Print some usefully debug data
        _LOGGER.debug(
            "config-dns = %s, local-dns = %s , backup-dns = CloudFlare DoT / debug: %s",
            dns_servers,
            dns_locals,
            debug,
        )

        # Write config to plugin
        try:
            write_json_file(
                self.coredns_config,
                {
                    "servers": dns_servers,
                    "locals": dns_locals,
                    "debug": debug,
                },
            )
        except ConfigurationFileError as err:
            raise CoreDNSError(
                f"Can't update coredns config: {err}", _LOGGER.error
            ) from err

    def _init_hosts(self) -> None:
        """Import hosts entry."""
        # Generate Default
        self.add_host(IPv4Address("127.0.0.1"), ["localhost"], write=False)
        self.add_host(
            self.sys_docker.network.supervisor, ["hassio", "supervisor"], write=False
        )
        self.add_host(
            self.sys_docker.network.gateway,
            ["homeassistant", "home-assistant"],
            write=False,
        )
        self.add_host(self.sys_docker.network.dns, ["dns"], write=False)
        self.add_host(self.sys_docker.network.observer, ["observer"], write=False)

    def write_hosts(self) -> None:
        """Write hosts from memory to file."""
        # Generate config file
        data = self.hosts_template.render(entries=self._hosts)

        try:
            self.hosts.write_text(data, encoding="utf-8")
        except OSError as err:
            raise CoreDNSError(f"Can't update hosts: {err}", _LOGGER.error) from err

    def add_host(self, ipv4: IPv4Address, names: list[str], write: bool = True) -> None:
        """Add a new host entry."""
        if not ipv4 or ipv4 == IPv4Address("0.0.0.0"):
            return

        hostnames: list[str] = []
        for name in names:
            hostnames.append(name)
            hostnames.append(f"{name}.{DNS_SUFFIX}")

        # Generate host entry
        entry = HostEntry(ipv4, hostnames)
        old = self._search_host(hostnames)

        if old:
            _LOGGER.debug("Update Host entry %s -> %s", ipv4, hostnames)
            self._hosts.remove(old)
        else:
            _LOGGER.debug("Add Host entry %s -> %s", ipv4, hostnames)
        self._hosts.append(entry)

        # Update hosts file
        if write:
            self.write_hosts()

    def delete_host(self, host: str, write: bool = True) -> None:
        """Remove a entry from hosts."""
        entry = self._search_host([host])
        if not entry:
            return

        _LOGGER.debug("Removing host entry %s - %s", entry.ip_address, entry.names)
        self._hosts.remove(entry)

        # Update hosts file
        if write:
            self.write_hosts()

    def _search_host(self, names: list[str]) -> Optional[HostEntry]:
        """Search a host entry."""
        for entry in self._hosts:
            for name in names:
                if name not in entry.names:
                    continue
                return entry
        return None

    async def stats(self) -> DockerStats:
        """Return stats of CoreDNS."""
        try:
            return await self.instance.stats()
        except DockerError as err:
            raise CoreDNSError() from err

    async def repair(self) -> None:
        """Repair CoreDNS plugin."""
        if await self.instance.exists():
            return

        _LOGGER.info("Repairing CoreDNS %s", self.version)
        try:
            await self.instance.install(self.version)
        except DockerError as err:
            _LOGGER.error("Repair of CoreDNS failed")
            self.sys_capture_exception(err)

    def _write_resolv(self, resolv_conf: Path) -> None:
        """Update/Write resolv.conf file."""
        nameservers = [str(self.sys_docker.network.dns), "127.0.0.11"]

        # Read resolv config
        data = self.resolv_template.render(servers=nameservers)

        # Write config back to resolv
        try:
            resolv_conf.write_text(data)
        except OSError as err:
            _LOGGER.warning("Can't write/update %s: %s", resolv_conf, err)
            return

        _LOGGER.info("Updated %s", resolv_conf)
