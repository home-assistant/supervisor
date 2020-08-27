"""Test gdbus gvariant parser."""
from supervisor.utils.gdbus import DBus


def test_simple_return():
    """Test Simple return value."""
    raw = "(objectpath '/org/freedesktop/systemd1/job/35383',)"

    # parse data
    data = DBus.parse_gvariant(raw)

    assert data == ["/org/freedesktop/systemd1/job/35383"]


def test_get_property():
    """Test Property parsing."""
    raw = "({'Hostname': <'hassio'>, 'StaticHostname': <'hassio'>, 'PrettyHostname': <''>, 'IconName': <'computer-embedded'>, 'Chassis': <'embedded'>, 'Deployment': <'production'>, 'Location': <''>, 'KernelName': <'Linux'>, 'KernelRelease': <'4.14.98-v7'>, 'KernelVersion': <'#1 SMP Sat May 11 02:17:06 UTC 2019'>, 'OperatingSystemPrettyName': <'HassOS 2.12'>, 'OperatingSystemCPEName': <'cpe:2.3:o:home_assistant:hassos:2.12:*:production:*:*:*:rpi3:*'>, 'HomeURL': <'https://hass.io/'>},)"

    # parse data
    data = DBus.parse_gvariant(raw)

    assert data[0] == {
        "Hostname": "hassio",
        "StaticHostname": "hassio",
        "PrettyHostname": "",
        "IconName": "computer-embedded",
        "Chassis": "embedded",
        "Deployment": "production",
        "Location": "",
        "KernelName": "Linux",
        "KernelRelease": "4.14.98-v7",
        "KernelVersion": "#1 SMP Sat May 11 02:17:06 UTC 2019",
        "OperatingSystemPrettyName": "HassOS 2.12",
        "OperatingSystemCPEName": "cpe:2.3:o:home_assistant:hassos:2.12:*:production:*:*:*:rpi3:*",
        "HomeURL": "https://hass.io/",
    }


