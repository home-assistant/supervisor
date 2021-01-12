#!/bin/bash
source "${BASH_SOURCE[0]%/*}/common.sh"
source "${BASH_SOURCE[0]%/*}/build-supervisor.sh"

set -eE

DOCKER_TIMEOUT=30
DOCKER_PID=0


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
        --security-opt apparmor:unconfined \
        -v /run/docker.sock:/run/docker.sock \
        -v /run/dbus:/run/dbus \
        -v "/workspaces/test_supervisor":/data \
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

echo "Run Supervisor"

start_docker
trap "stop_docker" ERR


if [ "$( docker container inspect -f '{{.State.Status}}' hassio_supervisor )" == "running" ]; then
    echo "Restarting Supervisor"
    docker rm -f hassio_supervisor
    init_dbus
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
    run_supervisor
    stop_docker
fi