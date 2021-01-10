# Home Assistant Supervisor

## First private cloud solution for home automation

Home Assistant (former Hass.io) is a container-based system for managing your
Home Assistant Core installation and related applications. The system is
controlled via Home Assistant which communicates with the Supervisor. The
Supervisor provides an API to manage the installation. This includes changing
network settings or installing and updating software.

## Installation

Installation instructions can be found at https://home-assistant.io/hassio.

## Development

The development of the Supervisor is not difficult but tricky.

- You can use the builder to create your Supervisor: https://github.com/home-assistant/hassio-builder
- Access a HassOS device or VM and pull your Supervisor.
- Set the developer modus with the CLI tool: `ha supervisor options --channel dev`
- Tag it as `homeassistant/xy-hassio-supervisor:latest`
- Restart the service with `systemctl restart hassos-supervisor | journalctl -fu hassos-supervisor`
- Test your changes

For small bugfixes or improvements, make a PR. For significant changes open a RFC first, please. Thanks.

## Release

Follow is the relase circle process:

1. Merge master into dev / make sure version stay on dev
2. Merge dev into master
3. Bump the release on master
4. Create a GitHub Release from master with the right version tag
