#!/bin/bash
#SBATCH --time=1:00:00
#SBATCH --ntasks=4
#SBATCH --mem=10gb
#SBATCH --job-name=milkyway_gce_sim_cristallo11_multithreaded
#SBATCH --mail-type=BEGIN,END,FAIL
#SBATCH --output=logs/run.out%j
#SBATCH --account=PAS2232


set -x


echo "Loading modules"
cd $SLURM_SUBMIT_DIR
module load miniconda3
source activate local

echo "Begining simulations"

export OMP_NUM_THREADS=4
python ../VICE/migration/simulations.py -f --dt=0.01 --name=$TMPDIR/cristallo11_multithreaded --nstars=2  --elements=fe_o_n_c --setup_nthreads=4 
echo "Completed simulation"
cp -r -u $TMPDIR/* $SLURM_SUBMIT_DIR/output

scontrol show job=$SLURM_JOB_ID
