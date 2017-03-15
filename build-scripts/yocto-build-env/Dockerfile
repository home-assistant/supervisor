FROM ubuntu:16.04

# Install the following utilities (required by poky)
RUN apt-get update && apt-get install -y \
    build-essential \
    chrpath \
    curl \
    diffstat \
    gcc-multilib \
    gawk \
    git-core \
    libsdl1.2-dev \
    texinfo \
    unzip \
    wget \
    xterm \
    cpio \
    file \
    python3 \
    && rm -rf /var/lib/apt/lists/*

# Set the locale to UTF-8 for bulding with poky morty
RUN locale-gen en_US.UTF-8
ENV LANG en_US.UTF-8

# Additional host packages required by resin
RUN apt-get update && apt-get install -y \
    apt-transport-https \
    && rm -rf /var/lib/apt/lists/*
RUN curl --silent https://deb.nodesource.com/gpgkey/nodesource.gpg.key | apt-key add -
ENV NODE_VERSION node_4.x
ENV DISTRO vivid
RUN echo "deb https://deb.nodesource.com/$NODE_VERSION $DISTRO main" | tee /etc/apt/sources.list.d/nodesource.list &&\
  echo "deb-src https://deb.nodesource.com/$NODE_VERSION $DISTRO main" | tee -a /etc/apt/sources.list.d/nodesource.list
RUN apt-get update && apt-get install -y \
    jq \
    nodejs \
    sudo \
    && rm -rf /var/lib/apt/lists/*

# Install docker
# https://docs.docker.com/engine/installation/linux/ubuntu/#install-using-the-repository
RUN apt-get update && apt-get install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    software-properties-common \
    && rm -rf /var/lib/apt/lists/*
VOLUME /var/lib/docker
RUN curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
RUN add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
RUN apt-get update && apt-get install -y \
    docker-ce \
    && rm -rf /var/lib/apt/lists/*

COPY run-resinos.sh /

WORKDIR /yocto/resin-board
