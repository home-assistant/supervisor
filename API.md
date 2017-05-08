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
    "beta_channel": "true|false",
    "addons": [
        {
            "name": "xy bla",
            "slug": "xy",
            "repository": "12345678|null",
            "version": "LAST_VERSION",
            "installed": "INSTALL_VERSION",
            "detached": "bool",
            "description": "description"
        }
    ],
    "addons_repositories": [
        "REPO_URL"
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
            "repository": "core|local|REP_ID",
            "version": "LAST_VERSION",
            "installed": "none|INSTALL_VERSION",
            "detached": "bool",
            "description": "description"
        }
    ],
    "repositories": [
        {
            "slug": "12345678",
            "name": "Repitory Name",
            "source": "URL_OF_REPOSITORY",
            "url": "null|WEBSITE",
            "maintainer": "null|BLA BLU <fla@dld.ch>"
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
    "addons_repositories": [
        "REPO_URL"
    ]
}
```

- POST `/supervisor/reload`

Reload addons/version.

- GET `/supervisor/logs`

Output the raw docker log

### Host

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
    "last_version": "LAST_VERSION"
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

### REST API addons

- GET `/addons/{addon}/info`
```json
{
    "name": "xy bla",
    "description": "description",
    "url": "null|url of addon",
    "detached": "bool",
    "repository": "12345678|null",
    "version": "VERSION",
    "last_version": "LAST_VERSION",
    "state": "started|stopped",
    "boot": "auto|manual",
    "options": {},
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

## Host Control

Communicate over unix socket with a host daemon.

- commands
```
# info
-> {'type', 'version', 'last_version', 'features', 'hostname'}
# reboot
# shutdown
# host-update [v]

# network info
# network hostname xy
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
