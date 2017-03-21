FROM %%BASE_IMAGE%%

# Add version
ENV VERSION %%HASS_VERSION%%

# install core packages
RUN apk --no-cache add libuv git linux-headers eudev-dev libusb-dev

# install component packages
RUN apk --no-cache add ffmpeg nmap net-tools

##
# install zwave
WORKDIR /usr/src/
RUN pip3 install --no-cache-dir cython==0.25.2

WORKDIR /usr/src/python-openzwave/
RUN git clone https://github.com/OpenZWave/python-openzwave \
    && cd python-openzwave \
    && git checkout v0.3.2 \
    && make build \
    && make install \
    && mkdir -p /usr/local/share/python-openzwave \
    && cp -R openzwave/config /usr/local/share/python-openzwave/config \
    && rm -rf /usr/src/python-openzwave

##
# install pip module for components

# install home-assistant
RUN pip3 install --no-cache-dir uvloop homeassistant==%%HASS_VERSION%%

# Run hass
CMD [ "python", "-m", "homeassistant", "--config", "/config" ]
