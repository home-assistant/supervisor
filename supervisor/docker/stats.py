"""Calc and represent docker stats data."""
from contextlib import suppress


class DockerStats:
    """Hold stats data from container inside."""

    def __init__(self, stats):
        """Initialize Docker stats."""
        self._cpu = 0.0
        self._network_rx = 0
        self._network_tx = 0
        self._blk_read = 0
        self._blk_write = 0

        try:
            self._memory_usage = stats["memory_stats"]["usage"]
            self._memory_limit = stats["memory_stats"]["limit"]
        except KeyError:
            self._memory_usage = 0
            self._memory_limit = 0

        # Calculate percent usage
        if self._memory_limit != 0:
            self._memory_percent = self._memory_usage / self._memory_limit * 100.0
        else:
            self._memory_percent = 0

        with suppress(KeyError):
            self._calc_cpu_percent(stats)

        with suppress(KeyError):
            self._calc_network(stats["networks"])

        with suppress(KeyError):
            self._calc_block_io(stats["blkio_stats"])

    def _calc_cpu_percent(self, stats):
        """Calculate CPU percent."""
        cpu_delta = (
            stats["cpu_stats"]["cpu_usage"]["total_usage"]
            - stats["precpu_stats"]["cpu_usage"]["total_usage"]
        )
        system_delta = (
            stats["cpu_stats"]["system_cpu_usage"]
            - stats["precpu_stats"]["system_cpu_usage"]
        )

        if system_delta > 0.0 and cpu_delta > 0.0:
            self._cpu = (cpu_delta / system_delta) * 100.0
        else:
            self._cpu = 0.0

    def _calc_network(self, networks):
        """Calculate Network IO stats."""
        for _, stats in networks.items():
            self._network_rx += stats["rx_bytes"]
            self._network_tx += stats["tx_bytes"]

    def _calc_block_io(self, blkio):
        """Calculate block IO stats."""
        for stats in blkio["io_service_bytes_recursive"]:
            if stats["op"] == "Read":
                self._blk_read += stats["value"]
            elif stats["op"] == "Write":
                self._blk_write += stats["value"]

    @property
    def cpu_percent(self):
        """Return CPU percent."""
        return round(self._cpu, 2)

    @property
    def memory_usage(self):
        """Return memory usage."""
        return self._memory_usage

    @property
    def memory_limit(self):
        """Return memory limit."""
        return self._memory_limit

    @property
    def memory_percent(self):
        """Return memory usage in percent."""
        return round(self._memory_percent, 2)

    @property
    def network_rx(self):
        """Return network rx stats."""
        return self._network_rx

    @property
    def network_tx(self):
        """Return network rx stats."""
        return self._network_tx

    @property
    def blk_read(self):
        """Return block IO read stats."""
        return self._blk_read

    @property
    def blk_write(self):
        """Return block IO write stats."""
        return self._blk_write
