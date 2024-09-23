#!/bin/bash

#SBATCH --mail-type=ALL
#SBATCH --mail-user=balle-max@web.de

module load devel/python/3.12.3_intel_2023.1.0
module load mpi/openmpi/5.0

mpirun --bind-to core --map-by core -report-bindings python refine.py
