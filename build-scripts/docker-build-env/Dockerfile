FROM ubuntu:16.04

RUN locale-gen en_US.UTF-8
ENV LANG en_US.UTF-8

# Install docker
# https://docs.docker.com/engine/installation/linux/ubuntu/#install-using-the-repository
RUN apt-get update && apt-get install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    software-properties-common \
    && rm -rf /var/lib/apt/lists/*
VOLUME /var/lib/docker
RUN curl -fsSL https://download.docker.com/linux/ubuntu/gpg | apt-key add -
RUN add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
RUN apt-get update && apt-get install -y \
    docker-ce \
    && rm -rf /var/lib/apt/lists/*

# setup arm binary support
RUN apt-get update && apt-get install -y \
    qemu-user-static \
    binfmt-support \
    && rm -rf /var/lib/apt/lists/*

COPY run-docker.sh /

WORKDIR /docker
