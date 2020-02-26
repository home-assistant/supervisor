ARG BUILD_FROM
FROM $BUILD_FROM

# Install base
RUN apk add --no-cache \
    eudev \
    eudev-libs \
    git \
    glib \
    libffi \
    libpulse \
    musl \
    openssl \
    socat

ARG BUILD_ARCH
WORKDIR /usr/src

# Install requirements
COPY requirements.txt .
RUN export MAKEFLAGS="-j$(nproc)" \
    && pip3 install --no-cache-dir --no-index --only-binary=:all: \
        "https://wheels.home-assistant.io/alpine-$(cut -d '.' -f 1-2 < /etc/alpine-release)/${BUILD_ARCH}/" \
        -r ./requirements.txt \
    && rm -f requirements.txt

# Install Home Assistant Supervisor
COPY . supervisor
RUN pip3 install --no-cache-dir -e ./supervisor \
    && python3 -m compileall ./supervisor/supervisor


WORKDIR /
COPY rootfs /
