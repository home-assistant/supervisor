#!/bin/bash

set -e

BUILD_CONTAINER_NAME=hassio-build-$$
DOCKER_REPO=pvizeli

cleanup() {
    echo "[INFO] Cleanup."

    # Stop docker container
    echo "[INFO] Cleaning up yocto-build container."
    docker stop $BUILD_CONTAINER_NAME 2> /dev/null || true
    docker rm --volumes $BUILD_CONTAINER_NAME 2> /dev/null || true

    if [ "$1" == "fail" ]; then
        exit 1
    fi
}
trap 'cleanup fail' SIGINT SIGTERM

# Sanity checks
if [ "$#" -ne 2 ]; then
    echo "Usage: create_hassio_supervisor.sh <MACHINE> <TAG>|NONE"
    echo "Optional environment: BUILD_DIR"
    exit 1
fi
if [ $1 != 'armhf' ] && [ $1 != 'aarch64' ] && [ $1 != 'i386' ] && [ $1 != 'amd64' ]; then
    echo "Error: $1 is not a supported platform for hassio-supervisor!"
    exit 1
fi

# Get the absolute script location
pushd `dirname $0` > /dev/null 2>&1
SCRIPTPATH=`pwd`
popd > /dev/null 2>&1

ARCH=$1
BASE_IMAGE="resin\/${ARCH}-alpine:3.5"
DOCKER_TAG=$2
DOCKER_IMAGE=${ARCH}-hassio-supervisor
BUILD_DIR=${BUILD_DIR:=$SCRIPTPATH}
WORKSPACE=${BUILD_DIR:=$SCRIPTPATH}/hassio-supervisor

# setup docker
echo "[INFO] Setup docker for supervisor"
mkdir -p $BUILD_DIR
mkdir -p $WORKSPACE

sed "s/%%BASE_IMAGE%%/${BASE_IMAGE}/g" ../../supervisor/Dockerfile  > $WORKSPACE/Dockerfile

# Run build
echo "[INFO] start docker build"
docker stop $BUILD_CONTAINER_NAME 2> /dev/null || true
docker rm --volumes $BUILD_CONTAINER_NAME 2> /dev/null || true
docker run --rm \
    -v $WORKSPACE:/docker \
    -v ~/.docker:/root/.docker \
    -e DOCKER_REPO=$DOCKER_REPO \
    -e DOCKER_IMAGE=$DOCKER_IMAGE \
    -e DOCKER_TAG=$DOCKER_TAG \
    --name $BUILD_CONTAINER_NAME \
    --privileged \
    pvizeli/docker-build-env \
    /run-docker.sh

echo "[INFO] cleanup WORKSPACE"
rm -rf $WORKSPACE

cleanup
exit 0
