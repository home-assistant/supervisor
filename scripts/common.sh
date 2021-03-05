#!/bin/bash

function start_docker() {
    local starttime
    local endtime

    echo "Starting docker."
    dockerd 2> /dev/null &
    DOCKER_PID=$!

    #Fix for Debian WSL Docker uses legacy IP Tables. Check if we are running in Microsoft WSL and are root, and are on debian, and running in a docker container
    if [[ $(grep icrosoft.*WSL /proc/version) ]]  && [[ $(id) == *'uid=0'* ]]  && [ -e /etc/debian_version ]  && [[ $(grep docker /proc/1/cgroup 2>&1 > /dev/null) ]]; then
        update-alternatives --set iptables /usr/sbin/iptables-legacy
    fi
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

function cleanup_lastboot() {
    if [[ -f /workspaces/test_supervisor/config.json ]]; then
        echo "Cleaning up last boot"
        cp /workspaces/test_supervisor/config.json /tmp/config.json
        jq -rM 'del(.last_boot)' /tmp/config.json > /workspaces/test_supervisor/config.json
        rm /tmp/config.json
    fi
}
