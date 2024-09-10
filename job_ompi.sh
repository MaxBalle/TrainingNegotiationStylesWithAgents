#!/bin/bash
module load devel/python/3.12.3_gnu_13.3
module load mpi/openmpi/5.0
module list
mpirun --bind-to core --map-by core -report-bindings python main.py