def test_systemd_unitlist_simple():
    """Test Systemd Unit list simple."""
    raw = "([('systemd-remount-fs.service', 'Remount Root and Kernel File Systems', 'loaded', 'active', 'exited', '', objectpath '/org/freedesktop/systemd1/unit/systemd_2dremount_2dfs_2eservice', uint32 0, '', objectpath '/'), ('sys-subsystem-net-devices-veth5714b4e.device', '/sys/subsystem/net/devices/veth5714b4e', 'loaded', 'active', 'plugged', '', '/org/freedesktop/systemd1/unit/sys_2dsubsystem_2dnet_2ddevices_2dveth5714b4e_2edevice', 0, '', '/'), ('rauc.service', 'Rauc Update Service', 'loaded', 'active', 'running', '', '/org/freedesktop/systemd1/unit/rauc_2eservice', 0, '', '/'), ('mnt-data-docker-overlay2-7493c48dd99ab0e68420e3317d93711630dd55a76d4f2a21863a220031203ac2-merged.mount', '/mnt/data/docker/overlay2/7493c48dd99ab0e68420e3317d93711630dd55a76d4f2a21863a220031203ac2/merged', 'loaded', 'active', 'mounted', '', '/org/freedesktop/systemd1/unit/mnt_2ddata_2ddocker_2doverlay2_2d7493c48dd99ab0e68420e3317d93711630dd55a76d4f2a21863a220031203ac2_2dmerged_2emount', 0, '', '/'), ('hassos-hardware.target', 'HassOS hardware targets', 'loaded', 'active', 'active', '', '/org/freedesktop/systemd1/unit/hassos_2dhardware_2etarget', 0, '', '/'), ('dev-zram1.device', '/dev/zram1', 'loaded', 'active', 'plugged', 'sys-devices-virtual-block-zram1.device', '/org/freedesktop/systemd1/unit/dev_2dzram1_2edevice', 0, '', '/'), ('sys-subsystem-net-devices-hassio.device', '/sys/subsystem/net/devices/hassio', 'loaded', 'active', 'plugged', '', '/org/freedesktop/systemd1/unit/sys_2dsubsystem_2dnet_2ddevices_2dhassio_2edevice', 0, '', '/'), ('cryptsetup.target', 'cryptsetup.target', 'not-found', 'inactive', 'dead', '', '/org/freedesktop/systemd1/unit/cryptsetup_2etarget', 0, '', '/'), ('sys-devices-virtual-net-vethd256dfa.device', '/sys/devices/virtual/net/vethd256dfa', 'loaded', 'active', 'plugged', '', '/org/freedesktop/systemd1/unit/sys_2ddevices_2dvirtual_2dnet_2dvethd256dfa_2edevice', 0, '', '/'), ('network-pre.target', 'Network (Pre)', 'loaded', 'inactive', 'dead', '', '/org/freedesktop/systemd1/unit/network_2dpre_2etarget', 0, '', '/'), ('sys-devices-virtual-net-veth5714b4e.device', '/sys/devices/virtual/net/veth5714b4e', 'loaded', 'active', 'plugged', '', '/org/freedesktop/systemd1/unit/sys_2ddevices_2dvirtual_2dnet_2dveth5714b4e_2edevice', 0, '', '/'), ('sys-kernel-debug.mount', 'Kernel Debug File System', 'loaded', 'active', 'mounted', '', '/org/freedesktop/systemd1/unit/sys_2dkernel_2ddebug_2emount', 0, '', '/'), ('slices.target', 'Slices', 'loaded', 'active', 'active', '', '/org/freedesktop/systemd1/unit/slices_2etarget', 0, '', '/'), ('etc-NetworkManager-system\x2dconnections.mount', 'NetworkManager persistent system connections', 'loaded', 'active', 'mounted', '', '/org/freedesktop/systemd1/unit/etc_2dNetworkManager_2dsystem_5cx2dconnections_2emount', 0, '', '/'), ('run-docker-netns-26ede3178729.mount', '/run/docker/netns/26ede3178729', 'loaded', 'active', 'mounted', '', '/org/freedesktop/systemd1/unit/run_2ddocker_2dnetns_2d26ede3178729_2emount', 0, '', '/'), ('dev-disk-by\x2dpath-platform\x2d3f202000.mmc\x2dpart2.device', '/dev/disk/by-path/platform-3f202000.mmc-part2', 'loaded', 'active', 'plugged', 'sys-devices-platform-soc-3f202000.mmc-mmc_host-mmc0-mmc0:e624-block-mmcblk0-mmcblk0p2.device', '/org/freedesktop/systemd1/unit/dev_2ddisk_2dby_5cx2dpath_2dplatform_5cx2d3f202000_2emmc_5cx2dpart2_2edevice', 0, '', '/')],)"

    # parse data
    data = DBus.parse_gvariant(raw)

    assert data == [
        [
            [
                "systemd-remount-fs.service",
                "Remount Root and Kernel File Systems",
                "loaded",
                "active",
                "exited",
                "",
                "/org/freedesktop/systemd1/unit/systemd_2dremount_2dfs_2eservice",
                0,
                "",
                "/",
            ],
            [
                "sys-subsystem-net-devices-veth5714b4e.device",
                "/sys/subsystem/net/devices/veth5714b4e",
                "loaded",
                "active",
                "plugged",
                "",
                "/org/freedesktop/systemd1/unit/sys_2dsubsystem_2dnet_2ddevices_2dveth5714b4e_2edevice",
                0,
                "",
                "/",
            ],
            [
                "rauc.service",
                "Rauc Update Service",
                "loaded",
                "active",
                "running",
                "",
                "/org/freedesktop/systemd1/unit/rauc_2eservice",
                0,
                "",
                "/",
            ],
            [
                "mnt-data-docker-overlay2-7493c48dd99ab0e68420e3317d93711630dd55a76d4f2a21863a220031203ac2-merged.mount",
                "/mnt/data/docker/overlay2/7493c48dd99ab0e68420e3317d93711630dd55a76d4f2a21863a220031203ac2/merged",
                "loaded",
                "active",
                "mounted",
                "",
                "/org/freedesktop/systemd1/unit/mnt_2ddata_2ddocker_2doverlay2_2d7493c48dd99ab0e68420e3317d93711630dd55a76d4f2a21863a220031203ac2_2dmerged_2emount",
                0,
                "",
                "/",
            ],
            [
                "hassos-hardware.target",
                "HassOS hardware targets",
                "loaded",
                "active",
                "active",
                "",
                "/org/freedesktop/systemd1/unit/hassos_2dhardware_2etarget",
                0,
                "",
                "/",
            ],
            [
                "dev-zram1.device",
                "/dev/zram1",
                "loaded",
                "active",
                "plugged",
                "sys-devices-virtual-block-zram1.device",
                "/org/freedesktop/systemd1/unit/dev_2dzram1_2edevice",
                0,
                "",
                "/",
            ],
            [
                "sys-subsystem-net-devices-hassio.device",
                "/sys/subsystem/net/devices/hassio",
                "loaded",
                "active",
                "plugged",
                "",
                "/org/freedesktop/systemd1/unit/sys_2dsubsystem_2dnet_2ddevices_2dhassio_2edevice",
                0,
                "",
                "/",
            ],
            [
                "cryptsetup.target",
                "cryptsetup.target",
                "not-found",
                "inactive",
                "dead",
                "",
                "/org/freedesktop/systemd1/unit/cryptsetup_2etarget",
                0,
                "",
                "/",
            ],
            [
                "sys-devices-virtual-net-vethd256dfa.device",
                "/sys/devices/virtual/net/vethd256dfa",
                "loaded",
                "active",
                "plugged",
                "",
                "/org/freedesktop/systemd1/unit/sys_2ddevices_2dvirtual_2dnet_2dvethd256dfa_2edevice",
                0,
                "",
                "/",
            ],
            [
                "network-pre.target",
                "Network (Pre)",
                "loaded",
                "inactive",
                "dead",
                "",
                "/org/freedesktop/systemd1/unit/network_2dpre_2etarget",
                0,
                "",
                "/",
            ],
            [
                "sys-devices-virtual-net-veth5714b4e.device",
                "/sys/devices/virtual/net/veth5714b4e",
                "loaded",
                "active",
                "plugged",
                "",
                "/org/freedesktop/systemd1/unit/sys_2ddevices_2dvirtual_2dnet_2dveth5714b4e_2edevice",
                0,
                "",
                "/",
            ],
            [
                "sys-kernel-debug.mount",
                "Kernel Debug File System",
                "loaded",
                "active",
                "mounted",
                "",
                "/org/freedesktop/systemd1/unit/sys_2dkernel_2ddebug_2emount",
                0,
                "",
                "/",
            ],
            [
                "slices.target",
                "Slices",
                "loaded",
                "active",
                "active",
                "",
                "/org/freedesktop/systemd1/unit/slices_2etarget",
                0,
                "",
                "/",
            ],
            [
                "etc-NetworkManager-system-connections.mount",
                "NetworkManager persistent system connections",
                "loaded",
                "active",
                "mounted",
                "",
                "/org/freedesktop/systemd1/unit/etc_2dNetworkManager_2dsystem_5cx2dconnections_2emount",
                0,
                "",
                "/",
            ],
            [
                "run-docker-netns-26ede3178729.mount",
                "/run/docker/netns/26ede3178729",
                "loaded",
                "active",
                "mounted",
                "",
                "/org/freedesktop/systemd1/unit/run_2ddocker_2dnetns_2d26ede3178729_2emount",
                0,
                "",
                "/",
            ],
            [
                "dev-disk-by-path-platform-3f202000.mmc-part2.device",
                "/dev/disk/by-path/platform-3f202000.mmc-part2",
                "loaded",
                "active",
                "plugged",
                "sys-devices-platform-soc-3f202000.mmc-mmc_host-mmc0-mmc0:e624-block-mmcblk0-mmcblk0p2.device",
                "/org/freedesktop/systemd1/unit/dev_2ddisk_2dby_5cx2dpath_2dplatform_5cx2d3f202000_2emmc_5cx2dpart2_2edevice",
                0,
                "",
                "/",
            ],
        ]
    ]


