# Hass.io Server

## Hass.io RESTful API

Interface for Home Assistant to control things from supervisor.

On error:

```json
{
    "result": "error",
    "message": ""
}
```

On success:

```json
{
    "result": "ok",
    "data": { }
}
```

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
    "addons": [
        {
            "name": "xy bla",
            "slug": "xy",
            "description": "description",
            "repository": "12345678|null",
            "version": "LAST_VERSION",
            "installed": "INSTALL_VERSION",
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
    "addons_repositories": [
        "REPO_URL"
    ]
}
```

- POST `/supervisor/reload`

Reload addons/version.

- GET `/supervisor/logs`

Output is the raw docker log.

### Security

- GET `/security/info`

```json
{
    "initialize": "bool",
    "totp": "bool"
}
```

- POST `/security/options`

```json
{
    "password": "xy"
}
```

- POST `/security/totp`

```json
{
    "password": "xy"
}
```

Return QR-Code

- POST `/security/session`
```json
{
    "password": "xy",
    "totp": "null|123456"
}
```

### Backup/Snapshot

- GET `/snapshots`

```json
{
    "snapshots": [
        {
            "slug": "SLUG",
            "date": "ISO",
            "name": "Custom name"
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
    "homeassistant": {
      "version": "INSTALLED_HASS_VERSION",
      "devices": []
    },
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
    "devices": [""],
    "image": "str",
    "custom": "bool -> if custom image",
    "boot": "bool",
    "port": 8123,
    "password": null,
    "ssl": "bool"
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
    "devices": [],
    "image": "Optional|null",
    "last_version": "Optional for custom image|null",
    "port": "port for access hass",
    "ssl": "bool"
}
```

Image with `null` and last_version with `null` reset this options.

- POST/GET `/homeassistant/api`

Proxy to real home-assistant instance.

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
            "privileged": ["NET_ADMIN", "SYS_ADMIN"],
            "devices": ["/dev/xy"],
            "url": "null|url",
            "logo": "bool",
            "audio": "bool",
            "gpio": "bool",
            "hassio_api": "bool"
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
    "privileged": ["NET_ADMIN", "SYS_ADMIN"],
    "devices": ["/dev/xy"],
    "logo": "bool",
    "hassio_api": "bool",
    "webui": "null|http(s)://[HOST]:port/xy/zx",
    "gpio": "bool",
    "audio": "bool",
    "audio_input": "null|0,0",
    "audio_output": "null|0,0"
}
```

- GET `/addons/{addon}/logo`

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

For reset custom network/audio settings, set it `null`.

- POST `/addons/{addon}/start`

- POST `/addons/{addon}/stop`

- POST `/addons/{addon}/install`

Optional:

```json
{
    "version": "VERSION"
}
```

- POST `/addons/{addon}/uninstall`

- POST `/addons/{addon}/update`

Optional:

```json
{
    "version": "VERSION"
}
```

- GET `/addons/{addon}/logs`

Output is the raw Docker log.

- POST `/addons/{addon}/restart`

- POST `/addons/{addon}/rebuild`

Only supported for local build addons

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
