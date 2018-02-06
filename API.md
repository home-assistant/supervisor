# Hass.io Server

## Hass.io RESTful API

Interface for Home Assistant to control things from supervisor.

On error / Code 400:

```json
{
    "result": "error",
    "message": ""
}
```

On success / Code 200:

```json
{
    "result": "ok",
    "data": { }
}
```

For access to API you need set the `X-HASSIO-KEY` they will be available for Add-ons/HomeAssistant with envoriment `HASSIO_TOKEN`.

### Hass.io

- GET `/supervisor/ping`
- GET `/supervisor/info`

The addons from `addons` are only installed one.

```json
{
    "version": "INSTALL_VERSION",
    "last_version": "LAST_VERSION",
    "arch": "armhf|aarch64|i386|amd64",
    "beta_channel": "true|false",
    "timezone": "TIMEZONE",
    "wait_boot": "int",
    "addons": [
        {
            "name": "xy bla",
            "slug": "xy",
            "description": "description",
            "repository": "12345678|null",
            "version": "LAST_VERSION",
            "installed": "INSTALL_VERSION",
            "icon": "bool",
            "logo": "bool",
            "state": "started|stopped",
        }
    ],
    "addons_repositories": [
        "REPO_URL"
    ]
}
```

- POST `/supervisor/update`

Optional:

```json
{
    "version": "VERSION"
}
```

- POST `/supervisor/options`

```json
{
    "beta_channel": "true|false",
    "timezone": "TIMEZONE",
    "wait_boot": "int",
    "addons_repositories": [
        "REPO_URL"
    ]
}
```

- POST `/supervisor/reload`

Reload addons/version.

- GET `/supervisor/logs`

Output is the raw docker log.

- GET `/supervisor/stats`
```json
{
    "cpu_percent": 0.0,
    "memory_usage": 283123,
    "memory_limit": 329392,
    "network_tx": 0,
    "network_rx": 0,
    "blk_read": 0,
    "blk_write": 0
}
```

### Snapshot

- GET `/snapshots`

```json
{
    "snapshots": [
        {
            "slug": "SLUG",
            "date": "ISO",
            "name": "Custom name",
            "type": "full|partial"
        }
    ]
}
```

- POST `/snapshots/reload`

- POST `/snapshots/new/full`

```json
{
    "name": "Optional"
}
```

- POST `/snapshots/new/partial`

```json
{
    "name": "Optional",
    "addons": ["ADDON_SLUG"],
    "folders": ["FOLDER_NAME"]
}
```

- POST `/snapshots/reload`

- GET `/snapshots/{slug}/info`

```json
{
    "slug": "SNAPSHOT ID",
    "type": "full|partial",
    "name": "custom snapshot name / description",
    "date": "ISO",
    "size": "SIZE_IN_MB",
    "homeassistant": "version",
    "addons": [
        {
            "slug": "ADDON_SLUG",
            "name": "NAME",
            "version": "INSTALLED_VERSION"
        }
    ],
    "repositories": ["URL"],
    "folders": ["NAME"]
}
```

- POST `/snapshots/{slug}/remove`
- POST `/snapshots/{slug}/restore/full`
- POST `/snapshots/{slug}/restore/partial`

```json
{
    "homeassistant": "bool",
    "addons": ["ADDON_SLUG"],
    "folders": ["FOLDER_NAME"]
}
```

### Host

- POST `/host/reload`
- POST `/host/shutdown`
- POST `/host/reboot`
- GET `/host/info`

```json
{
    "type": "",
    "version": "",
    "last_version": "",
    "features": ["shutdown", "reboot", "update", "hostname", "network_info", "network_control"],
    "hostname": "",
    "os": "",
    "audio": {
        "input": "0,0",
        "output": "0,0"
    }
}
```

- POST `/host/options`

```json
{
    "audio_input": "0,0",
    "audio_output": "0,0"
}
```

- POST `/host/update`

Optional:

```json
{
    "version": "VERSION"
}
```

- GET `/host/hardware`
```json
{
    "serial": ["/dev/xy"],
    "input": ["Input device name"],
    "disk": ["/dev/sdax"],
    "gpio": ["gpiochip0", "gpiochip100"],
    "audio": {
        "CARD_ID": {
            "name": "xy",
            "type": "microphone",
            "devices": {
                "DEV_ID": "type of device"
            }
        }
    }
}
```

- POST `/host/reload`

### Network

- GET `/network/info`

```json
{
    "hostname": ""
}
```

- POST `/network/options`

```json
{
    "hostname": "",
}
```

### Home Assistant

- GET `/homeassistant/info`

```json
{
    "version": "INSTALL_VERSION",
    "last_version": "LAST_VERSION",
    "image": "str",
    "custom": "bool -> if custom image",
    "boot": "bool",
    "port": 8123,
    "ssl": "bool",
    "watchdog": "bool"
}
```

- POST `/homeassistant/update`

Optional:

```json
{
    "version": "VERSION"
}
```

- GET `/homeassistant/logs`

Output is the raw Docker log.

- POST `/homeassistant/restart`
- POST `/homeassistant/check`
- POST `/homeassistant/start`
- POST `/homeassistant/stop`

- POST `/homeassistant/options`

```json
{
    "image": "Optional|null",
    "last_version": "Optional for custom image|null",
    "port": "port for access hass",
    "ssl": "bool",
    "password": "",
    "watchdog": "bool"
}
```

Image with `null` and last_version with `null` reset this options.

- POST/GET `/homeassistant/api`

