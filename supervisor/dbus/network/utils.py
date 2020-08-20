"""Network utils."""
from ipaddress import ip_address

# Return a 32bit representation of a IP Address


def ip2int(address: str) -> int:
    """Return a 32bit representation for a IP address."""
    return int(ip_address(".".join(address.split(".")[::-1])))


def int2ip(bitaddress: int) -> int:
    """Return a IP Address object from a 32bit representation."""
    return ip_address(
        ".".join([str(bitaddress >> (i << 3) & 0xFF) for i in range(0, 4)])
    )
