#!/bin/bash
#SBATCH --time=7:00:00
#SBATCH --ntasks=1
#SBATCH --mem=64gb
#SBATCH --job-name=milkyway_fiducial
#SBATCH --mail-type=BEGIN,END,FAIL
#SBATCH --output=logs/run.out%j
#SBATCH --account=PAS2232

# run this from the surp directory

set -x

cd $SLURM_SUBMIT_DIR
module load miniconda3
source activate local
# rm -rf $SLURM_SUBMIT_DIR/output/*

# export OMP_NUM_THREADS=8

# python milkyway.py $TMPDIR/
# python model_scripts/fiducial.py $TMPDIR/
python $1 $TMPDIR/



# export OMP_NUM_THREADS=1
cp -r -u $TMPDIR/* $SLURM_SUBMIT_DIR/output

# python milkyway.py $TMPDIR karakas10
# cp -r -u $TMPDIR/* $SLURM_SUBMIT_DIR/output

# python milkyway.py $TMPDIR ventura13
# cp -r -u $TMPDIR/* $SLURM_SUBMIT_DIR/output

# python milkyway.py $TMPDIR karakas16
# cp -r -u $TMPDIR/* $SLURM_SUBMIT_DIR/output

scontrol show job=$SLURM_JOB_ID