def test_systemd_unitlist_complex():
    """Test Systemd Unit list simple."""
    raw = "([('systemd-remount-fs.service', 'Remount Root and \"Kernel File Systems\"', 'loaded', 'active', 'exited', '', objectpath '/org/freedesktop/systemd1/unit/systemd_2dremount_2dfs_2eservice', uint32 0, '', objectpath '/'), ('sys-subsystem-net-devices-veth5714b4e.device', '/sys/subsystem/net/devices/veth5714b4e for \" is', 'loaded', 'active', 'plugged', '', '/org/freedesktop/systemd1/unit/sys_2dsubsystem_2dnet_2ddevices_2dveth5714b4e_2edevice', 0, '', '/')],)"

    # parse data
    data = DBus.parse_gvariant(raw)

    assert data == [
        [
            [
                "systemd-remount-fs.service",
                'Remount Root and "Kernel File Systems"',
                "loaded",
                "active",
                "exited",
                "",
                "/org/freedesktop/systemd1/unit/systemd_2dremount_2dfs_2eservice",
                0,
                "",
                "/",
            ],
            [
                "sys-subsystem-net-devices-veth5714b4e.device",
                '/sys/subsystem/net/devices/veth5714b4e for " is',
                "loaded",
                "active",
                "plugged",
                "",
                "/org/freedesktop/systemd1/unit/sys_2dsubsystem_2dnet_2ddevices_2dveth5714b4e_2edevice",
                0,
                "",
                "/",
            ],
        ]
    ]


