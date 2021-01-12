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

echo "Build Supervisor"
start_docker
trap "stop_docker" ERR

build_supervisor
