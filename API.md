# Supervisor

## Supervisor RESTful API

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
  "data": {}
}
```

For access to API you need use a authorization header with a `Bearer` token.
They are available for Add-ons and the Home Assistant using the `SUPERVISOR_TOKEN` environment variable.

### Supervisor

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
  "logging": "debug|info|warning|error|critical",
  "ip_address": "ip address",
  "wait_boot": "int",
  "debug": "bool",
  "debug_block": "bool",
  "addons": [
    {
      "name": "xy bla",
      "slug": "xy",
      "description": "description",
      "repository": "12345678|null",
      "version": "LATEST_VERSION",
      "installed": "INSTALL_VERSION",
      "icon": "bool",
      "logo": "bool",
      "state": "started|stopped"
    }
  ],
  "addons_repositories": ["REPO_URL"]
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
  "debug": "bool",
  "debug_block": "bool",
  "logging": "debug|info|warning|error|critical",
  "addons_repositories": ["REPO_URL"]
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
  "memory_percent": 1.4,
  "network_tx": 0,
  "network_rx": 0,
  "blk_read": 0,
  "blk_write": 0
}
```

- GET `/supervisor/repair`

Repair overlayfs issue and restore lost images

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
  "cpe": "xy|null"
}
```

- POST `/host/options`

```json
{
  "hostname": ""
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

- GET `/os/info`

```json
{
  "version": "2.3",
  "version_cli": "7",
  "version_latest": "2.4",
  "version_cli_latest": "8",
  "board": "ova|rpi",
  "boot": "rauc boot slot"
}
```

- POST `/os/update`

```json
{
  "version": "optional"
}
```

- POST `/os/update/cli`

```json
{
  "version": "optional"
}
```

- POST `/os/config/sync`

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
            "devices": [
                "chan_id": "channel ID",
                "chan_type": "type of device"
            ]
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

- POST `/hardware/trigger`

Trigger an udev reload

### Home Assistant

- GET `/core/info`

```json
{
  "version": "INSTALL_VERSION",
  "last_version": "LAST_VERSION",
  "arch": "arch",
  "machine": "Image machine type",
  "ip_address": "ip address",
  "image": "str",
  "custom": "bool -> if custom image",
  "boot": "bool",
  "port": 8123,
  "ssl": "bool",
  "watchdog": "bool",
  "wait_boot": 600
}
```

- POST `/core/update`

Optional:

```json
{
  "version": "VERSION"
}
```

- GET `/core/logs`

Output is the raw Docker log.

- POST `/core/restart`
- POST `/core/check`
- POST `/core/start`
- POST `/core/stop`
- POST `/core/rebuild`

- POST `/core/options`

```json
{
  "image": "Optional|null",
  "last_version": "Optional for custom image|null",
  "port": "port for access core",
  "ssl": "bool",
  "refresh_token": "",
  "watchdog": "bool",
  "wait_boot": 600
}
```

Image with `null` and last_version with `null` reset this options.

- POST/GET `/core/api`

Proxy to the Home Assistant Core instance.

- GET `/core/websocket`

Proxy to Home Assistant Core websocket.

- GET `/core/stats`

```json
{
  "cpu_percent": 0.0,
  "memory_usage": 283123,
  "memory_limit": 329392,
  "memory_percent": 1.4,
  "network_tx": 0,
  "network_rx": 0,
  "blk_read": 0,
  "blk_write": 0
}
```

### RESTful for API add-ons

If an add-on will call itself, you can use `/addons/self/...`.

- GET `/addons`

Get all available add-ons.

```json
{
  "addons": [
    {
      "name": "xy bla",
      "slug": "xy",
      "description": "description",
      "advanced": "bool",
      "stage": "stable|experimental|deprecated",
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
  "hostname": "xdssd-xybla",
  "dns": [],
  "description": "description",
  "long_description": "null|markdown",
  "auto_update": "bool",
  "url": "null|url of addon",
  "detached": "bool",
  "available": "bool",
  "advanced": "bool",
  "stage": "stable|experimental|deprecated",
  "arch": ["armhf", "aarch64", "i386", "amd64"],
  "machine": "[raspberrypi2, tinker]",
  "homeassistant": "null|min Home Assistant Core version",
  "repository": "12345678|null",
  "version": "null|VERSION_INSTALLED",
  "last_version": "LAST_VERSION",
  "state": "none|started|stopped",
  "boot": "auto|manual",
  "build": "bool",
  "options": "{}",
  "schema": "{}|null",
  "network": "{}|null",
  "network_description": "{}|null",
  "host_network": "bool",
  "host_pid": "bool",
  "host_ipc": "bool",
  "host_dbus": "bool",
  "privileged": ["NET_ADMIN", "SYS_ADMIN"],
  "apparmor": "disable|default|profile",
  "devices": ["/dev/xy"],
  "udev": "bool",
  "auto_uart": "bool",
  "icon": "bool",
  "logo": "bool",
  "changelog": "bool",
  "documentation": "bool",
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
  "kernel_modules": "bool",
  "devicetree": "bool",
  "docker_api": "bool",
  "video": "bool",
  "audio": "bool",
  "audio_input": "null|0,0",
  "audio_output": "null|0,0",
  "services_role": "['service:access']",
  "discovery": "['service']",
  "ip_address": "ip address",
  "ingress": "bool",
  "ingress_entry": "null|/api/hassio_ingress/slug",
  "ingress_url": "null|/api/hassio_ingress/slug/entry.html",
  "ingress_port": "null|int",
  "ingress_panel": "null|bool"
}
```

- GET `/addons/{addon}/icon`

- GET `/addons/{addon}/logo`

- GET `/addons/{addon}/changelog`

- GET `/addons/{addon}/documentation`

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
  "audio_input": "null|0,0",
  "ingress_panel": "bool"
}
```

Reset custom network/audio/options, set it `null`.

- POST `/addons/{addon}/security`

This function is not callable by itself.

```json
{
  "protected": "bool"
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
  "memory_percent": 1.4,
  "network_tx": 0,
  "network_rx": 0,
  "blk_read": 0,
  "blk_write": 0
}
```

### ingress

- POST `/ingress/session`

Create a new Session for access to ingress service.

```json
{
  "session": "token"
}
```

- GET `/ingress/panels`

Return a list of enabled panels.

```json
{
  "panels": {
    "addon_slug": {
      "enable": "boolean",
      "icon": "mdi:...",
      "title": "title",
      "admin": "boolean"
    }
  }
}
```

- VIEW `/ingress/{token}`

Ingress WebUI for this Add-on. The addon need support HASS Auth!
Need ingress session as cookie.

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

#### MySQL

- GET `/services/mysql`

```json
{
  "addon": "name",
  "host": "xy",
  "port": "8883",
  "username": "optional",
  "password": "optional"
}
```

- POST `/services/mysql`

```json
{
  "host": "xy",
  "port": "8883",
  "username": "optional",
  "password": "optional"
}
```

- DEL `/services/mysql`

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
  "supported_arch": ["arch1", "arch2"],
  "channel": "stable|beta|dev",
  "logging": "debug|info|warning|error|critical",
  "timezone": "Europe/Zurich"
}
```

