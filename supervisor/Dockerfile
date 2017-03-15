FROM %%BASE_IMAGE%%

# remove several traces of python
RUN apk del --no-cache python*

# http://bugs.python.org/issue19846
# > At the moment, setting "LANG=C" on a Linux system *fundamentally breaks Python 3*, and that's not OK.
ENV LANG C.UTF-8

# setup base
RUN apk add --no-cache python3

# install aiohttp
RUN pip3 install pip --no-cache --upgrade && pip3 install --no-cache aiohttp
