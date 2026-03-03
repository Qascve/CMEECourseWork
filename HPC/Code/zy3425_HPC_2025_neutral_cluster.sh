#!/bin/bash
# Q25 submission script for neutral cluster runs

#PBS -N zy3425_neutral
#PBS -l select=1:ncpus=1:mem=1gb
#PBS -l walltime=12:00:00
#PBS -J 1-100
#PBS -o /rds/general/user/zy3425/home/HPC/Log/neutral
#PBS -e /rds/general/user/zy3425/home/HPC/Log/neutral

set -euo pipefail


if [ -d "$PBS_O_WORKDIR/Code" ]; then
  cd "$PBS_O_WORKDIR/Code"
else
  cd "$PBS_O_WORKDIR"
fi


if command -v module >/dev/null 2>&1; then
  module load R || true
fi

echo "neutral cluster started"
echo "PBS_ARRAY_INDEX=${PBS_ARRAY_INDEX:-NA}"
echo "PWD=$(pwd)"
echo "HOSTNAME=$(hostname)"

Rscript zy3425_HPC_2025_neutral_cluster.R

status=$?

if [ "$status" -eq 0 ]; then
  echo "neutral run completed"
else
  echo "neutral run failed"
  exit "$status"
fi