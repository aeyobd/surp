#!/bin/bash
#SBATCH --time=2:00:00
#SBATCH --ntasks=1
#SBATCH --mem=32gb
#SBATCH --job-name=milkyway_fiducial
#SBATCH --mail-type=BEGIN,END,FAIL
#SBATCH --output=../logs/run.out%j
#SBATCH --account=PAS2232


set -x

cd $SLURM_SUBMIT_DIR
module load miniconda3
source activate local

python cmlrun.py $TMPDIR/ "$@"

# python pickle_outputs.py $TMPDIR/

cp -r -u $TMPDIR/*.vice $SLURM_SUBMIT_DIR/../output
cp -r -u $TMPDIR/*.out $SLURM_SUBMIT_DIR/../output


scontrol show job=$SLURM_JOB_ID
