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

- `/supervisor/ping`

- `/supervisor/info`

```json
{
    "version": "INSTALL_VERSION",
    "last_version": "LAST_VERSION",
    "beta_channel": "true|false",
    "addons": [
        {
            "name": "xy bla",
            "slug": "xy",
            "version": "LAST_VERSION",
            "installed": "none|INSTALL_VERSION",
            "dedicated": "bool",
            "description": "description"
        }
    ]
}
```

- `/supervisor/update`
Optional:
```json
{
    "version": "VERSION"
}
```

- `/supervisor/option`
```json
{
    "beta_channel": "true|false"
}
```

- `/supervisor/reload`

Reload addons/version.

- `/supervisor/logs`

Output the raw docker log

### Host

- `/host/shutdown`

- `/host/reboot`

- `/host/info`
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

- `/host/update`
Optional:
```json
{
    "version": "VERSION"
}
```

### Network

- `/network/info`

- `/network/options`
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

- `/homeassistant/info`

```json
{
    "version": "INSTALL_VERSION",
    "last_version": "LAST_VERSION"
}
```

- `/homeassistant/update`
Optional:
```json
{
    "version": "VERSION"
}
```

- `/homeassistant/logs`

Output the raw docker log

### REST API addons

- `/addons/{addon}/info`
```json
{
    "version": "VERSION",
    "last_version": "LAST_VERSION",
    "state": "started|stopped",
    "boot": "auto|manual",
    "options": {},
}
```

- `/addons/{addon}/options`
```json
{
    "boot": "auto|manual",
    "options": {},
}
```

- `/addons/{addon}/start`

- `/addons/{addon}/stop`

- `/addons/{addon}/install`
Optional:
```json
{
    "version": "VERSION"
}
```

- `/addons/{addon}/uninstall`

- `/addons/{addon}/update`
Optional:
```json
{
    "version": "VERSION"
}
```

- `/addons/{addon}/logs`

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
