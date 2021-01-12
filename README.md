# Home Assistant Supervisor

## First private cloud solution for home automation

Home Assistant (former Hass.io) is a container-based system for managing your
Home Assistant Core installation and related applications. The system is
controlled via Home Assistant which communicates with the Supervisor. The
Supervisor provides an API to manage the installation. This includes changing
network settings or installing and updating software.

## Installation

Installation instructions can be found at https://home-assistant.io/getting-started.

## Release

Releases are done in 3 stages (channels) with this structure:

1. Pull requests are merged to the `main` branch
2. A new build is pushed to the `dev` stage.
3. Releases are published
4. A new build is pushed to the `beta` stage.
5. The [`stable.json][stable] file is updated
6. The build that was pushed to `beta` will now be pushed to `stable`

[stable]: https://github.com/home-assistant/version/blob/master/stable.json
