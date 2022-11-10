#!/bin/bash
#SBATCH --time=2:00:00
#SBATCH --ntasks=1
#SBATCH --mem=32gb
#SBATCH --job-name=milkyway_fiducial
#SBATCH --mail-type=BEGIN,END,FAIL
#SBATCH --output=logs/run.out%j
#SBATCH --account=PAS2232


set -x

cd $SLURM_SUBMIT_DIR
module load miniconda3
source activate local

python simulate.py $TMPDIR/ "$@"

python json_outputs.py $TMPDIR/

cp -r -u $TMPDIR/*.json $SLURM_SUBMIT_DIR/output

scontrol show job=$SLURM_JOB_ID
