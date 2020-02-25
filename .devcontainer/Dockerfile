FROM python:3.7

WORKDIR /workspaces

# Install Node/Yarn for Frontent
RUN apt-get update && apt-get install -y --no-install-recommends \
        curl \
        git \
        apt-utils \
        apt-transport-https \
    && curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg | apt-key add - \
    && echo "deb https://dl.yarnpkg.com/debian/ stable main" | tee /etc/apt/sources.list.d/yarn.list \
    && apt-get update && apt-get install -y --no-install-recommends \
        nodejs \
        yarn \
    && curl -o - https://raw.githubusercontent.com/creationix/nvm/v0.34.0/install.sh | bash \
    && rm -rf /var/lib/apt/lists/*
ENV NVM_DIR /root/.nvm

# Install docker
# https://docs.docker.com/engine/installation/linux/docker-ce/ubuntu/
RUN apt-get update && apt-get install -y --no-install-recommends \
        apt-transport-https \
        ca-certificates \
        curl \
        software-properties-common \
        gpg-agent \
    && curl -fsSL https://download.docker.com/linux/debian/gpg | apt-key add - \
    && add-apt-repository "deb https://download.docker.com/linux/debian $(lsb_release -cs) stable" \
    && apt-get update && apt-get install -y --no-install-recommends \
        docker-ce \
        docker-ce-cli \
        containerd.io \
    && rm -rf /var/lib/apt/lists/*

# Install tools
RUN apt-get update && apt-get install -y --no-install-recommends \
        jq \
        dbus \
        network-manager \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies from requirements.txt if it exists
COPY requirements.txt requirements_tests.txt ./
RUN pip3 install -r requirements.txt -r requirements_tests.txt \
    && pip3 install tox \
    && rm -f requirements.txt requirements_tests.txt

# Set the default shell to bash instead of sh
ENV SHELL /bin/bash
