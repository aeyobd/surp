#!/bin/bash

# first argument is filename base
# second is number of threads

echo "Submitting Job"
rm -f logs/$1.log
NTHREADS=$(jq -r ".n_threads" "params/$1.json" )
echo using $NTHREADS

sbatch <<EOT
#!/bin/bash
#SBATCH --time=12:00:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=$NTHREADS
#SBATCH --mem=32gb
#SBATCH --job-name=$1
#SBATCH --mail-type=BEGIN,END,FAIL
#SBATCH --output=logs/$1
#SBATCH --account=$SLURM_ACCOUNT


set -xe
export OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK:w


python run.py \$TMPDIR ./params/$1.json

cp -ru \$TMPDIR/$1.vice ./out
cp \$TMPDIR/$1*.dat ./out

if [[ -z "$SURP_COPY_VICE" ]]; then;
else
    cp \$TMPDIR/C11_f0.2*.dat ./out
    cp -r \$TMPDIR/$1.vice ./out
fi

python json_outputs.py \$TMPDIR/$1.vice
python result.py \$TMPDIR/$1.json

cp \$TMPDIR/$1*.txt out
cp -r -u \$TMPDIR/$1.json out
cp \$TMPDIR/$1.csv out


scontrol show job=\$SLURM_JOB_ID

EOT
