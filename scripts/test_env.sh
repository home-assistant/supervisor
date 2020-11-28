#!/bin/bash
set -eE

DOCKER_TIMEOUT=30
DOCKER_PID=0


function start_docker() {
    local starttime
    local endtime

    echo "Starting docker."
    dockerd 2> /dev/null &
    DOCKER_PID=$!

    echo "Waiting for docker to initialize..."
    starttime="$(date +%s)"
    endtime="$(date +%s)"
    until docker info >/dev/null 2>&1; do
        if [ $((endtime - starttime)) -le $DOCKER_TIMEOUT ]; then
            sleep 1
            endtime=$(date +%s)
        else
            echo "Timeout while waiting for docker to come up"
            exit 1
        fi
    done
    echo "Docker was initialized"
}


function stop_docker() {
    local starttime
    local endtime

    echo "Stopping in container docker..."
    if [ "$DOCKER_PID" -gt 0 ] && kill -0 "$DOCKER_PID" 2> /dev/null; then
        starttime="$(date +%s)"
        endtime="$(date +%s)"

        # Now wait for it to die
        kill "$DOCKER_PID"
        while kill -0 "$DOCKER_PID" 2> /dev/null; do
            if [ $((endtime - starttime)) -le $DOCKER_TIMEOUT ]; then
                sleep 1
                endtime=$(date +%s)
            else
                echo "Timeout while waiting for container docker to die"
                exit 1
            fi
        done
    else
        echo "Your host might have been left with unreleased resources"
    fi
}


function build_supervisor() {
    docker pull homeassistant/amd64-builder:dev

    docker run --rm --privileged \
        -v /run/docker.sock:/run/docker.sock -v "$(pwd):/data" \
        homeassistant/amd64-builder:dev \
            --generic dev -t /data --test --amd64 --no-cache
}


function cleanup_lastboot() {
    if [[ -f /workspaces/test_supervisor/config.json ]]; then
        echo "Cleaning up last boot"
        cp /workspaces/test_supervisor/config.json /tmp/config.json
        jq -rM 'del(.last_boot)' /tmp/config.json > /workspaces/test_supervisor/config.json
        rm /tmp/config.json
    fi
}


function cleanup_docker() {
    echo "Cleaning up stopped containers..."
    docker rm $(docker ps -a -q) || true
}


function setup_test_env() {
    mkdir -p /workspaces/test_supervisor

    echo "Start Supervisor"
    docker run --rm --privileged \
        --name hassio_supervisor \
        --security-opt seccomp=unconfined \
        --security-opt apparmor:unconfined \
        -v /run/docker.sock:/run/docker.sock \
        -v /run/dbus:/run/dbus \
        -v "/workspaces/test_supervisor":/data \
        -v /etc/machine-id:/etc/machine-id:ro \
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

echo "Start Test-Env"

start_docker
trap "stop_docker" ERR

docker system prune -f

build_supervisor
cleanup_lastboot
cleanup_docker
init_dbus
setup_test_env
stop_docker
