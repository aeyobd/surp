#!/bin/bash
#SBATCH --time=2:00:00
#SBATCH --ntasks=1
#SBATCH --mem=32gb
#SBATCH --job-name=milkyway_fiducial
#SBATCH --mail-type=BEGIN,END,FAIL
#SBATCH --output=surp/logs/run.out%j
#SBATCH --account=PAS2232


set -x

cd $SLURM_SUBMIT_DIR
module load miniconda3
source activate local

python gridrun.py $TMPDIR/ $1 $2 $3 $4

cp -r -u $TMPDIR/* $SLURM_SUBMIT_DIR/surp/output


scontrol show job=$SLURM_JOB_ID
