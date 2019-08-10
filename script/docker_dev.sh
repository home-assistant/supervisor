#!/bin/bash
set -e

function start_docker() {
    local starttime
    local endtime

    echo "Starting docker."
    dockerd &
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


function install_builder() {

    docker pull homeassistant/amd64-builder:latest
}

start_docker
install_builder
