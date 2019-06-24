FROM python:3.7

WORKDIR /workspace

# Install Python dependencies from requirements.txt if it exists
COPY requirements.txt requirements_tests.txt /workspace/
RUN pip install -r requirements.txt \
    && pip3 install -r requirements_tests.txt \
    && pip install black tox

# Set the default shell to bash instead of sh
ENV SHELL /bin/bash