Proxy to real home-assistant instance.

- GET `/homeassistant/websocket`

Proxy to real websocket instance.

- GET `/homeassistant/stats`
```json
{
    "cpu_percent": 0.0,
    "memory_usage": 283123,
    "memory_limit": 329392,
    "network_tx": 0,
    "network_rx": 0,
    "blk_read": 0,
    "blk_write": 0
}
```

### RESTful for API addons

- GET `/addons`

Get all available addons.

```json
{
    "addons": [
        {
            "name": "xy bla",
            "slug": "xy",
            "description": "description",
            "arch": ["armhf", "aarch64", "i386", "amd64"],
            "repository": "core|local|REP_ID",
            "version": "LAST_VERSION",
            "installed": "none|INSTALL_VERSION",
            "detached": "bool",
            "build": "bool",
            "url": "null|url",
            "icon": "bool",
            "logo": "bool"
        }
    ],
    "repositories": [
        {
            "slug": "12345678",
            "name": "Repitory Name|unknown",
            "source": "URL_OF_REPOSITORY",
            "url": "WEBSITE|REPOSITORY",
            "maintainer": "BLA BLU <fla@dld.ch>|unknown"
        }
    ]
}
```

- POST `/addons/reload`
- GET `/addons/{addon}/info`

```json
{
    "name": "xy bla",
    "description": "description",
    "long_description": "null|markdown",
    "auto_update": "bool",
    "url": "null|url of addon",
    "detached": "bool",
    "repository": "12345678|null",
    "version": "null|VERSION_INSTALLED",
    "last_version": "LAST_VERSION",
    "state": "none|started|stopped",
    "boot": "auto|manual",
    "build": "bool",
    "options": "{}",
    "network": "{}|null",
    "host_network": "bool",
    "host_ipc": "bool",
    "host_dbus": "bool",
    "privileged": ["NET_ADMIN", "SYS_ADMIN"],
    "devices": ["/dev/xy"],
    "auto_uart": "bool",
    "icon": "bool",
    "logo": "bool",
    "changelog": "bool",
    "hassio_api": "bool",
    "homeassistant_api": "bool",
    "stdin": "bool",
    "webui": "null|http(s)://[HOST]:port/xy/zx",
    "gpio": "bool",
    "audio": "bool",
    "audio_input": "null|0,0",
    "audio_output": "null|0,0"
}
```

- GET `/addons/{addon}/icon`

- GET `/addons/{addon}/logo`

- GET `/addons/{addon}/changelog`

- POST `/addons/{addon}/options`

```json
{
    "boot": "auto|manual",
    "auto_update": "bool",
    "network": {
      "CONTAINER": "port|[ip, port]"
    },
    "options": {},
    "audio_output": "null|0,0",
    "audio_input": "null|0,0"
}
```

Reset custom network/audio/options, set it `null`.

- POST `/addons/{addon}/start`

- POST `/addons/{addon}/stop`

- POST `/addons/{addon}/install`

- POST `/addons/{addon}/uninstall`

- POST `/addons/{addon}/update`

- GET `/addons/{addon}/logs`

Output is the raw Docker log.

- POST `/addons/{addon}/restart`

- POST `/addons/{addon}/rebuild`

Only supported for local build addons

- POST `/addons/{addon}/stdin`

Write data to add-on stdin

- GET `/addons/{addon}/stats`
```json
{
    "cpu_percent": 0.0,
    "memory_usage": 283123,
    "memory_limit": 329392,
    "network_tx": 0,
    "network_rx": 0,
    "blk_read": 0,
    "blk_write": 0
}
```

### Service discovery

- GET `/services/discovery`
```json
[
    {
        "provider": "name",
        "uuid": "uuid",
        "component": "component",
        "platform": "null|platform",
        "config": {}
    }
]
```

- GET `/services/discovery/{UUID}`
```json
{
    "provider": "name",
    "uuid": "uuid",
    "component": "component",
    "platform": "null|platform",
    "config": {}
}
```

- POST `/services/discovery`
```json
{
    "component": "component",
    "platform": "null|platform",
    "config": {}
}
```

return:
```json
{
    "uuid": "uuid"
}
```

- DEL `/services/discovery/{UUID}`

- GET `/services`
```json
{
    "services": {
        "{service_slug}": {
            "available": "bool",
            "provider": "null|name|list"
        }
    }
}
```

#### MQTT

This service perform a auto discovery to Home-Assistant.

- GET `/services/mqtt`
```json
{
    "provider": "name",
    "host": "xy",
    "port": "8883",
    "ssl": "bool",
    "username": "optional",
    "password": "optional",
    "protocol": "3.1.1"
}
```

- POST `/services/mqtt`
```json
{
    "host": "xy",
    "port": "8883",
    "ssl": "bool|optional",
    "username": "optional",
    "password": "optional",
    "protocol": "3.1.1"
}
```

- DEL `/services/mqtt`

## Host Control

Communicate over UNIX socket with a host daemon.

- commands

```
# info
-> {'type', 'version', 'last_version', 'features', 'hostname'}
# reboot
# shutdown
# host-update [v]

# hostname xy

# network info
-> {}
# network wlan ssd xy
# network wlan password xy
# network int ip xy
# network int netmask xy
# network int route xy
```

Features:

- shutdown
- reboot
- update
- hostname
- network_info
- network_control

Answer:
```
{}|OK|ERROR|WRONG
```

- {}: json
- OK: call was successfully
- ERROR: error on call
- WRONG: not supported
