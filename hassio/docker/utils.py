"""HassIO docker utilitys."""
import logging

_LOGGER = logging.getLogger(__name__)


# pylint: disable=protected-access
def docker_process(method):
    """Wrap function with only run once."""
    async def wrap_api(api, *args, **kwargs):
        """Return api wrapper."""
        if api.lock.locked():
            _LOGGER.error(
                "Can't excute %s while a task is in progress", method.__name__)
            return False

        async with api.lock:
            return await method(api, *args, **kwargs)

    return wrap_api


def calc_cpu_percent(stats):
    """Calculate CPU percent."""
    percent = 0.0

    cpu_delta = stats['cpu_stats']['cpu_usage']['total_usage'] - \
        stats['precpu_stats']['cpu_usage']['total_usage']
    system_delta = stats['cpu_stats']['system_cpu_usage'] - \
        stats['precpu_stats']['system_cpu_usage']

    if system_delta > 0.0 and cpu_delta > 0.0:
        percent = (cpu_delta / system_delta) * \
            len(stats['cpu_stats']['cpu_usage']['percpu_usage']) * 100.0

    return percent


def calc_network(networks):
    """Calculate Network IO stats."""
    rx = tx = 0

    for _, stats in networks.items():
        rx += stats['rx_bytes']
        tx += stats['tx_bytes']

    return (rx, tx)
