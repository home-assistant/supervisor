#!/bin/bash

set -e

BUILD_CONTAINER_NAME=homeassistant-build-$$
DOCKER_REPO=pvizeli

cleanup() {
    echo "[INFO] Cleanup."

    # Stop docker container
    echo "[INFO] Cleaning up homeassistant-build container."
    docker stop $BUILD_CONTAINER_NAME 2> /dev/null || true
    docker rm --volumes $BUILD_CONTAINER_NAME 2> /dev/null || true

    if [ "$1" == "fail" ]; then
        exit 1
    fi
}
trap 'cleanup fail' SIGINT SIGTERM

# Sanity checks
if [ "$#" -ne 2 ]; then
    echo "Usage: create_homeassistant.sh <HASS_VERS> <MACHINE>"
    echo "Optional environment: BUILD_DIR"
    exit 1
fi

# Get the absolute script location
pushd `dirname $0` > /dev/null 2>&1
SCRIPTPATH=`pwd`
popd > /dev/null 2>&1

HASS_VERS=$1
MACHINE=$2
BASE_IMAGE="resin\/${MACHINE}-alpine-python:3.6"
DOCKER_TAG=$1
DOCKER_IMAGE=${MACHINE}-homeassistant
BUILD_DIR=${BUILD_DIR:=$SCRIPTPATH}
WORKSPACE=${BUILD_DIR:=$SCRIPTPATH}/hass

# setup docker
echo "[INFO] Setup docker for homeassistant"
mkdir -p $BUILD_DIR
mkdir -p $WORKSPACE

echo "[INFO] load homeassistant"
cp ../../homeassistant/Dockerfile $WORKSPACE/Dockerfile

sed -i "s/%%BASE_IMAGE%%/${BASE_IMAGE}/g" $WORKSPACE/Dockerfile
sed -i "s/%%HASS_VERSION%%/${HASS_VERS}/g" $WORKSPACE/Dockerfile

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
cd $BUILD_DIR
rm -rf $WORKSPACE

cleanup
exit 0