### DNS

- GET `/dns/info`

```json
{
  "host": "ip-address",
  "version": "1",
  "latest_version": "2",
  "servers": ["dns://8.8.8.8"],
  "locals": ["dns://xy"]
}
```

- POST `/dns/options`

```json
{
  "servers": ["dns://8.8.8.8"]
}
```

- POST `/dns/update`

```json
{
  "version": "VERSION"
}
```

- POST `/dns/restart`

- POST `/dns/reset`

- GET `/dns/logs`

- GET `/dns/stats`

```json
{
  "cpu_percent": 0.0,
  "memory_usage": 283123,
  "memory_limit": 329392,
  "memory_percent": 1.4,
  "network_tx": 0,
  "network_rx": 0,
  "blk_read": 0,
  "blk_write": 0
}
```

### Audio

- GET `/audio/info`

```json
{
  "host": "ip-address",
  "version": "1",
  "latest_version": "2",
  "audio": {
    "input": [
      {
        "name": "...",
        "description": "...",
        "volume": 0.3,
        "default": false
      }
    ],
    "output": [
      {
        "name": "...",
        "description": "...",
        "volume": 0.3,
        "default": false
      }
    ]
  }
}
```

- POST `/audio/update`

```json
{
  "version": "VERSION"
}
```

- POST `/audio/restart`

- POST `/audio/reload`

- GET `/audio/logs`

- POST `/audio/volume/input`

```json
{
  "name": "...",
  "volume": 0.5
}
```

- POST `/audio/volume/output`

```json
{
  "name": "...",
  "volume": 0.5
}
```

- POST `/audio/default/input`

```json
{
  "name": "..."
}
```

- POST `/audio/default/output`

```json
{
  "name": "..."
}
```

- GET `/audio/stats`

```json
{
  "cpu_percent": 0.0,
  "memory_usage": 283123,
  "memory_limit": 329392,
  "memory_percent": 1.4,
  "network_tx": 0,
  "network_rx": 0,
  "blk_read": 0,
  "blk_write": 0
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

* POST `/auth/reset`

```json
{
  "username": "xy",
  "password": "new-password"
}
```
