#!/bin/bash
source "${BASH_SOURCE[0]%/*}/common.sh"

set -eE

DOCKER_TIMEOUT=30
DOCKER_PID=0

function build_supervisor() {
    docker pull homeassistant/amd64-builder:dev

    docker run --rm \
        --privileged \
        -v /run/docker.sock:/run/docker.sock \
        -v "$(pwd):/data" \
        homeassistant/amd64-builder:dev \
            --generic latest \
            --target /data \
            --test \
            --amd64 \
            --no-cache
}


function cleanup_docker() {
    echo "Cleaning up stopped containers..."
    docker rm $(docker ps -a -q) || true
}


function run_supervisor() {
    mkdir -p /workspaces/test_supervisor

    echo "Start Supervisor"
    docker run --rm --privileged \
        --name hassio_supervisor \
        --privileged \
        --security-opt seccomp=unconfined \
        --security-opt apparmor=unconfined \
        -v /run/docker.sock:/run/docker.sock:rw \
        -v /run/dbus:/run/dbus:ro \
        -v /run/udev:/run/udev:ro \
        -v "/workspaces/test_supervisor":/data:rw \
        -v /etc/machine-id:/etc/machine-id:ro \
        -v /workspaces/supervisor:/usr/src/supervisor \
        -e SUPERVISOR_SHARE="/workspaces/test_supervisor" \
        -e SUPERVISOR_NAME=hassio_supervisor \
        -e SUPERVISOR_DEV=1 \
        -e SUPERVISOR_MACHINE="qemux86-64" \
        homeassistant/amd64-hassio-supervisor:latest

}


function init_dbus() {
    if pgrep dbus-daemon; then
        echo "Dbus is running"
        return 0
    fi

    echo "Startup dbus"
    mkdir -p /var/lib/dbus
    cp -f /etc/machine-id /var/lib/dbus/machine-id

    # cleanups
    mkdir -p /run/dbus
    rm -f /run/dbus/pid

    # run
    dbus-daemon --system --print-address
}


function init_udev() {
    if pgrep systemd-udevd; then
        echo "udev is running"
        return 0
    fi

    echo "Startup udev"

    # cleanups
    mkdir -p /run/udev

    # run
    /lib/systemd/systemd-udevd --daemon
    sleep 3
    udevadm trigger && udevadm settle
}

function init_os-agent() {
    if pgrep os-agent; then
        echo "os-agent is running"
        return 0
    fi

    if [ ! -f /usr/sbin/os-agent ]; then
        curl -Lo /usr/sbin/os-agent https://github.com/home-assistant/os-agent/releases/latest/download/os-agent-debian-amd64.bin
        curl -Lo /etc/dbus-1/system.d/io.hass.conf https://raw.githubusercontent.com/home-assistant/os-agent/main/contrib/io.hass.conf
        chmod a+x /usr/sbin/os-agent
    fi

    /usr/sbin/os-agent &
}

echo "Run Supervisor"

start_docker
trap "stop_docker" ERR


if [ "$( docker container inspect -f '{{.State.Status}}' hassio_supervisor )" == "running" ]; then
    echo "Restarting Supervisor"
    docker rm -f hassio_supervisor
    init_dbus
    init_udev
    init_os-agent
    cleanup_lastboot
    run_supervisor
    stop_docker

else
    echo "Starting Supervisor"
    docker system prune -f
    build_supervisor
    cleanup_lastboot
    cleanup_docker
    init_dbus
    init_udev
    init_os-agent
    run_supervisor
    stop_docker
fi
