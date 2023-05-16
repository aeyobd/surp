#!/bin/bash

# written like this so we can substitute the 
# name into the file for easier understanding

# first argument is filename
# second argument is the python call
echo "Submitting Job"
rm -f logs/$1.log
export SLURM_SUBMIT_DIR=.
export TMPDIR=./temp

bash <<EOT
#!/bin/bash
#SBATCH --time=2:00:00
#SBATCH --ntasks=1
#SBATCH --mem=32gb
#SBATCH --job-name=$1
#SBATCH --mail-type=BEGIN,END,FAIL
#SBATCH --output=logs/$1
#SBATCH --account=PAS2232



cd $SLURM_SUBMIT_DIR
pwd

python --version


python -c "
$2
" \$TMPDIR/

python \$SLURM_SUBMIT_DIR/src/simulation/json_outputs.py \$TMPDIR/

# cp -r -u \$TMPDIR/*.vice \$SLURM_SUBMIT_DIR/out
# cp -r -u \$TMPDIR/*.json \$SLURM_SUBMIT_DIR/out
# cp -r -u \$TMPDIR/*.csv \$SLURM_SUBMIT_DIR/results

EOT
