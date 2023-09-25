FROM ubuntu:focal as minimal-system

ARG DEBIAN_FRONTEND=noninteractive

# Env vars: locale
ENV LANG='en_US.UTF-8'
ENV LANGUAGE='en_US:en'
ENV LC_ALL='en_US.UTF-8'

# Use debconf to set locales to be generated when the locales apt package is installed later.
RUN echo "locales locales/default_environment_locale select en_US.UTF-8" | debconf-set-selections
RUN echo "locales locales/locales_to_be_generated multiselect en_US.UTF-8 UTF-8" | debconf-set-selections

# Install requirements that are absolutely necessary
RUN apt-get update && \
    apt-get -y dist-upgrade && \
    apt-get -y install --no-install-recommends \
        # Base Python system
        python3.8 \
        python3.8-venv \
        # Various required for building mysqlclient python package, used in some repos
        python3.8-dev \
        libmysqlclient21 \
        libmysqlclient-dev \
        pkg-config \
        libssl1.1 \
        libxmlsec1-openssl \
        # Assorted other useful things
        ntp \
        git \
        curl wget \
        # Generate locales
        locales

# Restore when done iterating on image
#
#RUN apt-get clean all && rm -rf /var/lib/apt/*

RUN useradd -m --shell /bin/false app

# /edx/dev/context will contain a directory for each repository we work
# with on the host, named by hash of path
RUN mkdir -p /edx/dev/context && chown -R app:app /edx/dev

USER app
