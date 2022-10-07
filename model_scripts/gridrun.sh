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

python pickle_outputs.py $TMPDIR/

cp -r -u $TMPDIR/*.pickle $SLURM_SUBMIT_DIR/surp/pickles


scontrol show job=$SLURM_JOB_ID
