#!/bin/sh
# Run the MPI build of SWAN when started by mpirun with 2 or more processes,
# the serial build otherwise.
if [ "${OMPI_COMM_WORLD_SIZE:-1}" -gt 1 ]; then
    exec /usr/local/bin/swan-mpi "$@"
fi
exec /usr/local/bin/swan-serial "$@"
