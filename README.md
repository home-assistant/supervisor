# Hass.io

## First private cloud solution for home automation

Hass.io is a Docker-based system for managing your Home Assistant installation
and related applications. The system is controlled via Home Assistant which
communicates with the Supervisor. The Supervisor provides an API to manage the
installation. This includes changing network settings or installing
and updating software.

![](misc/hassio.png?raw=true)

## Installation

Installation instructions can be found at <https://home-assistant.io/hassio>.

## Development

The development of the supervisor is a bit tricky. Not difficult but tricky.

- You can use the builder to build your supervisor: https://github.com/home-assistant/hassio-build/tree/master/builder
- Go into a HassOS device or VM and pull your supervisor.
- Turn on the developer modus in the `updater.json` file (usually `/usr/share/hassio/updater.json`) by setting `channel` to `dev`
- Tag it as `homeassistant/{ARCH}-hassio-supervisor:latest` (you can get the full tag by running `docker images "*/*-supervisor"`)
- Restart the service like `systemctl restart hassos-supervisor | journalctl -fu hassos-supervisor`
- Test your changes

Small Bugfix or improvements, make a PR. Significant change makes first an RFC.
