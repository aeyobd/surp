#!/bin/bash
#SBATCH --time=4:00:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64gb
#SBATCH --job-name=milkyway_multithread
#SBATCH --mail-type=BEGIN,END,FAIL
#SBATCH --output=surp/logs/run.out%j
#SBATCH --account=PAS2232

set -x

cd $SLURM_SUBMIT_DIR
module load miniconda3
source activate local

export OMP_NUM_THREADS=8

python $1 $TMPDIR/

cp -r -u $TMPDIR/* $SLURM_SUBMIT_DIR/surp/output

scontrol show job=$SLURM_JOB_ID
