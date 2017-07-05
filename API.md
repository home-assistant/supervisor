# HassIO Server

## HassIO REST API

Interface for HomeAssistant to control things from supervisor.

On error:
```json
{
    "result": "error",
    "message": ""
}
```

On success
```json
{
    "result": "ok",
    "data": { }
}
```

### HassIO

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
            "arch": ["armhf", "aarch64", "i386", "amd64"],
            "repository": "12345678|null",
            "version": "LAST_VERSION",
            "installed": "INSTALL_VERSION",
            "detached": "bool",
            "build": "bool",
            "url": "null|url"
        }
    ],
    "addons_repositories": [
        "REPO_URL"
    ],
    "snapshots": [
        {
            "slug": "SLUG",
            "data": "ISO",
            "name": "Custom name"
        }
    ]
}
```

- GET `/supervisor/addons`

Get all available addons

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
            "url": "null|url"
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

Output the raw docker log

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
See HostControl info command.
```json
{
    "type": "",
    "version": "",
    "last_version": "",
    "features": ["shutdown", "reboot", "update", "network_info", "network_control"],
    "hostname": "",
    "os": ""
}
```

- POST `/host/update`
Optional:
```json
{
    "version": "VERSION"
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
    "mode": "dhcp|fixed",
    "ssid": "",
    "ip": "",
    "netmask": "",
    "gateway": ""
}
```

### HomeAssistant

- GET `/homeassistant/info`

```json
{
    "version": "INSTALL_VERSION",
    "last_version": "LAST_VERSION",
    "devices": []
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

Output the raw docker log

- POST `/homeassistant/restart`

- POST `/homeassistant/options`
```json
{
    "devices": [],
}
```

### REST API addons

- POST `/addons/reload`

- GET `/addons/{addon}/info`
```json
{
    "name": "xy bla",
    "description": "description",
    "url": "null|url of addon",
    "detached": "bool",
    "repository": "12345678|null",
    "version": "null|VERSION_INSTALLED",
    "last_version": "LAST_VERSION",
    "state": "none|started|stopped",
    "boot": "auto|manual",
    "build": "bool",
    "options": "{}",
}
```

- POST `/addons/{addon}/options`
```json
{
    "boot": "auto|manual",
    "options": {},
}
```

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

Output the raw docker log

- POST `/addons/{addon}/restart`

## Host Control

Communicate over unix socket with a host daemon.

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

features:
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
