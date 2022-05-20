#!/bin/bash
#SBATCH --time=1:00:00
#SBATCH --ntasks=1
#SBATCH --mem=8gb
#SBATCH --job-name=milkyway_gce_sim
#SBATCH --mail-type=BEGIN,END,FAIL
#SBATCH --output=logs/run.out%j
#SBATCH --account=PAS2232

set -x

cd $SLURM_SUBMIT_DIR
module load miniconda3
source activate local
# rm -rf $SLURM_SUBMIT_DIR/output/*

python milkyway.py $TMPDIR cristallo11_test
cp -r -u $TMPDIR/* $SLURM_SUBMIT_DIR/output

# python milkyway.py $TMPDIR karakas10
# cp -r -u $TMPDIR/* $SLURM_SUBMIT_DIR/output

# python milkyway.py $TMPDIR ventura13
# cp -r -u $TMPDIR/* $SLURM_SUBMIT_DIR/output

# python milkyway.py $TMPDIR karakas16
# cp -r -u $TMPDIR/* $SLURM_SUBMIT_DIR/output

scontrol show job=$SLURM_JOB_ID
