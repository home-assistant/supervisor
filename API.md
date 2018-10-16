# Hass.io

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

This API call don't need a token.

- GET `/supervisor/info`

The addons from `addons` are only installed one.

```json
{
    "version": "INSTALL_VERSION",
    "last_version": "LAST_VERSION",
    "arch": "armhf|aarch64|i386|amd64",
    "channel": "stable|beta|dev",
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
    "channel": "stable|beta|dev",
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
            "type": "full|partial",
            "protected": "bool"
        }
    ]
}
```

- POST `/snapshots/reload`

- POST `/snapshots/new/upload`

return:
```json
{
    "slug": ""
}
```

- POST `/snapshots/new/full`

```json
{
    "name": "Optional",
    "password": "Optional"
}
```

return:
```json
{
    "slug": ""
}
```

- POST `/snapshots/new/partial`

```json
{
    "name": "Optional",
    "addons": ["ADDON_SLUG"],
    "folders": ["FOLDER_NAME"],
    "password": "Optional"
}
```

return:
```json
{
    "slug": ""
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
    "protected": "bool",
    "homeassistant": "version",
    "addons": [
        {
            "slug": "ADDON_SLUG",
            "name": "NAME",
            "version": "INSTALLED_VERSION",
            "size": "SIZE_IN_MB"
        }
    ],
    "repositories": ["URL"],
    "folders": ["NAME"]
}
```

- POST `/snapshots/{slug}/remove`

- GET `/snapshots/{slug}/download`

- POST `/snapshots/{slug}/restore/full`

```json
{
    "password": "Optional"
}
```

- POST `/snapshots/{slug}/restore/partial`

```json
{
    "homeassistant": "bool",
    "addons": ["ADDON_SLUG"],
    "folders": ["FOLDER_NAME"],
    "password": "Optional"
}
```

### Host

- POST `/host/reload`

- POST `/host/shutdown`

- POST `/host/reboot`

- GET `/host/info`

```json
{
    "hostname": "hostname|null",
    "features": ["shutdown", "reboot", "hostname", "services", "hassos"],
    "operating_system": "HassOS XY|Ubuntu 16.4|null",
    "kernel": "4.15.7|null",
    "chassis": "specific|null",
    "deployment": "stable|beta|dev|null",
    "cpe": "xy|null",
}
```

- POST `/host/options`

```json
{
    "hostname": "",
}
```

- POST `/host/reload`

#### Services

- GET `/host/services`
```json
{
    "services": [
        {
            "name": "xy.service",
            "description": "XY ...",
            "state": "active|"
        }
    ]
}
```

- POST `/host/service/{unit}/stop`

- POST `/host/service/{unit}/start`

- POST `/host/service/{unit}/reload`

### HassOS

- GET `/hassos/info`
```json
{
    "version": "2.3",
    "version_cli": "7",
    "version_latest": "2.4",
    "version_cli_latest": "8",
    "board": "ova|rpi"
}
```

- POST `/hassos/update`
```json
{
    "version": "optional"
}
```

- POST `/hassos/update/cli`
```json
{
    "version": "optional"
}
```

- POST `/hassos/config/sync`

Load host configs from a USB stick.

### Hardware

- GET `/hardware/info`
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

- GET `/hardware/audio`
```json
{
    "audio": {
        "input": {
            "0,0": "Mic"
        },
        "output": {
            "1,0": "Jack",
            "1,1": "HDMI"
        }
    }
}
```

### Home Assistant

- GET `/homeassistant/info`

```json
{
    "version": "INSTALL_VERSION",
    "last_version": "LAST_VERSION",
    "machine": "Image machine type",
    "image": "str",
    "custom": "bool -> if custom image",
    "boot": "bool",
    "port": 8123,
    "ssl": "bool",
    "watchdog": "bool",
    "startup_time": 600
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
    "refresh_token": "",
    "watchdog": "bool",
    "startup_time": 600
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

If a add-on will call itself, you can use `/addons/self/...`.

- GET `/addons`

Get all available addons.

```json
{
    "addons": [
        {
            "name": "xy bla",
            "slug": "xy",
            "description": "description",
            "repository": "core|local|REP_ID",
            "version": "LAST_VERSION",
            "installed": "none|INSTALL_VERSION",
            "detached": "bool",
            "available": "bool",
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
    "slug": "xdssd_xybla",
    "description": "description",
    "long_description": "null|markdown",
    "auto_update": "bool",
    "url": "null|url of addon",
    "detached": "bool",
    "available": "bool",
    "arch": ["armhf", "aarch64", "i386", "amd64"],
    "machine": "[raspberrypi2, tinker]",
    "repository": "12345678|null",
    "version": "null|VERSION_INSTALLED",
    "last_version": "LAST_VERSION",
    "state": "none|started|stopped",
    "boot": "auto|manual",
    "build": "bool",
    "options": "{}",
    "network": "{}|null",
    "host_network": "bool",
    "host_pid": "bool",
    "host_ipc": "bool",
    "host_dbus": "bool",
    "privileged": ["NET_ADMIN", "SYS_ADMIN"],
    "apparmor": "disable|default|profile",
    "devices": ["/dev/xy"],
    "auto_uart": "bool",
    "icon": "bool",
    "logo": "bool",
    "changelog": "bool",
    "hassio_api": "bool",
    "hassio_role": "default|homeassistant|manager|admin",
    "homeassistant_api": "bool",
    "auth_api": "bool",
    "full_access": "bool",
    "protected": "bool",
    "rating": "1-6",
    "stdin": "bool",
    "webui": "null|http(s)://[HOST]:port/xy/zx",
    "gpio": "bool",
    "devicetree": "bool",
    "docker_api": "bool",
    "audio": "bool",
    "audio_input": "null|0,0",
    "audio_output": "null|0,0",
    "services_role": "['service:access']",
    "discovery": "['service']"
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

- POST `/addons/{addon}/security`

This function is not callable by itself.

```json
{
    "protected": "bool",
}
```

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

### discovery

- GET `/discovery`
```json
{
    "discovery": [
        {
            "addon": "slug",
            "service": "name",
            "uuid": "uuid",
            "config": {}
        }
    ]
}
```

- GET `/discovery/{UUID}`
```json
{
    "addon": "slug",
    "service": "name",
    "uuid": "uuid",
    "config": {}
}
```

- POST `/discovery`
```json
{
    "service": "name",
    "config": {}
}
```

return:
```json
{
    "uuid": "uuid"
}
```

- DEL `/discovery/{UUID}`

### Services

- GET `/services`
```json
{
    "services": [
        {
            "slug": "name",
            "available": "bool",
            "providers": "list"
        }
    ]
}
```

#### MQTT

- GET `/services/mqtt`
```json
{
    "addon": "name",
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

### Misc

- GET `/info`
```json
{
    "supervisor": "version",
    "homeassistant": "version",
    "hassos": "null|version",
    "hostname": "name",
    "machine": "type",
    "arch": "arch",
    "channel": "stable|beta|dev"
}
```

### Auth / SSO API

You can use the user system on homeassistant. We handle this auth system on
supervisor.

You can call post `/auth`

We support:
- Json `{ "user|name": "...", "password": "..." }`
- application/x-www-form-urlencoded `user|name=...&password=...`
- BasicAuth
