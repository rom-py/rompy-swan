# SWAN runtime image for rompy-swan.
#
# Builds a SWAN release from its source tarball with NetCDF output, in two builds: a
# serial one and an MPI one. The `swan.exe` command is a wrapper that runs the MPI
# binary when launched by mpirun with 2 or more processes and the serial binary
# otherwise, so the same command works in both cases:
#
#   docker run --rm -v "$PWD":/data ghcr.io/rom-py/swan swan.exe
#   docker run --rm -v "$PWD":/data ghcr.io/rom-py/swan mpirun -n 4 swan.exe
#
# Build a release (see releases.txt for the versions and checksums):
#   docker build -t swan:41.51 \
#     --build-arg SWAN_VERSION=41.51 --build-arg SWAN_SHA256=<sha256> docker
#
# No ENTRYPOINT is set so the image works with rompy's DockerConfig backend, which
# runs `bash -c "<command>"` inside the container.

ARG BASE_IMAGE=ubuntu:24.04

FROM ${BASE_IMAGE} AS builder

ARG SWAN_VERSION=41.51
ARG SWAN_SHA256=325c229f3dde0b812db4ec9ae6fa1cd4086d2109562c389576590ce8f94b26bb
ARG SWAN_URL=https://swanmodel.sourceforge.io/download/zip

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
        ca-certificates \
        curl \
        gfortran \
        libnetcdf-dev \
        libnetcdff-dev \
        libopenmpi-dev \
        make \
        openmpi-bin \
        perl \
    && rm -rf /var/lib/apt/lists/*

# Release tarballs are named without the dot, e.g. swan4151.tar.gz for 41.51
RUN version="$(echo "${SWAN_VERSION}" | tr -d .)" \
    && curl -fsSL -o /tmp/swan.tar.gz "${SWAN_URL}/swan${version}.tar.gz" \
    && echo "${SWAN_SHA256}  /tmp/swan.tar.gz" | sha256sum -c - \
    && mkdir /opt/swan && tar xzf /tmp/swan.tar.gz -C /opt/swan --strip-components=1
WORKDIR /opt/swan

# FOR (ocpmix.ftn) declares its filename argument with a fixed length of 140 and
# rewrites path separators over that whole length, but SWAN passes it a shorter
# temporary when opening NetCDF output files. The writes past the end of the string
# corrupt the heap and SWAN intermittently crashes. Declaring the argument with
# assumed length limits the rewriting to the string that is passed. The replacement
# keeps the line length, since the source is fixed-form.
RUN sed -i 's|CHARACTER DDNAME\*(LENFNM), SF\*2|CHARACTER DDNAME*(*), SF*2     |' ocpmix.ftn \
    && grep -q 'CHARACTER DDNAME\*(\*), SF\*2' ocpmix.ftn

# `make config` writes macros.inc for the compiler. Setting NETCDFROOT enables NetCDF
# output (BLOCK and SPECOUT files ending in .nc); the lines it guards redefine
# variables in terms of themselves, which GNU make rejects, so they become appends.
# SWAN's Makefile builds swan.exe in place, so the two builds run one after the other.
RUN make config \
    && sed -i -e 's|^NETCDFROOT =$|NETCDFROOT = /usr|' \
        -e 's|^\(  *\)\([A-Za-z_]*\) = \$(\2)|\1\2 +=|' macros.inc \
    && make ser && mv swan.exe swan-serial && make clobber \
    && make mpi && mv swan.exe swan-mpi

# Record the packages that provide the shared libraries the binaries link to, so the
# runtime stage installs the right ones whatever the base image
RUN ldd swan-serial swan-mpi \
        | awk '/=> \// {print $3}' | xargs -r readlink -f | sort -u \
        | xargs -r dpkg -S 2>/dev/null | cut -d: -f1 | sort -u \
        > runtime-packages.txt

FROM ${BASE_IMAGE}

ARG SWAN_VERSION=41.51

LABEL org.opencontainers.image.title="swan" \
      org.opencontainers.image.description="SWAN ${SWAN_VERSION} with NetCDF and MPI, for use with rompy-swan" \
      org.opencontainers.image.source="https://github.com/rom-py/rompy-swan" \
      org.opencontainers.image.version="${SWAN_VERSION}" \
      org.opencontainers.image.licenses="GPL-3.0-or-later"

ENV DEBIAN_FRONTEND=noninteractive
COPY --from=builder /opt/swan/runtime-packages.txt /tmp/runtime-packages.txt
RUN apt-get update \
    && xargs -a /tmp/runtime-packages.txt apt-get install -y --no-install-recommends \
        openmpi-bin \
        openssh-client \
    && rm -rf /var/lib/apt/lists/* /tmp/runtime-packages.txt

COPY --from=builder /opt/swan/swan-serial /usr/local/bin/swan-serial
COPY --from=builder /opt/swan/swan-mpi /usr/local/bin/swan-mpi
COPY swan.sh /usr/local/bin/swan.exe

# Containers usually run as root, which Open MPI refuses by default
ENV OMPI_ALLOW_RUN_AS_ROOT=1 \
    OMPI_ALLOW_RUN_AS_ROOT_CONFIRM=1 \
    SWAN_VERSION=${SWAN_VERSION}

WORKDIR /data
CMD ["swan.exe"]
