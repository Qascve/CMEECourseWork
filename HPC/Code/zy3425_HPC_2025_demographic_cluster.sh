#!/bin/bash
# Q4 submission script for demographic cluster runs

#PBS -N zy3425_demographic
#PBS -l select=1:ncpus=4:mem=16gb
#PBS -l walltime=01:00:00
#PBS -J 1-100
#PBS -o /rds/general/user/zy3425/home/HPC/Log/demographic
#PBS -e /rds/general/user/zy3425/home/HPC/Log/demographic

set -euo pipefail

# Support qsub from either ~/HPC or ~/HPC/Code
if [ -d "$PBS_O_WORKDIR/Code" ]; then
  cd "$PBS_O_WORKDIR/Code"
else
  cd "$PBS_O_WORKDIR"
fi

if command -v module >/dev/null 2>&1; then
  module load R || true
fi

echo "demographic cluster started"
echo "PBS_ARRAY_INDEX=${PBS_ARRAY_INDEX:-NA}"
echo "PWD=$(pwd)"
echo "HOSTNAME=$(hostname)"

Rscript zy3425_HPC_2025_demographic_cluster.R
status=$?

if [ "$status" -eq 0 ]; then
  echo "demographic run completed"
else
  echo "demographic run failed"
  exit "$status"
fi