def test_networkmanager_dns_properties():
    """Test NetworkManager DNS properties."""
    raw = "({'Mode': <'default'>, 'RcManager': <'file'>, 'Configuration': <[{'nameservers': <['192.168.23.30']>, 'domains': <['syshack.local']>, 'interface': <'eth0'>, 'priority': <100>, 'vpn': <false>}]>},)"

    # parse data
    data = DBus.parse_gvariant(raw)

    assert data == [
        {
            "Mode": "default",
            "RcManager": "file",
            "Configuration": [
                {
                    "nameservers": ["192.168.23.30"],
                    "domains": ["syshack.local"],
                    "interface": "eth0",
                    "priority": 100,
                    "vpn": False,
                }
            ],
        }
    ]


def test_networkmanager_dns_properties_empty():
    """Test NetworkManager DNS properties."""
    raw = "({'Mode': <'default'>, 'RcManager': <'resolvconf'>, 'Configuration': <@aa{sv} []>},)"

    # parse data
    data = DBus.parse_gvariant(raw)

    assert data == [{"Mode": "default", "RcManager": "resolvconf", "Configuration": []}]


def test_networkmanager_binary_data():
    """Test NetworkManager Binary datastrings."""
    raw = "({'802-11-wireless': {'mac-address-blacklist': <@as []>, 'mode': <'infrastructure'>, 'security': <'802-11-wireless-security'>, 'seen-bssids': <['7C:2E:BD:98:1B:06']>, 'ssid': <[byte 0x4e, 0x45, 0x54, 0x54]>}, 'connection': {'id': <'NETT'>, 'interface-name': <'wlan0'>, 'permissions': <@as []>, 'timestamp': <uint64 1598526799>, 'type': <'802-11-wireless'>, 'uuid': <'13f9af79-a6e9-4e07-9353-165ad57bf1a8'>}, 'ipv6': {'address-data': <@aa{sv} []>, 'addresses': <@a(ayuay) []>, 'dns': <@aay []>, 'dns-search': <@as []>, 'method': <'auto'>, 'route-data': <@aa{sv} []>, 'routes': <@a(ayuayu) []>}, '802-11-wireless-security': {'auth-alg': <'open'>, 'key-mgmt': <'wpa-psk'>}, 'ipv4': {'address-data': <@aa{sv} []>, 'addresses': <@aau []>, 'dns': <@au []>, 'dns-search': <@as []>, 'method': <'auto'>, 'route-data': <@aa{sv} []>, 'routes': <@aau []>}, 'proxy': {}},)"

    data = DBus.parse_gvariant(raw)

    assert data == [
        {
            "802-11-wireless": {
                "mac-address-blacklist": [],
                "mode": "infrastructure",
                "security": "802-11-wireless-security",
                "seen-bssids": ["7C:2E:BD:98:1B:06"],
                "ssid": "NETT",
            },
            "connection": {
                "id": "NETT",
                "interface-name": "wlan0",
                "permissions": [],
                "timestamp": 1598526799,
                "type": "802-11-wireless",
                "uuid": "13f9af79-a6e9-4e07-9353-165ad57bf1a8",
            },
            "ipv6": {
                "address-data": [],
                "addresses": [],
                "dns": [],
                "dns-search": [],
                "method": "auto",
                "route-data": [],
                "routes": [],
            },
            "802-11-wireless-security": {"auth-alg": "open", "key-mgmt": "wpa-psk"},
            "ipv4": {
                "address-data": [],
                "addresses": [],
                "dns": [],
                "dns-search": [],
                "method": "auto",
                "route-data": [],
                "routes": [],
            },
            "proxy": {},
        }
    ]
