ARG BUILD_FROM
FROM $BUILD_FROM

# Install base
RUN apk add --no-cache \
    openssl \
    libffi \
    musl \
    git \
    socat \
    glib \
    eudev \
    eudev-libs

ARG BUILD_ARCH
WORKDIR /usr/src

# Install requirements
COPY requirements.txt .
RUN export MAKEFLAGS="-j$(nproc)" \
    && pip3 install --no-cache-dir --no-index --only-binary=:all: --find-links \
        "https://wheels.home-assistant.io/alpine-$(cut -d '.' -f 1-2 < /etc/alpine-release)/${BUILD_ARCH}/" \
        -r ./requirements.txt \
    && rm -f requirements.txt

# Install HassIO
COPY . hassio
RUN pip3 install --no-cache-dir -e ./hassio \
    && python3 -m compileall ./hassio/hassio


# Initialize udev daemon, handle CMD
COPY entry.sh /bin/
ENTRYPOINT ["/bin/entry.sh"]

WORKDIR /
CMD [ "python3", "-m", "supervisor" ]
