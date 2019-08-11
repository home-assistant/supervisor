#!/bin/bash
set -e

DOCKER_TIMEOUT=30


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


function build_supervisor() {
    docker pull homeassistant/amd64-builder:latest

    docker run --rm --privileged \
        -v /run/docker.sock:/run/docker.sock -v "$(pwd):/data" \
        homeassistant/amd64-builder:latest \
            --supervisor 3.7-alpine3.10 --version dev \
            -t /data --test --amd64 \
            --no-cache --docker-hub homeassistant
}


function setup_test_env() {
    mkdir -p test_data

    docker run --rm --privileged \
        --name hassio_supervisor \
        --security-opt seccomp=unconfined \
        --security-opt apparmor:unconfined \
        -v /run/docker.sock:/run/docker.sock \
        -v /run/dbus:/run/dbus \
        -v "$(pwd)/test_data":/data \
        -e SUPERVISOR_SHARE="$(pwd)/test_data" \
        -e SUPERVISOR_NAME=hassio_supervisor \
        -e HOMEASSISTANT_REPOSITORY="homeassistant/qemux86-64" \
        homeassistant/amd64-hassio-supervisor:latest
}


start_docker
build_supervisor
setup_test_env
