#!/bin/bash

# module load miniconda3/4.12.0-py39

# written like this so we can substitute the 
# name into the file for easier understanding

# first argument is filename
# second argument is the python call
echo "Submitting Job"
rm -f logs/$1.log

sbatch <<EOT
#!/bin/bash
#SBATCH --time=16:00:00
#SBATCH --ntasks=$3
#SBATCH --mem=32gb
#SBATCH --job-name=$1
#SBATCH --mail-type=BEGIN,END,FAIL
#SBATCH --output=logs/$1
#SBATCH --account=PAS2232


set -x
export OMP_NUM_THREADS=1

cd $SLURM_SUBMIT_DIR
# # miniconda is specificed in bashrc
# module load miniconda3/4.12.0-py39
# # print out python version for recordkeeping
python --version


export OMP_NUM_THREADS=$3
python -c "
$2
" \$TMPDIR/

export OMP_NUM_THREADS=1
python \$SLURM_SUBMIT_DIR/surp/simulation/json_outputs.py \$TMPDIR/

cp -r -u \$TMPDIR/*.vice \$SLURM_SUBMIT_DIR/out
cp -r -u \$TMPDIR/*.json \$SLURM_SUBMIT_DIR/out
# cp \$TMPDIR/*.vice/*.txt \$SLURM_SUBMIT_DIR/out
# cp -r -u \$TMPDIR/*.csv \$SLURM_SUBMIT_DIR/results

scontrol show job=\$SLURM_JOB_ID

EOT
