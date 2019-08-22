"""Home Assistant control object."""
import asyncio
import logging
from contextlib import suppress
from ipaddress import IPv4Address
from pathlib import Path
from string import Template
from typing import Awaitable, List, Optional

import attr

from .const import ATTR_SERVERS, ATTR_VERSION, DNS_SERVERS, FILE_HASSIO_DNS, DNS_SUFFIX
from .coresys import CoreSys, CoreSysAttributes
from .docker.dns import DockerDNS
from .docker.stats import DockerStats
from .exceptions import CoreDNSError, CoreDNSUpdateError, DockerAPIError
from .misc.forwarder import DNSForward
from .utils.json import JsonConfig
from .validate import SCHEMA_DNS_CONFIG

_LOGGER: logging.Logger = logging.getLogger(__name__)

COREDNS_TMPL: Path = Path(__file__).parents[0].joinpath("data/coredns.tmpl")
RESOLV_CONF: Path = Path("/etc/resolv.conf")


@attr.s
class HostEntry:
    """Single entry in hosts."""

    ip_address: IPv4Address = attr.ib()
    names: List[str] = attr.ib()


class CoreDNS(JsonConfig, CoreSysAttributes):
    """Home Assistant core object for handle it."""

    def __init__(self, coresys: CoreSys):
        """Initialize hass object."""
        super().__init__(FILE_HASSIO_DNS, SCHEMA_DNS_CONFIG)
        self.coresys: CoreSys = coresys
        self.instance: DockerDNS = DockerDNS(coresys)
        self.forwarder: DNSForward = DNSForward()

        self._hosts: List[HostEntry] = []

    @property
    def corefile(self) -> Path:
        """Return Path to corefile."""
        return Path(self.sys_config.path_dns, "corefile")

    @property
    def hosts(self) -> Path:
        """Return Path to corefile."""
        return Path(self.sys_config.path_dns, "hosts")

    @property
    def servers(self) -> List[str]:
        """Return list of DNS servers."""
        return self._data[ATTR_SERVERS]

    @servers.setter
    def servers(self, value: List[str]) -> None:
        """Return list of DNS servers."""
        self._data[ATTR_SERVERS] = value

    @property
    def version(self) -> Optional[str]:
        """Return current version of DNS."""
        return self._data.get(ATTR_VERSION)

    @version.setter
    def version(self, value: str) -> None:
        """Return current version of DNS."""
        self._data[ATTR_VERSION] = value

    @property
    def latest_version(self) -> Optional[str]:
        """Return latest version of CoreDNS."""
        return self.sys_updater.version_dns

    @property
    def in_progress(self) -> bool:
        """Return True if a task is in progress."""
        return self.instance.in_progress

    @property
    def need_update(self) -> bool:
        """Return True if an update is available."""
        return self.version != self.latest_version

    async def load(self) -> None:
        """Load DNS setup."""
        self._init_hosts()

        # Check CoreDNS state
        try:
            # Evaluate Version if we lost this information
            if not self.version:
                self.version = await self.instance.get_latest_version(key=int)

            await self.instance.attach(tag=self.version)
        except DockerAPIError:
            _LOGGER.info(
                "No CoreDNS plugin Docker image %s found.", self.instance.image
            )

            # Install CoreDNS
            with suppress(CoreDNSError):
                await self.install()
        else:
            self.version = self.instance.version
            self.save_data()

        # Start DNS forwarder
        self.sys_create_task(self.forwarder.start(self.sys_docker.network.dns))

        with suppress(CoreDNSError):
            self._update_local_resolv()

        # Start is not Running
        if await self.instance.is_running():
            await self.restart()
        else:
            await self.start()

    async def unload(self) -> None:
        """Unload DNS forwarder."""
        await self.forwarder.stop()

    async def install(self) -> None:
        """Install CoreDNS."""
        _LOGGER.info("Setup CoreDNS plugin")
        while True:
            # read homeassistant tag and install it
            if not self.latest_version:
                await self.sys_updater.reload()

            if self.latest_version:
                with suppress(DockerAPIError):
                    await self.instance.install(self.latest_version)
                    break
            _LOGGER.warning("Error on install CoreDNS plugin. Retry in 30sec")
            await asyncio.sleep(30)

        _LOGGER.info("CoreDNS plugin now installed")
        self.version = self.instance.version
        self.save_data()

        # Init Hosts / Run server
        self.write_hosts()
        await self.start()

    async def update(self, version: Optional[str] = None) -> None:
        """Update CoreDNS plugin."""
        version = version or self.latest_version

        if version == self.version:
            _LOGGER.warning("Version %s is already installed for CoreDNS", version)
            return

        try:
            await self.instance.update(version)
        except DockerAPIError:
            _LOGGER.error("CoreDNS update fails")
            raise CoreDNSUpdateError() from None
        else:
            # Cleanup
            with suppress(DockerAPIError):
                await self.instance.cleanup()

        self.version = version
        self.save_data()

        # Start CoreDNS
        await self.start()

    async def restart(self) -> None:
        """Restart CoreDNS plugin."""
        self._write_corefile()
        with suppress(DockerAPIError):
            await self.instance.restart()

    async def start(self) -> None:
        """Run CoreDNS."""
        self._write_corefile()

        # Start Instance
        _LOGGER.info("Start CoreDNS plugin")
        try:
            await self.instance.run()
        except DockerAPIError:
            _LOGGER.error("Can't start CoreDNS plugin")
            raise CoreDNSError() from None

    async def reset(self) -> None:
        """Reset Config / Hosts."""
        self.servers = DNS_SERVERS

        # Resets hosts
        with suppress(OSError):
            self.hosts.unlink()
        self._init_hosts()

        await self.sys_addons.sync_dns()

    def _write_corefile(self) -> None:
        """Write CoreDNS config."""
        try:
            corefile_template: Template = Template(COREDNS_TMPL.read_text())
        except OSError as err:
            _LOGGER.error("Can't read coredns template file: %s", err)
            raise CoreDNSError() from None

        # Generate config file
        dns_servers = self.servers + list(set(DNS_SERVERS) - set(self.servers))
        data = corefile_template.safe_substitute(servers=" ".join(dns_servers))

        try:
            self.corefile.write_text(data)
        except OSError as err:
            _LOGGER.error("Can't update corefile: %s", err)
            raise CoreDNSError() from None

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

    def write_hosts(self) -> None:
        """Write hosts from memory to file."""
        try:
            with self.hosts.open("w") as hosts:
                for entry in self._hosts:
                    hosts.write(f"{entry.ip_address!s} {' '.join(entry.names)}\n")
        except OSError as err:
            _LOGGER.error("Can't write hosts file: %s", err)
            raise CoreDNSError() from None

    def add_host(self, ipv4: IPv4Address, names: List[str], write: bool = True) -> None:
        """Add a new host entry."""
        if not ipv4 or ipv4 == IPv4Address("0.0.0.0"):
            return

        hostnames: List[str] = []
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

        # No match on hosts
        if not entry:
            _LOGGER.debug("Can't remove Host entry: %s", host)
            return

        _LOGGER.debug("Remove Host entry %s - %s", entry.ip_address, entry.names)
        self._hosts.remove(entry)

        # Update hosts file
        if write:
            self.write_hosts()

    def _search_host(self, names: List[str]) -> Optional[HostEntry]:
        """Search a host entry."""
        for entry in self._hosts:
            for name in names:
                if name not in entry.names:
                    continue
                return entry

    def logs(self) -> Awaitable[bytes]:
        """Get CoreDNS docker logs.

        Return Coroutine.
        """
        return self.instance.logs()

    async def stats(self) -> DockerStats:
        """Return stats of CoreDNS."""
        try:
            return await self.instance.stats()
        except DockerAPIError:
            raise CoreDNSError() from None

    def is_running(self) -> Awaitable[bool]:
        """Return True if Docker container is running.

        Return a coroutine.
        """
        return self.instance.is_running()

    def is_fails(self) -> Awaitable[bool]:
        """Return True if a Docker container is fails state.

        Return a coroutine.
        """
        return self.instance.is_fails()

    async def repair(self) -> None:
        """Repair CoreDNS plugin."""
        if await self.instance.exists():
            return

        _LOGGER.info("Repair CoreDNS %s", self.version)
        try:
            await self.instance.install(self.version)
        except DockerAPIError:
            _LOGGER.error("Repairing of CoreDNS fails")

    def _update_local_resolv(self) -> None:
        """Update local resolv file."""
        resolv_lines: List[str] = []
        nameserver = f"nameserver {self.sys_docker.network.dns!s}"

        # Read resolv config
        try:
            with RESOLV_CONF.open("r") as resolv:
                for line in resolv.readlines():
                    if not line:
                        continue
                    resolv_lines.append(line.strip())
        except OSError as err:
            _LOGGER.warning("Can't read local resolv: %s", err)
            raise CoreDNSError() from None

        if nameserver in resolv_lines:
            return
        _LOGGER.info("Update resolv from Supervisor")

        # Write config back to resolv
        resolv_lines.append(nameserver)
        try:
            with RESOLV_CONF.open("w") as resolv:
                for line in resolv_lines:
                    resolv.write(f"{line}\n")
        except OSError as err:
            _LOGGER.warning("Can't write local resolv: %s", err)
            raise CoreDNSError() from None
